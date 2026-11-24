"""Record validation shared by generator, validator and tests."""
from __future__ import annotations

import re
from typing import Any

MAX_INPUT_CHARS = 700
MAX_CHOICE_CHARS = 100
MIN_CHOICES, MAX_CHOICES = 2, 10
CONF_TOL = 1e-6
_WS = re.compile(r"\s+")


def norm_text(s: str) -> str:
    return _WS.sub(" ", s.strip().lower())


def validate_record(r: dict[str, Any]) -> list[str]:
    errs: list[str] = []
    if set(r) != {"input", "choices", "out"}:
        errs.append(f"keys={sorted(r)}")
        return errs
    inp = r["input"]
    choices = r["choices"]
    out = r["out"]
    if not isinstance(inp, str) or not inp.strip():
        errs.append("input must be a non-empty string")
    else:
        if len(inp) > MAX_INPUT_CHARS:
            errs.append("input too long")
        lines = inp.split("\n")
        if not (1 <= len(lines) <= 3):
            errs.append(f"line_count={len(lines)}")
        if any(not ln.strip() for ln in lines):
            errs.append("blank line")
        if inp != inp.strip():
            errs.append("input has outer whitespace")
        if "\t" in inp or "\r" in inp:
            errs.append("bad control character")
    if not isinstance(choices, list) or not (MIN_CHOICES <= len(choices) <= MAX_CHOICES):
        errs.append(f"choices must be a list of {MIN_CHOICES}-{MAX_CHOICES} items")
        return errs
    seen: set[str] = set()
    for c in choices:
        if not isinstance(c, str) or not c.strip():
            errs.append("empty choice")
            continue
        if len(c) > MAX_CHOICE_CHARS:
            errs.append("choice too long")
        k = norm_text(c)
        if k in seen:
            errs.append("duplicate choice")
        seen.add(k)
    if not isinstance(out, list) or len(out) != len(choices):
        errs.append("out must be a list with one score per choice")
        return errs
    if all(x == -1 for x in out):
        return errs  # decline: every listed option is rejected
    if any(x == -1 for x in out):
        errs.append("out mixes -1 with confidence scores")
        return errs
    for x in out:
        if isinstance(x, bool) or not isinstance(x, (int, float)) or not (0 <= x <= 1):
            errs.append("confidence scores must be numbers in [0, 1]")
            return errs
    if abs(sum(out) - 1.0) > CONF_TOL:
        errs.append(f"confidence scores sum to {sum(out)}, not 1")
    return errs


def validate_soft(r: dict[str, Any]) -> list[str]:
    """Extra quality checks that are warnings, not hard failures."""
    warn: list[str] = []
    inp = r["input"].lower()
    for c in r["choices"]:
        if c.lower().strip() == inp.strip():
            warn.append("choice equals input")
    return warn
