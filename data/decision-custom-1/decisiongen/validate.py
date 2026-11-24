"""Dataset validator for decision-custom-1."""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from . import config
from .schema import norm_text, validate_record
from .seeds_apps import APP_PATTERNS
from .seeds_tools import SPECIAL_TOOLS, TOOLS
from .seeds_tools_extra import SPECIAL_PATTERNS

SLICES = ("general_valid", "general_decline", "tool_valid", "tool_decline")


def _sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    out = []
    with path.open("r", encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, 1):
            if not line.endswith("\n"):
                raise ValueError(f"{path.name}:{lineno}: missing trailing newline")
            try:
                obj = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path.name}:{lineno}: {exc}") from exc
            if not isinstance(obj, dict):
                raise ValueError(f"{path.name}:{lineno}: record is not an object")
            out.append(obj)
    return out


def validate(data: Path, deep: bool = False, write: bool = True) -> dict[str, Any]:
    data = Path(data)
    errors: list[str] = []
    warnings: list[str] = []
    checks: dict[str, Any] = {}

    manifest_path = data / "manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(manifest_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    files = manifest.get("files", [])
    expected_files = config.TOTAL // config.BATCH_SIZE
    if len(files) != expected_files:
        errors.append(f"manifest lists {len(files)} files, expected {expected_files}")

    all_records: list[dict[str, Any]] = []
    all_meta: list[dict[str, Any]] = []
    slice_counts = Counter()
    line_counts = Counter()
    choice_counts = Counter()
    plus_counts: dict[int, Counter] = {n: Counter() for n in config.CHOICE_COUNTS}
    tool_behaviors = Counter()
    tool_declines = Counter()
    general_declines = Counter()
    per_file_ok = True

    for entry in files:
        name = entry["path"]
        path = data / name
        audit_path = data / "audit" / name.replace(".jsonl", ".meta.jsonl")
        if not path.exists() or not audit_path.exists():
            errors.append(f"{name}: missing data or audit file")
            per_file_ok = False
            continue
        try:
            records = _read_jsonl(path)
            metas = _read_jsonl(audit_path)
        except ValueError as exc:
            errors.append(str(exc))
            per_file_ok = False
            continue
        if len(records) != config.BATCH_SIZE:
            errors.append(f"{name}: {len(records)} records, expected {config.BATCH_SIZE}")
            per_file_ok = False
        if len(metas) != len(records):
            errors.append(f"{name}: audit has {len(metas)} rows, data has {len(records)}")
            per_file_ok = False
        digest = _sha(path)
        if digest != entry.get("sha256"):
            errors.append(f"{name}: sha256 mismatch")
        if len(path.read_bytes()) != entry.get("bytes"):
            errors.append(f"{name}: byte size mismatch")
        local = Counter()
        for i, (rec, meta) in enumerate(zip(records, metas)):
            errs = validate_record(rec)
            if errs:
                errors.append(f"{name}:{i + 1}: {errs}")
                continue
            key = ("tool" if meta.get("kind") == "tool" else "general") + (
                "_decline" if meta.get("decline") else "_valid"
            )
            local[key] += 1
            slice_counts[key] += 1
            line_counts[rec["input"].count("\n") + 1] += 1
            n = len(rec["choices"])
            choice_counts[n] += 1
            answer = meta.get("answer")
            if not isinstance(answer, int) or isinstance(answer, bool) or not (-1 <= answer < n):
                errors.append(f"{name}:{i + 1}: bad audit answer={answer}")
            elif meta.get("decline"):
                if answer != -1:
                    errors.append(f"{name}:{i + 1}: decline record has answer={answer}")
                if rec["out"] != [-1] * n:
                    errors.append(f"{name}:{i + 1}: decline scores are not all -1")
            else:
                if answer == -1:
                    errors.append(f"{name}:{i + 1}: non-decline record has answer=-1")
                    continue
                top = max(range(n), key=lambda j: rec["out"][j])
                if top != answer:
                    errors.append(f"{name}:{i + 1}: highest confidence is not the answer")
                plus_counts[n][answer] += 1
                sid = meta.get("source_id", "")
                correct = ""
                if meta.get("kind") == "tool":
                    if sid.startswith("tool:"):
                        correct = sid.split(":", 1)[1]
                    elif sid.startswith("special:"):
                        _, behavior, pi = sid.split(":")
                        pats = [p for p in SPECIAL_PATTERNS if p["behavior"] == behavior]
                        correct = pats[int(pi)]["correct"]
                elif sid.startswith("app:"):
                    _, domain, pi = sid.split(":")
                    pats = [p for p in APP_PATTERNS if p["domain"] == domain]
                    correct = pats[int(pi)]["correct"]
                if correct and rec["choices"][answer] != correct:
                    errors.append(f"{name}:{i + 1}: answer is not {correct}")
            if meta.get("kind") == "tool":
                tool_behaviors[meta.get("behavior", "")] += 1
                if meta.get("decline"):
                    tool_declines[meta.get("reason", "")] += 1
                    if set(rec["choices"]) - set(TOOLS) - set(SPECIAL_TOOLS):
                        errors.append(f"{name}:{i + 1}: unknown tool in choices")
                else:
                    if meta.get("behavior") == "direct":
                        if set(rec["choices"]) - set(TOOLS):
                            errors.append(f"{name}:{i + 1}: unknown tool in choices")
            elif meta.get("decline"):
                general_declines[meta.get("reason", "")] += 1
        expected = entry.get("counts")
        if expected != {k: local.get(k, 0) for k in SLICES}:
            errors.append(f"{name}: per-file counts do not match manifest")
            per_file_ok = False
        all_records.extend(records)
        all_meta.extend(metas)

    # Cross-file checks
    if slice_counts["general_valid"] != config.GENERAL_VALID:
        errors.append(f"general_valid={slice_counts['general_valid']}")
    if slice_counts["general_decline"] != config.GENERAL_DECLINE:
        errors.append(f"general_decline={slice_counts['general_decline']}")
    if slice_counts["tool_valid"] != config.TOOL_VALID:
        errors.append(f"tool_valid={slice_counts['tool_valid']}")
    if slice_counts["tool_decline"] != sum(config.TOOL_DECLINE.values()):
        errors.append(f"tool_decline={slice_counts['tool_decline']}")
    domain_counts = Counter(m["domain"] for m in all_meta if m["kind"] == "general")
    for domain, (valid, decline_n) in config.GENERAL.items():
        if domain_counts[domain] != valid + decline_n:
            errors.append(f"general domain {domain}: {domain_counts[domain]} != {valid + decline_n}")
    for domain, expected in config.APPLICATIONS.items():
        if domain_counts[domain] != expected:
            errors.append(f"application {domain}: {domain_counts[domain]} != {expected}")
    if sum(line_counts.values()) != config.TOTAL:
        errors.append(f"total records={sum(line_counts.values())}")
    for k, v in config.LINE_COUNTS.items():
        if line_counts[k] != v:
            errors.append(f"line_count {k}: {line_counts[k]} != {v}")
    for k, v in config.CHOICE_COUNTS.items():
        if choice_counts[k] != v:
            errors.append(f"choices {k}: {choice_counts[k]} != {v}")
    for n, counter in plus_counts.items():
        vals = [counter.get(i, 0) for i in range(n)]
        if vals and max(vals) - min(vals) > 1:
            errors.append(f"index imbalance for {n} choices: {vals}")

    norm = [norm_text(r["input"]) for r in all_records]
    unique = len(set(norm))
    if unique != len(norm):
        errors.append(f"duplicate inputs: {len(norm) - unique}")
    if any(not r["choices"] for r in all_records):
        errors.append("empty choices list")

    if deep:
        from .generator import build_records

        rebuilt, _ = build_records()
        a = sorted(json.dumps(r, sort_keys=True, ensure_ascii=False) for r in all_records)
        b = sorted(json.dumps(r, sort_keys=True, ensure_ascii=False) for r in rebuilt)
        if a != b:
            errors.append("deep check: dataset records differ from generator output")

    checks = {
        "records": sum(line_counts.values()),
        "unique_inputs": unique,
        "files": len(files),
        "bytes": sum(e.get("bytes", 0) for e in files),
        "slices": dict(slice_counts),
        "line_counts": {str(k): v for k, v in sorted(line_counts.items())},
        "choice_counts": {str(k): v for k, v in sorted(choice_counts.items())},
        "tool_behaviors": dict(sorted(tool_behaviors.items())),
        "tool_decline_reasons": dict(sorted(tool_declines.items())),
        "general_decline_pools": dict(sorted(general_declines.items())),
        "general_domains": dict(sorted(domain_counts.items())),
        "per_file_exact": per_file_ok,
        "deep": deep,
    }
    result = {"status": "passed" if not errors else "failed", "errors": errors,
              "warnings": warnings, "checks": checks}

    if write:
        (data / "validation.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        manifest["validation"] = {"status": result["status"], "errors": len(errors),
                                  "unique_inputs": unique}
        (data / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return result


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Validate the decision dataset.")
    ap.add_argument("--data", default="dataset")
    ap.add_argument("--deep", action="store_true", help="regenerate and compare every record")
    ap.add_argument("--no-write", action="store_true")
    args = ap.parse_args(argv)
    result = validate(Path(args.data), deep=args.deep, write=not args.no_write)
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
