# Tools & Structure Project — Extract structured data from unstructured text

A starter app for the Tools & Structure project. Single-turn structured output using Claude's forced `tool_use` pattern, with Pydantic validation.

## Setup

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# edit .env and set ANTHROPIC_API_KEY
```

## Run

```bash
python extract.py
```

The starter is configured for **job postings** — it will extract cleanly from `job_posting.txt` and `job_posting_2.txt`, and fail (in interesting ways) on `meeting_notes.txt`, `recipe.txt`, and `email.txt`.

## Your job

1. **Choose a target document type.** Pick one of the non-job samples, or write your own (drop a `.txt` into `documents/`).
2. **Replace the three TODO blocks in `extract.py`:**
   - `EXTRACT_TOOL` — JSON schema for the fields you want
   - `Job` Pydantic model — same fields as the schema, with types
   - `SYSTEM_PROMPT` — instruction to the model
3. **Add at least one explicit rule** in the system prompt that handles a failure you observed.
4. **Run against the matching samples.** Iterate until you have one case that works cleanly and one that breaks cleanly.

## What to present

- Your schema (3–5 sentences on why those fields)
- Your system prompt
- One document that extracted cleanly, one that broke
- What you changed (prompt rule? schema field? validation?) to make the failure more manageable

**The failures are where you learn how this pattern actually works.**

## Alternative project

Propose your own structured-extraction use case. Anything where unstructured text in → typed object out works as the project frame. Common picks: receipts → line items + total, customer reviews → sentiment + tags + key phrases, calendar invites → event objects.
