# The Module 3 job-post extractor (the ⭐ extended webapp) for "Run it live".
#
# A plain server-rendered Flask app — it serves its own UI at "/" and has
# /api/extract + /api/draft-email. No frontend build, no ttyd needed.
#
# Build context = Projects/Module_03_extractor/webapp (so COPY . grabs app.py,
# templates/, examples). ANTHROPIC_API_KEY arrives via the k8s secret.
FROM python:3.11-slim

RUN pip install --no-cache-dir flask flask-cors anthropic python-dotenv gunicorn

WORKDIR /srv
COPY . /srv
RUN useradd -m runner && chown -R runner /srv
USER runner

EXPOSE 5001
CMD ["gunicorn", "-b", "0.0.0.0:5001", "--workers", "2", "--timeout", "120", "app:app"]
