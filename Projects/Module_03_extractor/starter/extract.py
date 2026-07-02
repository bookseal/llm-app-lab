"""Tools & Structure starter — extract structured data from unstructured text.

Single-turn structured output using Claude's forced tool_use pattern,
validated with Pydantic.

The starter is configured for job postings — runs cleanly on the two
`job_posting*.txt` samples and intentionally falls down on the others.
Your job is to redefine the schema, prompt, and Pydantic model to fit
a different document type (or define your own).
"""
import json
import sys
from pathlib import Path

from anthropic import Anthropic
from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError

load_dotenv()  # loads ANTHROPIC_API_KEY from .env

client = Anthropic()

# ════════════════════════════════════════════════════════════════
# TODO — replace the three blocks below to match your chosen
# document type. The defaults extract from a job posting.
# ════════════════════════════════════════════════════════════════

EXTRACT_TOOL = {
    "name": "record_job",
    "description": "Record the structured fields of a job posting.",
    "input_schema": {
        "type": "object",
        "properties": {
            "title":      {"type": "string"},
            "company":    {"type": "string"},
            "location":   {"type": "string"},
            "remote":     {"type": "boolean"},
            "salary_min": {"type": ["number", "null"]},
            "salary_max": {"type": ["number", "null"]},
            "currency":   {"type": ["string", "null"]},
        },
        "required": ["title", "company", "location", "remote"],
    },
}


class Job(BaseModel):
    title: str
    company: str
    location: str
    remote: bool
    salary_min: float | None = None
    salary_max: float | None = None
    currency: str | None = None


SYSTEM_PROMPT = """Extract the listed fields from the job posting.

Rules:
- Return null for unknown fields rather than guessing.
- Salary fields are numbers without currency symbols ($, USD, etc.).
- "remote" is true only if the role can be done fully remotely.
"""

# ════════════════════════════════════════════════════════════════


def extract(text: str) -> dict:
    """Send `text` to Claude, force the EXTRACT_TOOL, return its input dict."""
    resp = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": text}],
        tools=[EXTRACT_TOOL],
        tool_choice={"type": "tool", "name": EXTRACT_TOOL["name"]},
    )
    block = next((b for b in resp.content if b.type == "tool_use"), None)
    if block is None:
        raise ValueError("Model did not call the tool")
    return block.input


def validate(raw: dict) -> BaseModel:
    """Validate the raw dict against the Pydantic model."""
    return Job(**raw)


def main() -> int:
    docs = sorted(Path("documents").glob("*.txt"))
    if not docs:
        print("No documents found in documents/", file=sys.stderr)
        return 1

    failures = 0
    for path in docs:
        print(f"\n=== {path.name} ===")
        text = path.read_text()
        try:
            raw = extract(text)
            obj = validate(raw)
            print(json.dumps(obj.model_dump(), indent=2))
        except ValidationError as e:
            failures += 1
            print(f"VALIDATION FAILED:\n{e}", file=sys.stderr)
        except Exception as e:
            failures += 1
            print(f"EXTRACT FAILED: {e}", file=sys.stderr)

    print(f"\n{len(docs) - failures} / {len(docs)} extracted successfully")
    return 0 if failures == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
