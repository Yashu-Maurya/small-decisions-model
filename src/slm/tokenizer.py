import json, os
from itertools import groupby

DATA_PATH = "/Users/yashumaurya/Documents/slm/data/decision-custom-1/dataset"
VOCAB_SIZE=4096

def load_file(path)->list:
    records=[]
    with open(f"{path}", "r", encoding="utf-8") as f:
        records = [json.loads(line) for line in f if line.strip()]
    return records

vocab="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!? \n\t1234567890\'':,.;-$_()\"|%°"

def get_stats(ids:list):
    counts = {}
    for pair in zip(ids, ids[1:]):
        counts[pair] = counts.get(pair, 0) + 1
    return counts

def merge(ids, pair, idx):
    new_ids=[]
    i = 0
    while i < len(ids):
        if i < len(ids)-1 and pair[0] == ids[i] and pair[1] == ids[i+1]:
            new_ids.append(idx)
            i+=2
        else:
            new_ids.append(ids[i])
            i+=1
    return new_ids

def train_tokenizer(inp:str):
    tokens = list(map(int, inp.encode('utf-8')))
    num_merges = VOCAB_SIZE - 256
    ids = list(tokens)
    
    merges = {}
    for i in range(num_merges):
        stats = get_stats(ids)
        if not stats:
            break
        pair = max(stats, key=stats.get)
        idx = 256+i
        ids = merge(ids, pair, idx)
        merges[pair] = idx
    return ids, merges

def encode(inp:str, merges:dict):
    ids = list(map(int, inp.encode('utf-8')))
    while len(ids) >= 2:
        stats = get_stats(ids)
        pair = min(stats, key=lambda p: merges.get(p, float("inf")))
        if pair not in merges:
            break
        idx = merges[pair]
        ids = merge(ids, pair, idx)
    return ids

def decode(ids:list, merges:dict):
    vocab_bytes = {idx: bytes([idx]) for idx in range(256)}
    for (p0, p1), idx in merges.items():
        vocab_bytes[idx] = vocab_bytes[p0] + vocab_bytes[p1]
    tokens = b"".join(vocab_bytes[idx] for idx in ids)
    return tokens.decode("utf-8", errors="replace")

def save_merges(merges: dict, path: str = "merges.json"):
    with open(path, "w", encoding="utf-8") as f:
        json.dump({f"{p0},{p1}": idx for (p0, p1), idx in merges.items()}, f)

def load_merges(path: str = "merges.json") -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return {tuple(map(int, k.split(","))): v for k, v in json.load(f).items()}
    
def build_vocab(merges: dict) -> dict:
    vocab = {idx: bytes([idx]) for idx in range(256)}
    for (p0, p1), idx in merges.items():
        vocab[idx] = vocab[p0] + vocab[p1]
    return vocab

def save_vocab(vocab: dict, path: str = "vocab.json"):
    with open(path, "w", encoding="utf-8") as f:
        json.dump({str(idx): list(token_bytes) for idx, token_bytes in vocab.items()}, f)

def load_vocab(path: str = "vocab.json") -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return {int(idx): bytes(token_bytes) for idx, token_bytes in json.load(f).items()}

if __name__ == "__main__": 
    dataset_files = sorted([file for file in os.listdir(path=DATA_PATH) if file.endswith(".jsonl")], key=lambda f: f.lower())
    records = load_file(f"{DATA_PATH}/{dataset_files[0]}")
    
    corpus = " \n".join(record["input"] for record in records)
    corpus = " \n".join(choice for record in records for choice in record["choices"] )

    new_vocab, merges = train_tokenizer(corpus)
    vocab = build_vocab(merges=merges)
    for record in records: 
        inp, choices, out = record["input"], record["choices"], record["out"]
        encoded = encode(inp, merges)
        decoded = decode(encoded, merges)
        print(len(encoded), encoded, "\n")
        print(len(decoded), decoded, "\n\n")
        
        
    print(len(new_vocab), new_vocab, merges)
    save_merges(merges=merges, path="merges.json")
    save_vocab(vocab=vocab, path="vocab.json")
    