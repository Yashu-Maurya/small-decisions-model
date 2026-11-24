import heapq, json, os
from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = PACKAGE_DIR.parent.parent
DATA_PATH = str(PROJECT_ROOT / "data" / "decision-custom-1" / "dataset")
VOCAB_SIZE = 4096


def load_file(path) -> list:
    with open(f"{path}", "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


vocab = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!? \n\t1234567890'':,.;-$_()\"|%°"


def get_stats(ids: list):
    counts = {}
    for pair in zip(ids, ids[1:]):
        counts[pair] = counts.get(pair, 0) + 1
    return counts


def merge(ids, pair, idx):
    new_ids = []
    i = 0
    while i < len(ids):
        if i < len(ids) - 1 and pair[0] == ids[i] and pair[1] == ids[i + 1]:
            new_ids.append(idx)
            i += 2
        else:
            new_ids.append(ids[i])
            i += 1
    return new_ids


def train_tokenizer(inp: str):
    tokens = list(map(int, inp.encode("utf-8")))
    num_merges = VOCAB_SIZE - 256
    ids = list(tokens)

    merges = {}
    for i in range(num_merges):
        stats = get_stats(ids)
        if not stats:
            break
        pair = max(stats, key=stats.get)
        idx = 256 + i
        ids = merge(ids, pair, idx)
        merges[pair] = idx
    return ids, merges


def encode(inp: str, merges: dict) -> list[int]:
    """Encode a UTF-8 string into BPE token IDs using a min-heap over merge ranks."""
    ids = list(inp.encode("utf-8"))
    n = len(ids)
    if n < 2:
        return ids

    nxt = list(range(1, n + 1))
    nxt[-1] = -1
    prv = list(range(-1, n - 1))
    alive = [True] * n
    merges_get = merges.get

    heap: list[tuple[int, int]] = []
    for i in range(n - 1):
        rank = merges_get((ids[i], ids[i + 1]))
        if rank is not None:
            heapq.heappush(heap, (rank, i))

    while heap:
        rank, i = heapq.heappop(heap)
        if not alive[i]:
            continue
        j = nxt[i]
        if j == -1 or not alive[j]:
            continue
        if merges_get((ids[i], ids[j])) != rank:
            continue

        ids[i] = rank
        alive[j] = False
        nj = nxt[j]
        nxt[i] = nj
        if nj != -1:
            prv[nj] = i

        pi = prv[i]
        if pi != -1:
            nr = merges_get((ids[pi], rank))
            if nr is not None:
                heapq.heappush(heap, (nr, pi))
        if nj != -1:
            nr = merges_get((rank, ids[nj]))
            if nr is not None:
                heapq.heappush(heap, (nr, i))

    out: list[int] = []
    cur = 0
    while cur != -1:
        if alive[cur]:
            out.append(ids[cur])
        cur = nxt[cur]
    return out


def decode(ids: list, merges: dict):
    vocab_bytes = {idx: bytes([idx]) for idx in range(256)}
    for (p0, p1), idx in merges.items():
        vocab_bytes[idx] = vocab_bytes[p0] + vocab_bytes[p1]
    tokens = b"".join(vocab_bytes[idx] for idx in ids)
    return tokens.decode("utf-8", errors="replace")


def save_merges(merges: dict, path: str | Path = PACKAGE_DIR / "merges.json"):
    with open(path, "w", encoding="utf-8") as f:
        json.dump({f"{p0},{p1}": idx for (p0, p1), idx in merges.items()}, f)


def load_merges(path: str | Path = PACKAGE_DIR / "merges.json") -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return {tuple(map(int, k.split(","))): v for k, v in json.load(f).items()}


def build_vocab(merges: dict) -> dict:
    vocab = {idx: bytes([idx]) for idx in range(256)}
    for (p0, p1), idx in merges.items():
        vocab[idx] = vocab[p0] + vocab[p1]
    return vocab


def save_vocab(vocab: dict, path: str | Path = PACKAGE_DIR / "vocab.json"):
    with open(path, "w", encoding="utf-8") as f:
        json.dump({str(idx): list(token_bytes) for idx, token_bytes in vocab.items()}, f)


def load_vocab(path: str | Path = PACKAGE_DIR / "vocab.json") -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return {int(idx): bytes(token_bytes) for idx, token_bytes in json.load(f).items()}


if __name__ == "__main__":
    dataset_files = sorted(
        [file for file in os.listdir(path=DATA_PATH) if file.endswith(".jsonl")],
        key=lambda f: f.lower(),
    )
    records = load_file(f"{DATA_PATH}/{dataset_files[0]}")

    corpus = " \n".join(record["input"] for record in records)
    corpus = " \n".join(choice for record in records for choice in record["choices"])

    new_vocab, merges = train_tokenizer(corpus)
    vocab = build_vocab(merges=merges)
    for record in records:
        inp, choices, out = record["input"], record["choices"], record["out"]
        encoded = encode(inp, merges)
        decoded = decode(encoded, merges)
        print(len(encoded), encoded, "\n")
        print(len(decoded), decoded, "\n\n")

    print(len(new_vocab), new_vocab, merges)
    save_merges(merges=merges, path=PACKAGE_DIR / "merges.json")
    save_vocab(vocab=vocab, path=PACKAGE_DIR / "vocab.json")
