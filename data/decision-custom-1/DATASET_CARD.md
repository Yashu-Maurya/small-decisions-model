# Dataset Card: decision-custom-1

## Overview

- **Name:** decision-custom-1
- **Version:** 2.0.0
- **Format:** JSONL, one record per line
- **Size:** 1,010,000 records across 101 files (~344 MiB / 361 MB)
- **Language:** English
- **License:** synthetic data generated for this project; names, organisations,
  tools, and events are fictional
- **Generator seed:** 20261124

## Purpose

Train and evaluate a small language model on constrained decision tasks: given
a short situation and a list of options, return a confidence score for every
option, or `-1` for every option when none is acceptable. A quarter of the data
covers tool routing; the rest covers everyday, social, work, health, money,
travel, learning, communication, ethics, and three real-world-style application
families (smart-home control, avatar animations, and true/false spam & safety
classification).

## Schema

```json
{"input": "string (1-3 lines)", "choices": ["string", "..."],
 "out": [0.02, 0.95, 0.03]}
```

- `choices` has 2–10 distinct entries.
- `out` has exactly one number per choice. Scores are in `[0, 1]` and sum to 1.
- The highest score marks the selected option (0.82–0.97); the correct index is
  approximately balanced per choice-count bucket.
- A decline is `[-1, ..., -1]`, with one `-1` per choice. `-1` is never listed as
  a choice.

## Composition

| Slice | Records |
|---|---:|
| General valid (incl. applications) | 656,500 |
| General decline | 101,000 |
| Tool valid | 202,000 |
| Tool decline | 50,500 |

- Tool records: 252,500 (25%).
- Decline records: 151,500 (15%), of which 50,500 are tool declines.
- Input lines: 505,000 / 303,000 / 202,000 for 1 / 2 / 3 lines.
- Choice counts: 50,000 / 101,000 / 557,000 / 151,500 / 50,500 / 40,000 /
  60,000 for 2 / 3 / 4 / 5 / 6 / 8 / 10 choices.
- Every normalised input occurs exactly once.

| Application family | Records | Choices | Person |
|---|---:|---:|---|
| Home control | 60,000 | 10 named actions | mostly first person |
| Animation routing | 40,000 | 8 named animations | first and second person |
| True/false classification | 50,000 | `true`, `false` | third-person message text |

Tool-valid behaviours: direct 161,600, clarify/confirm 20,200, read-only 10,100,
multi-step 10,100. Tool-decline reasons: unsafe/destructive 15,150, missing
arguments 12,120, no suitable tool 8,080, policy/privacy 7,070, ambiguous 5,050,
already done 3,030.

## Construction

The dataset is fully synthetic. Scenario cards were hand-authored, each with
situation templates, a correct action or option, and a distractor pool. The
generator samples cards, slots, line layout, choice count, and target index
under exact quotas. It uses no web scraping, no user data, no third-party
datasets, and no per-example model calls. Names, places, companies, tools, and
animations are invented. Generation is deterministic: the same seed and code
produce byte-identical files.

Confidence targets are generated as integer weights out of 10,000 and converted
to four-decimal scores, so each distribution sums to exactly 1 in integer
arithmetic (within floating-point tolerance in the JSON). The selected option
receives 0.82–0.97; decline records use `-1` throughout.

Around 96% of cards/tools are assigned to train, 2% to validation, and 2% to
test. Splits are card- and tool-disjoint and stored only in the audit sidecars.
The canonical JSONL files contain no split labels or answer indices.

## Intended use

- Supervised fine-tuning or evaluation of small models on constrained choice
  selection, tool routing, action selection, and binary classification.
- Training a model to emit a calibrated probability distribution over options,
  with a clear convention for "none of the above".
- Curriculum experiments where a compact, fully controllable dataset is useful.

## Out of scope

- Factual question answering, open-ended dialogue, or general instruction
  following.
- Real tool execution, real API schemas, or production tool safety.
- Professional medical, legal, or financial advice.
- Production spam/phishing filtering; the classification examples are simple
  synthetic templates, not representative of real mail.
- Claims about human preference, fairness, or real-world decision quality.

## Biases and limitations

- English-only, with a mostly European city list and Western office/consumer
  settings.
- Template artefacts remain: phrasing repeats, and some distractors are
  obviously wrong.
- The tool and animation catalogs are fictional; their descriptions are embedded
  in the input, so the task tests routing rather than knowledge of real APIs.
- Confidence values are synthetic targets, not measured model calibration.
- Decline examples teach a conservative policy: when a request is unsafe,
  underspecified, impossible, or already done, the correct output is all `-1`.
  This is a dataset convention, not a universal rule for deployed systems.
- Health and safety scenarios are illustrative and must not be treated as
  guidance.

## Maintenance

- Source code and tests live in this repository.
- `dataset/manifest.json` records per-file counts and SHA-256 hashes.
- `dataset/checksums.sha256` covers all 101 data files.
- Regenerate with `python3 -m decisiongen generate --out dataset`; verify with
  `python3 -m decisiongen validate --data dataset --deep`.
- Bump `VERSION` and change `SEED` for a new release, then regenerate the
  manifest, checksums, and this card.
