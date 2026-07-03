# The Module 4 RAG app (Streamlit UI) for "Run it live".
#
# streamlit_app.py is a single-command web app (like the agent's REPL) — same
# retrieval as the Flask/React version, but one process on port 8501. It loads
# the prebuilt index (index.bge.pkl) and embeds queries with sentence-
# transformers (BGE), downloaded on first run.
#
# Build context = Projects/Module_04_rag/rag-starter (see .dockerignore, which
# drops .venv / node_modules / caches). ANTHROPIC_API_KEY via the k8s secret.
FROM python:3.11-slim

RUN pip install --no-cache-dir \
    flask flask-cors anthropic python-dotenv \
    "sentence-transformers>=3.0" "streamlit>=1.58"

WORKDIR /srv
COPY . /srv
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
