# SLM lab

A starter workspace for training a small language model from scratch locally.

## Environment

Use Python 3.11–3.13. The system Python detected during setup was 3.15, which is outside this project's supported range. A Python 3.13 environment is already present in `.venv`.

```sh
source .venv/bin/activate
python -c 'import torch, datasets, transformers; print("ready")'
```

If recreating the environment, use a compatible Python version with `uv venv --python 3.13 .venv` and `uv pip install --python .venv/bin/python -e '.[dev]'`.

## Dataset

The prepared FineWeb-Edu corpus is in [`data/fineweb_edu_1b`](data/fineweb_edu_1b):

- `train-000.txt` through `train-009.txt`: 1,000,000,679 source-counted GPT-2 tokens in UTF-8 plain text, about 4.6 GB total.
- `validation.txt`: 5,006,866 source-counted GPT-2 tokens from a separate source shard, about 23 MB.
- `manifest.json`: source revision, token and document counts, file sizes, and SHA-256 checksums.

Each document is followed by a blank line. The exact count will change when a new tokenizer is trained. The text files are ignored by Git. Source: [HuggingFaceFW/fineweb-edu](https://huggingface.co/datasets/HuggingFaceFW/fineweb-edu), `sample-10BT`, revision `87f0914`.

To regenerate in an empty output directory, run `python scripts/prepare_fineweb_edu.py --output data/new_fineweb_edu_1b`. The current validation file was generated from a separate held-out sample shard with `python scripts/prepare_validation.py`.

## Layout

- `src/slm/`: model and training code
- `data/`: datasets and processed data (ignored by Git)
- `checkpoints/`: model weights (ignored by Git)
- `runs/`: logs and metrics (ignored by Git)

Next step: train a tokenizer, then define the model and training pipeline for this corpus.

