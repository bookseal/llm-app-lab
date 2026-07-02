# From prompting to fine-tuning — support-ticket routing

A hands-on walk through three ways to solve the same task, measured on the same
test set so the numbers are directly comparable:

1. **Zero-shot prompting** — Claude routes from team definitions alone.
2. **Few-shot prompting** — add a few labeled examples to the prompt.
3. **Custom training / fine-tuning** — train a small local classifier on a
   labeled training set. No Claude calls at inference.

The task is **routing a customer-support ticket to the team that owns it**
(Billing, Account Access, Technical Support, Sales, Trust & Safety, Data Privacy).

### What makes it hard: hidden house rules

If the routing were obvious, every stage would score 100% and there'd be no
lesson. The difficulty here comes from **org-specific routing conventions that
are *not* written in the team descriptions** — exactly the situation real support
orgs are in. This company's rules:

| Ticket looks like… | Obvious guess | This company routes it to |
|---|---|---|
| "I'd like to upgrade my plan / add seats" | Sales | **Billing** (Sales handles *new* prospects only) |
| "Close / delete my account" | Account Access | **Data Privacy** (owns all account erasure) |
| "Charges I didn't make / my account was hacked" | Billing / Account Access | **Trust & Safety** (owns fraud + compromise) |
| "I can't log in — it throws a 500 / crashes" | Account Access | **Technical Support** (an error is a bug) |

These rules are deliberately kept **out of `taxonomy.json`**, so a model reasoning
from the team descriptions alone (zero-shot) gets them wrong. The few-shot
examples and the training data *demonstrate* the rules — which is the
whole point: this is knowledge you teach by example, not by definition.

## A note on "fine-tuning"

The Claude API does **not** offer self-serve fine-tuning of Claude itself. The
production-relevant pattern — and the one this project teaches — is to train a
**small, cheap, local** model on labeled data. The trained classifier here
routes a ticket in milliseconds for fractions of a cent, with no API call.

**About the training data:** in a real deployment you'd train on **real labeled
examples captured from production** (each ticket paired with the team that
actually resolved it). To keep this project self-contained and runnable without
a production log, a ready-made training set ships in
`data/synthetic_train.jsonl` (~240 labeled tickets). Swap in your own real data
and the pipeline is unchanged.

**It may or may not beat the prompting stages on accuracy — and that's the
lesson either way.** What you're comparing is a trade-off space: a prompt is
zero-setup but pays a model call per ticket; a trained model is near-free and
instant per ticket but only as good as the data you trained it on. Watch *where* each
approach wins and loses (the per-class F1 and confusion matrix make this concrete).

## Setup

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# set ANTHROPIC_API_KEY
```

First run downloads the embedding model (`all-MiniLM-L6-v2`, ~80 MB), one-time.

## Run order

```bash
# 1. Baselines (each calls Claude once per test ticket, prints its own report)
python stage0_zeroshot.py
python stage1_fewshot.py

# 2. Train the small classifier on the included training set and score it on
#    the same test set (data/synthetic_train.jsonl ships with the project)
python stage2_finetune.py

# 3. See all three side by side (reads cached predictions — no new Claude calls)
python evaluate.py
```

`evaluate.py` prints a progression table:

```
================  PROGRESSION  ================
stage                              accuracy  macro-F1
Stage 0 — zero-shot prompting          ...      ...
Stage 1 — few-shot prompting           ...      ...
Stage 2 — distilled classifier         ...      ...
```

## What's in here

```
finetune/
├── data/
│   ├── taxonomy.json          team names + definitions (used in prompts)
│   ├── test.jsonl             48 hand-labeled gold tickets — the fixed yardstick
│   ├── seed_examples.jsonl    21 labeled examples for few-shot (disjoint from test)
│   ├── synthetic_train.jsonl  the training set (~240 labeled tickets, ships with project)
│   └── preds/                 each stage's predictions (for the comparison)
├── common.py                  taxonomy/IO, Claude routing (forced tool), embeddings
├── stage0_zeroshot.py
├── stage1_fewshot.py
├── stage2_finetune.py         embed → logistic-regression classifier
├── evaluate.py                scoring (accuracy, per-class F1, confusion) + progression
└── classifier.joblib          the trained model (created by stage 2)
```

## Design choices worth discussing in class

- **Same test set, same metric, every stage.** The only thing that changes is the
  method. The test set is never used for examples or training (no leakage).
- **Forced tool + enum.** Every Claude call is constrained to a valid team, so the
  difference between stages is *accuracy*, never malformed output.
- **The taxonomy must be hard enough.** If zero-shot already scored 100%, there'd
  be no progression to show. The confusable categories are the point.
- **Training-data quality is the ceiling for stage 2.** The classifier can only
  learn the boundaries present in its training set. Biased or low-diversity data
  → a biased classifier. Inspect `synthetic_train.jsonl` — and in production,
  prefer real labeled tickets captured from your logs.

## Things to try

- Replace `data/synthetic_train.jsonl` with your own labeled tickets (same
  `{"text", "team"}` format) and re-run stage 2 — the pipeline is unchanged.
- Swap `LogisticRegression` for a small MLP (`sklearn.neural_network.MLPClassifier`).
- Add more confusable test cases and see which stage degrades first.
- Translate a few test tickets into another language — the prompt stages handle
  it; the trained classifier only will if you switch `EMBED_MODEL` (in
  `common.py`) to the multilingual model used elsewhere in the course.
