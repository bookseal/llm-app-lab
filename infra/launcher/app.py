"""The LAUNCHER — the missing half of the docs' "Run it live" button.

A static HTML page can't start a server process. So the button on each project
page talks to THIS tiny API, which turns k8s deployments on and off:

    browser (docs page)                 launcher (this app)            k3s
    POST /launch {"app":"agent"}  ───►  kubectl scale --replicas=1 ──► pod starts
    GET  /status/agent  (poll)    ───►  deployment ready?        ───►  readyReplicas
                                  ◄───  {"state":"ready","url":…}
    …idle for IDLE_MINUTES…             kubectl scale --replicas=0 ──► pod gone

v1 keeps it deliberately simple: ONE long-lived Deployment per app that scales
0 ↔ 1 (scale-to-zero on demand), not a throwaway pod per click. One shared
instance is plenty for a classroom, and the contract in docs/run.js
(/launch + /status polling) is honored exactly.

Runs inside the cluster with a ServiceAccount that may only get/scale the
deployments named in APPS (see rbac in k8s.yaml).
"""
import json
import subprocess
import threading
import time

from flask import Flask, jsonify, request

app = Flask(__name__)

# ── the only apps this launcher will ever touch (allowlist, not a parameter) ──
APPS = {
    "agent": {
        "deployment": "app-agent",
        "namespace": "llm-app-lab",
        "url": "https://agent.bit-habit.com",
    },
}
IDLE_MINUTES = 20          # scale back to 0 this long after the last /launch
ALLOWED_ORIGIN = "https://llm-app-lab.bit-habit.com"

last_launch: dict[str, float] = {}   # app name → unix time of last /launch


def kubectl(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["kubectl", *args], capture_output=True, text=True, timeout=20)


def scale(cfg: dict, replicas: int) -> bool:
    r = kubectl("scale", f"deploy/{cfg['deployment']}", f"--replicas={replicas}",
                "-n", cfg["namespace"])
    return r.returncode == 0


def ready_replicas(cfg: dict) -> int:
    r = kubectl("get", f"deploy/{cfg['deployment']}", "-n", cfg["namespace"], "-o", "json")
    if r.returncode != 0:
        return -1
    return json.loads(r.stdout).get("status", {}).get("readyReplicas") or 0


@app.after_request
def cors(resp):
    resp.headers["Access-Control-Allow-Origin"] = ALLOWED_ORIGIN
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return resp


@app.route("/launch", methods=["POST", "OPTIONS"])
def launch():
    if request.method == "OPTIONS":
        return "", 204
    name = (request.get_json(silent=True) or {}).get("app", "")
    cfg = APPS.get(name)
    if not cfg:
        return jsonify(state="error", message=f"unknown app {name!r}"), 404
    last_launch[name] = time.time()
    if ready_replicas(cfg) >= 1:                      # already warm → instant
        return jsonify(id=name, state="ready", url=cfg["url"])
    if not scale(cfg, 1):
        return jsonify(state="error", message="could not scale up"), 500
    return jsonify(id=name, state="starting")


@app.route("/status/<name>")
def status(name: str):
    cfg = APPS.get(name)
    if not cfg:
        return jsonify(state="error", message=f"unknown app {name!r}"), 404
    n = ready_replicas(cfg)
    if n < 0:
        return jsonify(state="error", message="could not read deployment")
    if n >= 1:
        return jsonify(state="ready", url=cfg["url"])
    return jsonify(state="starting")


@app.route("/healthz")
def healthz():
    return "ok"


def reaper():
    """Scale idle apps back to zero — 'it shuts down when idle'."""
    while True:
        time.sleep(60)
        now = time.time()
        for name, cfg in APPS.items():
            ts = last_launch.get(name)
            if ts and now - ts > IDLE_MINUTES * 60:
                if ready_replicas(cfg) >= 1:
                    scale(cfg, 0)
                last_launch.pop(name, None)


threading.Thread(target=reaper, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
