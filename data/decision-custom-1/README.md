# decision-custom-1

A synthetic, deterministic decision dataset for training a tiny model to rank a
list of options with calibrated confidence scores.

- **1,010,000** decisions in **101 JSONL files** of 10,000 records each
  (`decisions-00000.jsonl` … `decisions-00100.jsonl`).
- **252,500** tool-routing decisions, including **50,500** tool declines.
- **151,500** declines total (15%).
- **150,000** real-world application decisions: 60,000 smart-home action
  selections, 40,000 animation selections, and 50,000 `true`/`false` spam,
  phishing and safety classifications.
- **1,010,000 unique inputs**; no scraped text and no per-example LLM calls.
- Reproducible from a fixed seed with the included Python generator (v2.0.0).

## Record format

```json
{"input":"...","choices":["...","..."],"out":[0.93,0.07]}
```

- `input`: 1–3 newline-separated lines.
- `choices`: 2–10 distinct short strings.
- `out`: one confidence score per choice, in `[0, 1]`, **summing to 1**.
  The score at the index of the correct option is the largest (0.82–0.97).

For a decline — no listed option is acceptable — every score is `-1`:

```json
{"input":"...","choices":["...","..."],"out":[-1,-1]}
```

`-1` is never a choice. Declines are used for unsafe, underspecified,
irrelevant, impossible, or already-completed requests, and for situations where
none of the listed actions is appropriate.

## Composition

| Slice | Count |
|---|---:|
| General valid (incl. applications) | 656,500 |
| General decline | 101,000 |
| Tool valid | 202,000 |
| Tool decline | 50,500 |
| **Total** | **1,010,000** |

| Application | Count | Choices |
|---|---:|---:|
| Home-control action selection | 60,000 | 10 |
| Avatar-animation selection | 40,000 | 8 |
| True/false classification | 50,000 | 2 (`true`, `false`) |

Other exact distributions:

| Property | Counts |
|---|---|
| Input lines | 1: 505,000 · 2: 303,000 · 3: 202,000 |
| Choice count | 2: 50,000 · 3: 101,000 · 4: 557,000 · 5: 151,500 · 6: 50,500 · 8: 40,000 · 10: 60,000 |
| Correct index | balanced within each choice-count bucket |
| Tool behaviour | direct 161,600 · clarify/confirm 20,200 · read-only 10,100 · multi-step 10,100 |

General domains: work, social, everyday, health, money, travel, learning,
communication, ethics. Tool domains: calendar/email, search, files/code,
shopping/payments, travel/maps, messaging, CRM/data, smart home, health,
productivity, and other.

## Real-world-style decisions

- **Home control:** a first-person intent such as `I'm heading into the kitchen
  this evening and need the light on right away.` The ten candidate actions and
  their short descriptions are embedded in the input; the model must pick the
  right one from the confidence scores.
- **Animations:** first- and second-person intents (`I want to agree without
  speaking` / `You saw a friend at the door`) mapped to eight avatar animations
  such as `wave`, `nod`, `shake_head`, `celebrate`, `sit_down`.
- **True/false:** spam and phishing filtering, abusive-comment and fake-review
  flags, unsafe-request detection, duplicate-ticket and private-data checks.
  The only options are `"true"` and `"false"`, and the question text states
  explicitly what `true` means.

## Files

```
dataset/
  decisions-00000.jsonl ... decisions-00100.jsonl  # training records
  manifest.json                                     # counts, hashes, distributions
  stats.json                                        # distribution only
  checksums.sha256                                  # sha256 of the 101 data files
  preview.jsonl                                     # 500-record preview
  validation.json                                   # validator output
  REPORT.md                                         # human-readable summary
  audit/
    decisions-00000.meta.jsonl ...                  # QA metadata, one row per record
```

Only the `decisions-*.jsonl` files are model input. The `audit/` sidecars carry
provenance, the correct answer index, and slice labels; do not train on them.

## Reproduce

Requires Python 3.10+ and no third-party packages.

```bash
python3 -m decisiongen generate --out dataset
python3 -m decisiongen validate --data dataset --deep
```

Generation takes about a minute. `--deep` rebuilds every record and checks
that the files match the generator output byte for byte.

Useful commands:

```bash
python3 -m decisiongen sample --data dataset --n 5 --tool --no-decline
python3 -m decisiongen sample --data dataset --n 5 --domain home_control
python3 -m decisiongen sample --data dataset --n 5 --domain binary
python3 -m decisiongen stats --data dataset
python3 -m unittest discover -s tests -v
```

## Design notes

- **Deterministic:** seed `20261124`, version `2.0.0`.
- **Authored templates + slots:** scenario cards define the situation, correct
  action, and distractor pool. Names, times, places, and tool arguments are
  sampled from hand-written pools.
- **Disjoint splits:** roughly 96/2/2 train/val/test by card and by tool. Splits
  live only in the audit metadata so the training files stay simple.
- **Confidence targets:** integer weights summing to 10,000 are converted to
  four-decimal scores, so each `out` is a small probability distribution. The
  correct option always receives 0.82–0.97; declines use all `-1`.
- **Tool and action choices** are names with short descriptions embedded in the
  input, so the task tests routing rather than memorising a catalog.

## Limitations

English-only, template-driven, and intentionally compact. The tool and animation
catalogs and all scenarios are fictional. Health, money, safety and spam
examples are decision-making exercises, not professional advice or production
filters. Distractors are often clearly bad, so the dataset is best treated as a
curriculum or smoke-test set for small models, not a benchmark of nuanced
judgement. See `DATASET_CARD.md` for details.
