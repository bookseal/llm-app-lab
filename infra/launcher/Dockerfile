# The launcher API: Flask + the kubectl binary it shells out to.
FROM python:3.11-slim

ARG KUBECTL_VERSION=v1.30.0
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && curl -fsSLo /usr/local/bin/kubectl \
       "https://dl.k8s.io/release/${KUBECTL_VERSION}/bin/linux/$(dpkg --print-architecture)/kubectl" \
    && chmod +x /usr/local/bin/kubectl \
    && apt-get purge -y curl && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir flask gunicorn

WORKDIR /srv
COPY app.py .

# in-cluster: kubectl picks up the ServiceAccount token automatically
EXPOSE 8080
CMD ["gunicorn", "-b", "0.0.0.0:8080", "--workers", "1", "--threads", "8", "app:app"]
