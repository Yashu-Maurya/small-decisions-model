import json
import os
import time
from concurrent.futures import ProcessPoolExecutor, wait, FIRST_COMPLETED
from pathlib import Path

import torch
from torch import long, nn, tensor
from torch.nn import functional as F

from slm.batching import init_worker, prepare_file_batches
from slm.tokenizer import DATA_PATH, encode, load_merges

PACKAGE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = PACKAGE_DIR.parent.parent
MERGES_PATH = PACKAGE_DIR / "merges.json"
CHECKPOINT_PATH = PROJECT_ROOT / "checkpoints" / "smol_decision_epoch1.pt"

merges = load_merges(MERGES_PATH)
VOCAB_SIZE = 256 + len(merges)
DEVICE = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"

BATCH_SIZE = 256
MAX_TOKENS = 128
LEARNING_RATE = 0.003


def encode_record(record: dict):
    inp, choices, out = record["input"], record["choices"], record["out"]
    return {
        "input": encode(inp, merges=merges),
        "choices": [encode(choice, merges) for choice in choices],
        "out": out,
    }


def update_none_val(out):
    if all(value == -1 for value in out):
        values = [0.0] * len(out) + [1.0]
    else:
        values = out + [0.0]

    return torch.tensor(values, dtype=torch.float32, device=DEVICE)


class SmolDecision(nn.Module):
    def __init__(self, vocab_size: int, dim: int):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, dim)
        self.choice_score = nn.Sequential(
            nn.Linear(dim * 2, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
        )
        self.null_score = nn.Linear(dim, 1)

    def vector(self, ids: list[int]):
        tokens = tensor(ids[:MAX_TOKENS], dtype=long, device=DEVICE)
        return self.embedding(tokens).mean(dim=0)

    def forward(self, record: dict):
        inp, choices, _out = record["input"], record["choices"], record["out"]

        scores = []
        inp_vec = self.vector(inp)
        for choice_ids in choices:
            choice_vector = self.vector(choice_ids)
            pair = torch.cat([inp_vec, choice_vector])
            scores.append(self.choice_score(pair).squeeze())
        scores.append(self.null_score(inp_vec).squeeze())
        return torch.stack(scores)

    def forward_batch(
        self,
        flat_tokens: torch.Tensor,
        offsets: torch.Tensor,
        batch_size: int,
        max_choices: int,
    ) -> torch.Tensor:
        bags = F.embedding_bag(flat_tokens, self.embedding.weight, offsets, mode="mean")
        inp_vecs = bags[:batch_size]
        ch_vecs = bags[batch_size:].view(batch_size, max_choices, -1)
        pairs = torch.cat([inp_vecs.unsqueeze(1).expand(-1, max_choices, -1), ch_vecs], dim=-1)
        ch_logits = self.choice_score(pairs).squeeze(-1)
        null_logits = self.null_score(inp_vecs)
        return torch.cat([ch_logits, null_logits], dim=1)


def _batch_to_tensors(batch_tuple):
    flat_tokens_np, offsets_np, mask_np, targets_np, bs, max_c = batch_tuple
    flat_tokens = torch.from_numpy(flat_tokens_np).to(DEVICE, non_blocking=True)
    offsets = torch.from_numpy(offsets_np).to(DEVICE, non_blocking=True)
    mask = torch.from_numpy(mask_np).to(DEVICE, non_blocking=True)
    targets = torch.from_numpy(targets_np).to(DEVICE, non_blocking=True)
    return flat_tokens, offsets, mask, targets, bs, max_c


def _masked_loss(logits: torch.Tensor, mask: torch.Tensor, targets: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
    masked_logits = logits.masked_fill(~mask, float("-inf"))
    log_probs = F.log_softmax(masked_logits, dim=1)
    log_probs = torch.where(mask, log_probs, torch.zeros_like(log_probs))
    loss = -(targets * log_probs).sum() / logits.shape[0]
    return loss, masked_logits


@torch.inference_mode()
def evaluate_batches(model: SmolDecision, batches: list) -> tuple[float, float, int]:
    model.eval()
    total_loss = 0.0
    total_correct = 0
    total_count = 0
    for batch_tuple in batches:
        flat_tokens, offsets, mask, targets, bs, max_c = _batch_to_tensors(batch_tuple)
        logits = model.forward_batch(flat_tokens, offsets, bs, max_c)
        loss, masked_logits = _masked_loss(logits, mask, targets)
        total_loss += loss.item() * bs
        total_correct += (masked_logits.argmax(dim=1) == targets.argmax(dim=1)).sum().item()
        total_count += bs
    model.train()
    if total_count == 0:
        return 0.0, 0.0, 0
    return total_loss / total_count, total_correct / total_count, total_count


def main() -> None:
    dataset_files = sorted(
        [
            file
            for file in os.listdir(path=DATA_PATH)
            if file.startswith("decisions-") and file.endswith(".jsonl")
        ],
        key=lambda f: f.lower(),
    )
    with open(f"{DATA_PATH}/manifest.json", encoding="utf-8") as f:
        manifest = json.load(f)
    total_corpus_records = manifest.get("records") or manifest["totals"]["records"]
    expected_train_records = max(1, total_corpus_records - 40_000)

    model = SmolDecision(VOCAB_SIZE, 64).to(DEVICE)
    optimizer = torch.optim.AdamW(model.parameters(), lr=LEARNING_RATE)

    num_workers = min(8, max(1, (os.cpu_count() or 2) // 2))
    max_in_flight = num_workers * 2

    processed_train = 0
    total_loss = 0.0
    val_batches: list = []
    test_batches: list = []
    started = time.monotonic()
    last_report = 0

    model.train()
    print(f"Training on {len(dataset_files)} files | device={DEVICE} | batch_size={BATCH_SIZE} | workers={num_workers}")

    with ProcessPoolExecutor(
        max_workers=num_workers,
        initializer=init_worker,
        initargs=(str(MERGES_PATH),),
    ) as executor:
        file_iter = iter(dataset_files)
        in_flight = set()

        for _ in range(min(max_in_flight, len(dataset_files))):
            fname = next(file_iter, None)
            if fname is not None:
                in_flight.add(executor.submit(prepare_file_batches, (DATA_PATH, fname, BATCH_SIZE, MAX_TOKENS)))

        while in_flight:
            done, in_flight = wait(in_flight, return_when=FIRST_COMPLETED)
            for fut in done:
                next_fname = next(file_iter, None)
                if next_fname is not None:
                    in_flight.add(executor.submit(prepare_file_batches, (DATA_PATH, next_fname, BATCH_SIZE, MAX_TOKENS)))

                split_batches = fut.result()
                if "val" in split_batches:
                    val_batches.extend(split_batches["val"])
                if "test" in split_batches:
                    test_batches.extend(split_batches["test"])

                for batch_tuple in split_batches.get("train", ()):
                    flat_tokens, offsets, mask, targets, bs, max_c = _batch_to_tensors(batch_tuple)
                    optimizer.zero_grad(set_to_none=True)
                    logits = model.forward_batch(flat_tokens, offsets, bs, max_c)
                    loss, _ = _masked_loss(logits, mask, targets)
                    loss.backward()
                    optimizer.step()

                    processed_train += bs
                    total_loss += loss.item() * bs

                    if processed_train - last_report >= 20_000:
                        last_report = processed_train
                        elapsed = time.monotonic() - started
                        rate = processed_train / max(elapsed, 0.001)
                        remaining = max(0, expected_train_records - processed_train) / max(rate, 0.001)
                        print(
                            f"\r{processed_train:,}/{expected_train_records:,} "
                            f"({min(1.0, processed_train / expected_train_records):.1%}) | "
                            f"avg loss {total_loss / processed_train:.4f} | "
                            f"{rate:.1f} records/s | "
                            f"ETA {remaining:.1f}s",
                            end="",
                            flush=True,
                        )

    elapsed = time.monotonic() - started
    print(
        f"\r{processed_train:,}/{processed_train:,} (100.0%) | "
        f"avg loss {total_loss / max(1, processed_train):.4f} | "
        f"{processed_train / max(elapsed, 0.001):.1f} records/s | "
        f"elapsed {elapsed:.1f}s          "
    )

    val_loss, val_acc, val_n = evaluate_batches(model, val_batches)
    test_loss, test_acc, test_n = evaluate_batches(model, test_batches)
    print(f"Val  ({val_n:,} records): loss={val_loss:.4f}, acc={val_acc:.2%}")
    print(f"Test ({test_n:,} records): loss={test_loss:.4f}, acc={test_acc:.2%}")

    CHECKPOINT_PATH.parent.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), CHECKPOINT_PATH)
    print(f"Checkpoint saved to {CHECKPOINT_PATH}")


if __name__ == "__main__":
    main()
