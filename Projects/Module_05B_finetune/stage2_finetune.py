"""Stage 2 — distillation: train a small classifier on the synthetic data.

We embed each Claude-generated ticket with a local sentence-transformer and fit
a logistic-regression classifier on those vectors. At inference time there are
NO Claude calls — just an embed + a matrix multiply, so routing a ticket costs
fractions of a cent and runs in milliseconds.

This is "fine-tuning" in the practical sense: we specialized a small model on
our task using data distilled from the big model. (The Claude API doesn't expose
self-serve fine-tuning of Claude itself; distilling into a small local model is
the runnable, production-relevant version of the same idea.)
"""
import sys

import joblib
from sklearn.linear_model import LogisticRegression

import common
from evaluate import print_report

MODEL_PATH = common.ROOT / "classifier.joblib"


def train():
    train_path = common.DATA / "synthetic_train.jsonl"
    if not train_path.exists():
        raise FileNotFoundError(
            "No training data at data/synthetic_train.jsonl. This file ships with "
            "the project; restore it (or drop in your own labeled tickets in the "
            "same {\"text\", \"team\"} format)."
        )
    rows = common.load_jsonl(train_path)
    X = common.embed([r["text"] for r in rows])
    y = [r["team"] for r in rows]
    clf = LogisticRegression(max_iter=2000, C=10.0)
    clf.fit(X, y)
    joblib.dump(clf, MODEL_PATH)
    print(f"Trained on {len(rows)} synthetic tickets -> {MODEL_PATH.name}", file=sys.stderr)
    return clf


def load_classifier():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"No trained classifier at {MODEL_PATH.name}. Run `python stage2_finetune.py` "
            "(after `python generate_synthetic.py`)."
        )
    return joblib.load(MODEL_PATH)


def predict(tickets):
    clf = load_classifier()
    X = common.embed([t["text"] for t in tickets])
    preds = clf.predict(X)
    return [
        {"id": t["id"], "gold": t["team"], "pred": str(p), "text": t["text"]}
        for t, p in zip(tickets, preds)
    ]


def main():
    train()
    tickets = common.load_jsonl(common.DATA / "test.jsonl")
    preds = predict(tickets)
    common.write_jsonl(common.PREDS / "stage2_finetune.jsonl", preds)
    print_report(
        "Stage 2 — distilled classifier",
        [p["gold"] for p in preds],
        [p["pred"] for p in preds],
        common.team_names(),
    )


if __name__ == "__main__":
    main()
