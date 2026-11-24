"""Command line interface: generate, validate, sample."""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

from . import config
from .generator import build_records, write_dataset


def _cmd_generate(args: argparse.Namespace) -> int:
    out = Path(args.out)
    records, metas = build_records()
    manifest = write_dataset(out, records, metas)
    print(json.dumps({
        "out": str(out),
        "records": manifest["totals"]["records"],
        "files": manifest["totals"]["files"],
        "tool": manifest["totals"]["tool"],
        "decline": manifest["totals"]["decline"],
        "bytes": manifest["totals"]["bytes"],
    }, indent=2))
    return 0


def _cmd_validate(args: argparse.Namespace) -> int:
    from .validate import validate

    result = validate(Path(args.data), deep=args.deep, write=not args.no_write)
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "passed" else 1


def _load(data: Path):
    manifest = json.loads((data / "manifest.json").read_text(encoding="utf-8"))
    records, metas = [], []
    for entry in manifest["files"]:
        name = entry["path"]
        with (data / name).open("r", encoding="utf-8") as fh:
            records.extend(json.loads(line) for line in fh)
        with (data / "audit" / name.replace(".jsonl", ".meta.jsonl")).open("r", encoding="utf-8") as fh:
            metas.extend(json.loads(line) for line in fh)
    return records, metas


def _cmd_sample(args: argparse.Namespace) -> int:
    data = Path(args.data)
    records, metas = _load(data)
    picked = []
    for rec, meta in zip(records, metas):
        if args.decline is True and not meta["decline"]:
            continue
        if args.decline is False and meta["decline"]:
            continue
        if args.domain and meta["domain"] != args.domain:
            continue
        if args.tool is True and meta["kind"] != "tool":
            continue
        if args.tool is False and meta["kind"] == "tool":
            continue
        picked.append((rec, meta))
        if len(picked) >= args.n:
            break
    for rec, meta in picked:
        print(f"# {meta['source_id']} domain={meta['domain']} decline={meta['decline']} "
              f"answer={meta['answer']} out={rec['out']}")
        print(rec["input"])
        print(" | ".join(f"{i}:{c}" for i, c in enumerate(rec["choices"])))
        print()
    if not picked:
        print("no records matched", file=sys.stderr)
        return 1
    return 0


def _cmd_stats(args: argparse.Namespace) -> int:
    manifest = json.loads((Path(args.data) / "manifest.json").read_text(encoding="utf-8"))
    print(json.dumps(manifest["distribution"], indent=2))
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="decisiongen", description="Synthetic decision dataset generator.")
    sub = ap.add_subparsers(dest="command", required=True)

    g = sub.add_parser("generate", help="write the dataset files and manifest")
    g.add_argument("--out", default="dataset")
    g.set_defaults(func=_cmd_generate)

    v = sub.add_parser("validate", help="validate a generated dataset")
    v.add_argument("--data", default="dataset")
    v.add_argument("--deep", action="store_true", help="regenerate and compare all records")
    v.add_argument("--no-write", action="store_true")
    v.set_defaults(func=_cmd_validate)

    s = sub.add_parser("sample", help="print sample records")
    s.add_argument("--data", default="dataset")
    s.add_argument("--n", type=int, default=10)
    s.add_argument("--domain")
    s.add_argument("--tool", action=argparse.BooleanOptionalAction, default=None)
    s.add_argument("--decline", action=argparse.BooleanOptionalAction, default=None)
    s.set_defaults(func=_cmd_sample)

    st = sub.add_parser("stats", help="print distribution stats")
    st.add_argument("--data", default="dataset")
    st.set_defaults(func=_cmd_stats)

    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
