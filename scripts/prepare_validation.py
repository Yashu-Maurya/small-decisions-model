"""Create a held-out FineWeb-Edu text validation file from a separate shard."""

import json
from pathlib import Path

from datasets import load_dataset


OUTPUT = Path("data/fineweb_edu_1b")
SOURCE_FILE = (
    "https://huggingface.co/datasets/HuggingFaceFW/fineweb-edu/resolve/"
    "87f0914/sample/10BT/013_00000.parquet"
)
TARGET = 5_000_000


def main() -> None:
    manifest_path = OUTPUT / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    stream = load_dataset("parquet", data_files={"train": SOURCE_FILE}, split="train", streaming=True)
    path = OUTPUT / "validation.txt"
    tokens = 0
    documents = 0
    with path.open("w", encoding="utf-8", newline="\n") as writer:
        for row in stream:
            text = row.get("text")
            count = row.get("token_count")
            if not isinstance(text, str) or not text.strip():
                continue
            if not isinstance(count, int) or count <= 0:
                raise ValueError("source row lacks a valid token_count")
            writer.write(text.rstrip() + "\n\n")
            tokens += count
            documents += 1
            if tokens >= TARGET:
                break
    if tokens < TARGET:
        raise RuntimeError(f"only {tokens} tokens were available")
    manifest["actual_source_tokens"]["validation"] = tokens
    manifest["documents"]["validation"] = documents
    manifest["validation_source_file"] = SOURCE_FILE
    manifest["shards"] = [s for s in manifest["shards"] if s["file"] != "validation.txt"]
    manifest["shards"].append({"file": "validation.txt", "source_tokens": tokens, "documents": documents})
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"validation={tokens:,} tokens, {documents:,} documents")


if __name__ == "__main__":
    main()
