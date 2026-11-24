"""Exact quota helpers."""
from __future__ import annotations

from math import floor


def largest_remainder(total: int, weights: dict[str, int]) -> dict[str, int]:
    """Allocate `total` exactly according to integer weights."""
    s = sum(weights.values())
    if s <= 0:
        raise ValueError("weights must sum to a positive number")
    raw = {k: total * v / s for k, v in weights.items()}
    out = {k: floor(v) for k, v in raw.items()}
    left = total - sum(out.values())
    order = sorted(raw, key=lambda k: (raw[k] - out[k], k), reverse=True)
    for k in order[:left]:
        out[k] += 1
    return out


def split_counts(total: int, keys: list[str]) -> dict[str, int]:
    """Even split with remainder assigned deterministically."""
    base, rem = divmod(total, len(keys))
    return {k: base + (1 if i < rem else 0) for i, k in enumerate(keys)}
