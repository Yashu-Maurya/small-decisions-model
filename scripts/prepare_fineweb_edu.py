"""Stream FineWeb-Edu into reproducible UTF-8 text shards.

The source token_count is a GPT-2 token estimate. A trained tokenizer will have
different counts. Run this only after choosing a dataset size and source.
"""

import argparse
import json
from pathlib import Path

from datasets import load_dataset


SOURCE = "HuggingFaceFW/fineweb-edu"
CONFIG = "sample-10BT"
REVISION = "87f0914"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("data/fineweb_edu_1b"))
    parser.add_argument("--train-tokens", type=int, default=1_000_000_000)
    parser.add_argument("--validation-tokens", type=int, default=5_000_000)
    parser.add_argument("--shard-tokens", type=int, default=100_000_000)
    args = parser.parse_args()
    if min(args.train_tokens, args.validation_tokens, args.shard_tokens) <= 0:
        parser.error("token targets must be positive")
    args.output.mkdir(parents=True, exist_ok=True)
    if any(args.output.iterdir()):
        parser.error(f"output directory is not empty: {args.output}")

    stream = load_dataset(
        SOURCE, name=CONFIG, split="train", streaming=True, revision=REVISION
    )
    counts = {"train": 0, "validation": 0}
    documents = {"train": 0, "validation": 0}
    shards = []
    shard_index = -1
    shard_tokens = 0
    writer = None
    current_split = None
    try:
        for row in stream:
            text = row.get("text")
            tokens = row.get("token_count")
            if not isinstance(text, str) or not text.strip():
                continue
            if not isinstance(tokens, int) or tokens <= 0:
                raise ValueError("source row lacks a valid token_count")
            split = "train" if counts["train"] < args.train_tokens else "validation"
            if split == "validation" and counts["validation"] >= args.validation_tokens:
                break

            if split == "train" and (writer is None or shard_tokens >= args.shard_tokens):
                if writer is not None:
                    writer.close()
                shard_index += 1
                name = f"train-{shard_index:03d}.txt"
                writer = (args.output / name).open("w", encoding="utf-8", newline="\n")
                shards.append({"file": name, "source_tokens": 0, "documents": 0})
                shard_tokens = 0
                current_split = "train"
            elif split == "validation" and current_split == "train":
                writer.close()
                writer = None
                current_split = None

            if split == "validation":
                if writer is None:
                    name = "validation.txt"
                    writer = (args.output / name).open("w", encoding="utf-8", newline="\n")
                    shards.append({"file": name, "source_tokens": 0, "documents": 0})
                    current_split = "validation"

            writer.write(text.rstrip() + "\n\n")
            counts[split] += tokens
            documents[split] += 1
            shards[-1]["source_tokens"] += tokens
            shards[-1]["documents"] += 1
            if split == "train":
                shard_tokens += tokens
            if sum(documents.values()) % 10_000 == 0:
                print(f"train={counts['train']:,} validation={counts['validation']:,}", flush=True)
    finally:
        if writer is not None:
            writer.close()

    if counts["train"] < args.train_tokens or counts["validation"] < args.validation_tokens:
        raise RuntimeError(f"stream ended early: {counts}")
    manifest = {
        "source": SOURCE,
        "config": CONFIG,
        "revision": REVISION,
        "format": "UTF-8 plain text; documents separated by blank lines",
        "token_count_basis": "FineWeb-Edu source token_count (GPT-2 tokenizer estimate)",
        "requested_tokens": {"train": args.train_tokens, "validation": args.validation_tokens},
        "actual_source_tokens": counts,
        "documents": documents,
        "shards": shards,
    }
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(counts), flush=True)


if __name__ == "__main__":
    main()
