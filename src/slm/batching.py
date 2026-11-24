"""Fast tokenization and batch packing for decision-custom-1 without importing torch."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from slm.tokenizer import encode, load_merges

_WORKER_MERGES: dict | None = None
_WORKER_CACHE: dict[str, list[int]] = {}


def init_worker(merges_path: str) -> None:
    """Initialize per-worker BPE merges and local string encoding cache."""
    global _WORKER_MERGES, _WORKER_CACHE
    _WORKER_MERGES = load_merges(merges_path)
    _WORKER_CACHE = {}


def _encode_cached(
    text: str,
    merges: dict,
    cache: dict[str, list[int]],
    max_tokens: int,
) -> list[int]:
    ids = cache.get(text)
    if ids is not None:
        return ids
    ids = encode(text, merges)[:max_tokens]
    if not ids:
        ids = [0]
    if len(text) <= 80 and len(cache) < 100_000:
        cache[text] = ids
    return ids


def pack_batches(
    encoded_records: list[tuple[list[int], list[list[int]], list[float]]],
    batch_size: int,
) -> list[tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, int, int]]:
    """Pack encoded records into zero-copy numpy arrays for EmbeddingBag training/eval."""
    batches = []
    for start in range(0, len(encoded_records), batch_size):
        batch = encoded_records[start : start + batch_size]
        bs = len(batch)
        max_c = max(len(item[1]) for item in batch)

        flat_tokens: list[int] = []
        offsets: list[int] = []
        for inp_ids, _, _ in batch:
            offsets.append(len(flat_tokens))
            flat_tokens.extend(inp_ids)

        mask = np.zeros((bs, max_c + 1), dtype=np.bool_)
        targets = np.zeros((bs, max_c + 1), dtype=np.float32)

        for i, (_, ch_ids, out) in enumerate(batch):
            nc = len(ch_ids)
            mask[i, :nc] = True
            mask[i, max_c] = True
            if all(v == -1 for v in out):
                targets[i, max_c] = 1.0
            else:
                targets[i, :nc] = out
            for j in range(max_c):
                offsets.append(len(flat_tokens))
                if j < nc:
                    flat_tokens.extend(ch_ids[j])
                else:
                    flat_tokens.append(0)

        batches.append((
            np.asarray(flat_tokens, dtype=np.int64),
            np.asarray(offsets, dtype=np.int64),
            mask,
            targets,
            bs,
            max_c,
        ))
    return batches


def prepare_file_batches(
    task: tuple[str, str, int, int],
) -> dict[str, list[tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, int, int]]]:
    """Load, tokenize, and pack a single JSONL shard split by audit metadata."""
    data_path, filename, batch_size, max_tokens = task
    assert _WORKER_MERGES is not None
    merges = _WORKER_MERGES
    cache = _WORKER_CACHE

    data_dir = Path(data_path)
    rec_path = data_dir / filename
    meta_path = data_dir / "audit" / filename.replace(".jsonl", ".meta.jsonl")

    splits: dict[str, list[tuple[list[int], list[list[int]], list[float]]]] = {
        "train": [],
        "val": [],
        "test": [],
    }
    with rec_path.open("r", encoding="utf-8") as rf, meta_path.open("r", encoding="utf-8") as mf:
        for rline, mline in zip(rf, mf):
            if not rline.strip():
                continue
            rec = json.loads(rline)
            meta = json.loads(mline)
            split = meta.get("split", "train")
            inp_ids = _encode_cached(rec["input"], merges, cache, max_tokens)
            ch_ids = [_encode_cached(c, merges, cache, max_tokens) for c in rec["choices"]]
            splits.setdefault(split, []).append((inp_ids, ch_ids, rec["out"]))

    return {split: pack_batches(items, batch_size) for split, items in splits.items() if items}
