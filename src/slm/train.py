import os, time, json
from pathlib import Path
from torch import nn, tensor, long
import torch
from torch.nn import functional as F
from slm.tokenizer import encode, load_merges, load_file, DATA_PATH

merges = load_merges(str(Path(__file__).with_name("merges.json")))
VOCAB_SIZE = 256 + len(merges)
DEVICE = "mps"

def encode_record(record: dict):
    inp, choices, out = record["input"], record["choices"], record["out"]
    return {
        "input": encode(inp, merges=merges),
        "choices": [encode(choice, merges) for choice in choices],
        "out": out
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
            nn.Linear(dim*2, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32,1)
        )
        self.null_score = nn.Linear(dim, 1)
        
    def vector(self, ids: list[int]):
        tokens = tensor(ids[:128], dtype=long, device=DEVICE)
        return self.embedding(tokens).mean(dim=0)
    
    def forward(self, record: dict):
        inp, choices, out = record["input"], record["choices"], record["out"]
        
        scores=[]
        inp = self.vector(inp)
        for id in choices:
            choice_vector = self.vector(id)
            pair = torch.cat([inp, choice_vector])
            scores.append(self.choice_score(pair).squeeze())
        scores.append(self.null_score(inp).squeeze())
        return torch.stack(scores)
        

if __name__ == "__main__":
    dataset_files = sorted([file for file in os.listdir(path=DATA_PATH) if file.startswith("decisions-") and file.endswith(".jsonl")], key=lambda f: f.lower())
    records = load_file(f"{DATA_PATH}/{dataset_files[0]}")
    model = SmolDecision(VOCAB_SIZE, 64).to(DEVICE)
    optimizer = torch.optim.AdamW(model.parameters(), lr=0.001)
    with open(f"{DATA_PATH}/manifest.json", encoding="utf-8") as f:
        total_records = json.load(f)["records"]

    processed = 0
    total_loss = 0.0
    started = time.monotonic()
    model.train()
    print(dataset_files[1:2])
    for filename in dataset_files[1:2]:
        records = load_file(f"{DATA_PATH}/{filename}")

        for record in records:
            example = encode_record(record)
            target = update_none_val(example["out"])

            optimizer.zero_grad()
            logits = model(example)
            loss = -(target * F.log_softmax(logits, dim=0)).sum()
            loss.backward()
            optimizer.step()

            processed += 1
            total_loss += loss.item()

            if processed % 1000 == 0 or processed == total_records:
                elapsed = time.monotonic() - started
                rate = processed / max(elapsed, 0.001)
                remaining = (total_records - processed) / max(rate, 0.001)

                print(
                    f"\r{processed:,}/{total_records:,} "
                    f"({processed / total_records:.1%}) | "
                    f"avg loss {total_loss / processed:.4f} | "
                    f"{rate:.1f} records/s | "
                    f"ETA {remaining / 60:.1f} min",
                    end="",
                    flush=True,
                )

    print()
    checkpoint_dir = Path(__file__).resolve().parents[2] / "checkpoints"
    os.makedirs(checkpoint_dir, exist_ok=True)
    torch.save(model.state_dict(), checkpoint_dir / "smol_decision_epoch1.pt")
    print("Checkpoint saved.")
