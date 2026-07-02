"""Stage 1 — few-shot routing.

The same prompt as stage 0, plus a handful of labeled examples per team drawn
from data/seed_examples.jsonl. The examples teach Claude where *your* team
boundaries actually sit — especially the confusable ones.
"""
import common
from evaluate import print_report


def build_system() -> str:
    examples = common.load_jsonl(common.DATA / "seed_examples.jsonl")
    ex_block = "\n\n".join(f'Ticket: "{e["text"]}"\nTeam: {e["team"]}' for e in examples)
    return f"""You route incoming customer-support tickets to the team that owns them.
Choose exactly one team. The teams are:

{common.taxonomy_block()}

Here are example tickets and the correct team for each:

{ex_block}

Call the route_ticket tool with the single best team for the ticket."""


SYSTEM = build_system()


def predict(tickets):
    return common.route_testset(SYSTEM, tickets)


def main():
    tickets = common.load_jsonl(common.DATA / "test.jsonl")
    preds = predict(tickets)
    common.write_jsonl(common.PREDS / "stage1_fewshot.jsonl", preds)
    print_report(
        "Stage 1 — few-shot prompting",
        [p["gold"] for p in preds],
        [p["pred"] for p in preds],
        common.team_names(),
    )


if __name__ == "__main__":
    main()
