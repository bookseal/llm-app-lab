"""Shared scoring, and the final side-by-side comparison.

Each stage script writes its predictions to data/preds/<stage>.jsonl and prints
its own report (via print_report below). Run `python evaluate.py` afterwards to
see all stages in one progression table — it reads the cached predictions, so it
makes no new Claude calls.
"""
import common

STAGES = [
    ("stage0_zeroshot", "Stage 0 — zero-shot prompting"),
    ("stage1_fewshot", "Stage 1 — few-shot prompting"),
    ("stage2_finetune", "Stage 2 — distilled classifier"),
]


def accuracy(golds, preds):
    return sum(g == p for g, p in zip(golds, preds)) / len(golds)


def per_class(golds, preds, labels):
    """Precision, recall, F1, and support (n) for each label."""
    out = {}
    for lab in labels:
        tp = sum(g == lab and p == lab for g, p in zip(golds, preds))
        fp = sum(g != lab and p == lab for g, p in zip(golds, preds))
        fn = sum(g == lab and p != lab for g, p in zip(golds, preds))
        prec = tp / (tp + fp) if tp + fp else 0.0
        rec = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
        out[lab] = (prec, rec, f1, tp + fn)
    return out


def macro_f1(golds, preds, labels):
    pc = per_class(golds, preds, labels)
    return sum(v[2] for v in pc.values()) / len(labels)


def print_report(title, golds, preds, labels):
    print(f"\n=== {title} ===")
    print(f"accuracy: {accuracy(golds, preds):.1%}    macro-F1: {macro_f1(golds, preds, labels):.3f}\n")

    pc = per_class(golds, preds, labels)
    print(f"{'team':<18}{'prec':>6}{'rec':>6}{'F1':>7}{'n':>5}")
    for lab in labels:
        p, r, f, n = pc[lab]
        print(f"{lab:<18}{p:>6.2f}{r:>6.2f}{f:>7.2f}{n:>5}")

    # Confusion matrix — rows are the true team, columns the predicted team.
    print("\nconfusion (row = gold, col = predicted):")
    idx = {lab: i for i, lab in enumerate(labels)}
    mat = [[0] * len(labels) for _ in labels]
    for g, p in zip(golds, preds):
        mat[idx[g]][idx[p]] += 1
    print(f"{'':<19}" + "".join(f"{j:>4}" for j in range(len(labels))))
    for i, lab in enumerate(labels):
        print(f"{i}. {lab:<16}" + "".join(f"{mat[i][j]:>4}" for j in range(len(labels))))
    print("  " + "   ".join(f"{i}={lab}" for i, lab in enumerate(labels)))


def load_preds(stage):
    path = common.PREDS / f"{stage}.jsonl"
    return common.load_jsonl(path) if path.exists() else None


def main():
    labels = common.team_names()
    rows = []
    for stage, title in STAGES:
        preds = load_preds(stage)
        if preds is None:
            rows.append((title, None))
            continue
        golds = [p["gold"] for p in preds]
        ps = [p["pred"] for p in preds]
        rows.append((title, (accuracy(golds, ps), macro_f1(golds, ps, labels))))

    print("\n================  PROGRESSION  ================")
    print(f"{'stage':<34}{'accuracy':>10}{'macro-F1':>10}")
    for title, m in rows:
        if m is None:
            print(f"{title:<34}{'(not run)':>20}")
        else:
            print(f"{title:<34}{m[0]:>9.1%}{m[1]:>10.3f}")

    if any(m is None for _, m in rows):
        print("\nSome stages haven't been run yet — see the README for the run order.")


if __name__ == "__main__":
    main()
