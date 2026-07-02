"""Shared helpers for the finetune project.

Covers the three things every stage needs: the taxonomy + data IO, Claude-based
routing (for the prompt stages), and the local embedder (for the distilled
classifier stage).
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent
DATA = ROOT / "data"
PREDS = DATA / "preds"

# Claude model used for the prompt-based stages and synthetic data generation.
# Matches the rest of the course; classification is cheap so Sonnet is plenty.
MODEL = "claude-sonnet-4-6"

# Local sentence-transformer used to turn tickets into vectors for the
# distilled classifier. 384-dim, ~80MB, runs on CPU.
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


# ════════════════════════════════════════════════════════════════
# Taxonomy + data IO
# ════════════════════════════════════════════════════════════════

def load_taxonomy() -> list[dict]:
    return json.loads((DATA / "taxonomy.json").read_text())["teams"]


def team_names() -> list[str]:
    return [t["name"] for t in load_taxonomy()]


def taxonomy_block() -> str:
    """The team list as prompt text — used verbatim in the prompt stages."""
    return "\n".join(f"- {t['name']}: {t['description']}" for t in load_taxonomy())


def load_jsonl(path) -> list[dict]:
    path = Path(path)
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def write_jsonl(path, rows) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(r) for r in rows) + "\n")


# ════════════════════════════════════════════════════════════════
# Claude routing — used by the prompt-based stages (0 and 1)
# ════════════════════════════════════════════════════════════════

_client = None


def get_client():
    global _client
    if _client is None:
        from anthropic import Anthropic
        from dotenv import load_dotenv
        load_dotenv()  # ANTHROPIC_API_KEY from .env
        _client = Anthropic()
    return _client


def route_tool(names: list[str]) -> dict:
    """A forced tool whose only field is the team, constrained to a known enum.

    Forcing this tool guarantees a *valid* label every time — so the difference
    between stages is purely accuracy, never malformed output.
    """
    return {
        "name": "route_ticket",
        "description": "Assign the support ticket to exactly one team.",
        "input_schema": {
            "type": "object",
            "properties": {"team": {"type": "string", "enum": names}},
            "required": ["team"],
        },
    }


def classify(text: str, system: str, names: list[str]) -> str:
    resp = get_client().messages.create(
        model=MODEL,
        max_tokens=256,
        system=system,
        messages=[{"role": "user", "content": text}],
        tools=[route_tool(names)],
        tool_choice={"type": "tool", "name": "route_ticket"},
    )
    block = next(b for b in resp.content if b.type == "tool_use")
    return block.input["team"]


def route_testset(system: str, tickets: list[dict]) -> list[dict]:
    """Classify every ticket with Claude, printing progress to stderr."""
    names = team_names()
    preds = []
    for i, t in enumerate(tickets, 1):
        pred = classify(t["text"], system, names)
        mark = "✓" if pred == t["team"] else "✗"
        print(f"  [{i:>2}/{len(tickets)}] {mark} {t['team']:<16} -> {pred}", file=sys.stderr)
        preds.append({"id": t["id"], "gold": t["team"], "pred": pred, "text": t["text"]})
    return preds


# ════════════════════════════════════════════════════════════════
# Embeddings — used by the distilled classifier (stage 2)
# ════════════════════════════════════════════════════════════════

_embed_model = None


def get_embed_model():
    global _embed_model
    if _embed_model is None:
        from sentence_transformers import SentenceTransformer
        print(f"Loading embedding model ({EMBED_MODEL})...", file=sys.stderr)
        _embed_model = SentenceTransformer(EMBED_MODEL)
    return _embed_model


def embed(texts: list[str]):
    """Return unit-normalized embedding vectors for a list of strings."""
    return get_embed_model().encode(list(texts), normalize_embeddings=True)
