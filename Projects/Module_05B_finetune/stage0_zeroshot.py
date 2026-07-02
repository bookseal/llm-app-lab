"""Stage 0 — zero-shot routing.

Claude sees only the team definitions and the ticket. No examples. This is the
baseline: how well does a general model route using instructions alone?
"""
import common
from evaluate import print_report

SYSTEM = f"""You route incoming customer-support tickets to the team that owns them.
Choose exactly one team. The teams are:

{common.taxonomy_block()}

Call the route_ticket tool with the single best team for the ticket."""


def predict(tickets):
    return common.route_testset(SYSTEM, tickets)


def main():
    tickets = common.load_jsonl(common.DATA / "test.jsonl")
    preds = predict(tickets)
    common.write_jsonl(common.PREDS / "stage0_zeroshot.jsonl", preds)
    print_report(
        "Stage 0 — zero-shot prompting",
        [p["gold"] for p in preds],
        [p["pred"] for p in preds],
        common.team_names(),
    )


if __name__ == "__main__":
    main()
