# The 5D data-analyst agent for "Run it live".
#
# The app is a terminal REPL (python agent.py) — no web UI of its own. Instead
# of writing a wrapper that would drift from the classroom artifact, we serve
# the REAL terminal over the web with ttyd: the browser (or the docs page's
# iframe) gets the exact same session a student gets locally.
#
# Built from the same starter zip students download, so live demo ≡ artifact.
FROM python:3.11-slim

ARG TTYD_VERSION=1.7.7
RUN apt-get update && apt-get install -y --no-install-recommends curl unzip \
    && ARCH=$(dpkg --print-architecture | sed 's/amd64/x86_64/; s/arm64/aarch64/') \
    && curl -fsSLo /usr/local/bin/ttyd \
       "https://github.com/tsl0922/ttyd/releases/download/${TTYD_VERSION}/ttyd.${ARCH}" \
    && chmod +x /usr/local/bin/ttyd \
    && curl -fsSLo /tmp/agent-app.zip "https://ksetp.netlify.app/assets/agents/agent-app.zip" \
    && unzip /tmp/agent-app.zip -d /srv && rm /tmp/agent-app.zip \
    && apt-get purge -y curl unzip && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /srv/agent-app
RUN pip install --no-cache-dir -r requirements.txt

# unprivileged: the tools are read-only by construction, keep the pod that way too
RUN useradd -m runner && chown -R runner /srv/agent-app
USER runner

# ANTHROPIC_API_KEY arrives via the k8s secret (see ../../k8s.yaml).
# -W writable terminal · respawns the REPL when a session ends.
EXPOSE 7681
CMD ["ttyd", "-W", "-p", "7681", "python", "agent.py"]
