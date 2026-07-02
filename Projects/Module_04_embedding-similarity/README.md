# Embedding playground — cosine similarity

A tiny console app to build intuition for what embeddings measure: type two
phrases, get their **cosine similarity**. It uses a local **multilingual**
sentence-transformers model (`paraphrase-multilingual-MiniLM-L12-v2`), so the
two phrases can even be in different languages. No API key needed.

## Setup

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

First run downloads the embedding model (~470 MB), one-time.

## Run

Interactive:

```bash
python similarity.py
# phrase 1 › a dog runs in the park
# phrase 2 › a puppy sprints across the grass
# cosine similarity: 0.541
```

One-shot:

```bash
python similarity.py "cat" "고양이"
```

## What to notice

Cosine similarity ranges from -1 to 1: near-identical meaning scores high,
related ideas land in the middle, unrelated phrases hover near 0. Try:

- *"king"* vs *"queen"* (related)
- *"I love this"* vs *"I hate this"* (opposite sentiment, same topic — note it's **not** near -1)
- A sentence vs its translation in another language (the multilingual model scores these high — an English-only model like the one in `rag-starter` would score ~0)
