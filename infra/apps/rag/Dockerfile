# The Module 4 RAG app (Streamlit UI) for "Run it live".
#
# streamlit_app.py is a single-command web app (like the agent's REPL) — same
# retrieval as the Flask/React version, but one process on port 8501. It loads
# the prebuilt index (index.bge.pkl) and embeds queries with sentence-
# transformers (BGE), downloaded on first run.
#
# Build context = Projects/Module_04_rag  (NOT rag-starter): the app imports the
# shared `harness` package, a SIBLING of rag-starter one level up. indexer.py
# runs `sys.path.insert(0, Path(__file__).resolve().parent.parent)` to reach it,
# so the container must MIRROR the repo layout — indexer.py in a subdir whose
# parent holds harness/. See Projects/Module_04_rag/.dockerignore for exclusions.
# ANTHROPIC_API_KEY via the k8s secret.
#
#   docker build -f infra/apps/rag/Dockerfile -t llm-app-lab/app-rag:v1 \
#                Projects/Module_04_rag
FROM python:3.11-slim

RUN pip install --no-cache-dir \
    flask flask-cors anthropic python-dotenv \
    "sentence-transformers>=3.0" "streamlit>=1.58" \
    rank-bm25           # harness/retrieval.py — BM25 half of the hybrid retrieve

# Mirror the repo layout EXACTLY — the imports point both ways:
#   indexer.py       → parent.parent  reaches harness/   (needs harness/ one up)
#   harness/retrieval.py → parent.parent/"rag-starter"  imports indexer
# so the sibling must keep the name `rag-starter`, not a renamed dir.
#   /srv/rag-starter/indexer.py  ↔  /srv/harness/  as siblings under /srv.
COPY harness/     /srv/harness/
COPY rag-starter/ /srv/rag-starter/
WORKDIR /srv/rag-starter

RUN useradd -m runner && mkdir -p /home/runner/.cache && chown -R runner /srv /home/runner
USER runner

# headless server; the embedding model caches under the runner home on first use
ENV STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_BROWSER_GATHERUSAGESTATS=false \
    HF_HOME=/home/runner/.cache/huggingface

EXPOSE 8501
CMD ["streamlit", "run", "streamlit_app.py", \
     "--server.port=8501", "--server.address=0.0.0.0", \
     "--server.fileWatcherType=none"]
