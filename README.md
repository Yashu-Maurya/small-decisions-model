# SLM lab

A local experiment in training a small **text-to-decision** model. Given a text input and a list of possible actions, the model scores each action and an additional **none of these** option. The choices can change from one request to the next.

## Setup

Use Python 3.11–3.13. The existing `.venv` uses Python 3.13.

```sh
source .venv/bin/activate
python -c 'import torch; print(torch.__version__)'
```

To recreate the environment:

```sh
uv venv --python 3.13 .venv
uv pip install --python .venv/bin/python -e '.[dev]'
```

The training script currently sets `DEVICE = "mps"`, so it requires a Mac with a working PyTorch MPS backend. Check with:

```sh
.venv/bin/python -c 'import torch; print(torch.backends.mps.is_available())'
```

## Decision dataset

The active dataset is in [`data/decision-custom-1/dataset`](data/decision-custom-1/dataset). It has 1,010,000 synthetic records across 101 JSONL files. Each record has this shape:

```json
{"input":"Tell me a joke","choices":["Reply with a joke","laugh_animation"],"out":[0.9,0.1]}
```

`out` is a synthetic target distribution over the listed choices. An all-`-1` array means that none of the choices should be selected. The model converts that case into a target of 1.0 for its extra **none of these** output. See the [dataset card](data/decision-custom-1/DATASET_CARD.md) for the dataset's construction, limitations, and split metadata. The corresponding `dataset/audit/decisions-*.meta.jsonl` files identify train, validation, and test records.

## Tokenizer and model

[`src/slm/tokenizer.py`](src/slm/tokenizer.py) implements byte-level BPE. The trained tokenizer is saved as `src/slm/merges.json` and `src/slm/vocab.json`. Training and prediction must use the same merges: changing token IDs after training makes a checkpoint incompatible with the tokenizer.

[`src/slm/train.py`](src/slm/train.py) defines `SmolDecision`. It embeds and averages the input tokens and each choice's tokens. A shared network produces one logit per choice, and another layer produces the **none of these** logit. Softmax turns the logits into probabilities. Training uses soft-label cross-entropy against `out`.

## Train

Run from the project root:

```sh
PYTHONPATH=src .venv/bin/python -m slm.train
```

The script writes `checkpoints/smol_decision_epoch1.pt`. **As currently written, it trains only on `dataset_files[1:2]`**, the second sorted data file. Its progress denominator still reads the full dataset count from `manifest.json`, so the percentage and ETA do not describe this subset run. Change the file selection and progress total together before running the whole corpus.

The current training loop also does not use the audit split labels, so a full-file run would include validation and test records. Use those labels to separate records before reporting validation or test accuracy. The checkpoint stores model weights; keep the tokenizer files and the model dimensions alongside it.

## Predict

After training has produced the checkpoint, run:

```sh
PYTHONPATH=src .venv/bin/python -m slm.predict
```

[`src/slm/predict.py`](src/slm/predict.py) loads the checkpoint and prints probabilities and the selected decision for its current example list. It selects MPS when available and otherwise uses CPU. These printed probabilities reproduce synthetic training targets; they are not calibrated estimates of real-world correctness.

## Other corpus

[`data/fineweb_edu_1b`](data/fineweb_edu_1b) contains a separate, unlabeled FineWeb-Edu text corpus: about 1 billion source-counted GPT-2 tokens for training and 5 million for validation. It is not used by the current decision model. Its `manifest.json` records provenance, sizes, and checksums. The preparation scripts are in `scripts/`.
