# infra/ — the "Run it live" launcher

The docs pages carry a `▶ Run it live` button (`docs/run.js`). A static page
cannot start a server, so the button talks to a tiny **launcher API** that
scales k8s deployments **0 ↔ 1 on demand** and reports when they are ready.
Full principle write-up (with diagrams): `docs/launcher.html`.

```
browser (docs page)              launcher (Flask, this dir)          k3s
POST /launch {"app":"agent"} ──► kubectl scale --replicas=1  ──►  pod starts
GET  /status/agent  (poll)   ──► deployment readyReplicas?
                             ◄── {"state":"ready","url":"https://agent.bit-habit.com"}
…idle 20 min…                    kubectl scale --replicas=0  ──►  pod gone
```

The agent app itself is a terminal REPL, so its container serves the **real
terminal** over the web with [ttyd](https://github.com/tsl0922/ttyd) — the
browser gets the exact session a student gets locally.

## Layout

| Path | What |
|---|---|
| `launcher/app.py` | the API: `/launch`, `/status/<app>`, idle reaper, app allowlist |
| `launcher/Dockerfile` | Flask + kubectl |
| `apps/agent/Dockerfile` | ttyd + the published `agent-app.zip` (live demo ≡ classroom artifact) |
| `k8s.yaml` | namespace, RBAC (launcher may only scale this namespace), deployments, services, ingresses |

## Deploy (on the bit-habit server)

```bash
# 0) sanity: confirm the cluster's TLS convention first and adjust k8s.yaml
kubectl get ingress -A          # copy the existing tls.secretName / annotations

# 1) build the images on the node (k3s uses containerd, no docker registry needed)
cd llm-app-lab/infra
docker build -t llm-app-lab/launcher:v1 launcher/
docker build -t llm-app-lab/app-agent:v1 apps/agent/
docker save llm-app-lab/launcher:v1  | sudo k3s ctr images import -
docker save llm-app-lab/app-agent:v1 | sudo k3s ctr images import -

# 2) secret + manifests
kubectl create ns llm-app-lab --dry-run=client -o yaml | kubectl apply -f -
kubectl -n llm-app-lab create secret generic anthropic \
  --from-literal=ANTHROPIC_API_KEY=sk-ant-…
kubectl apply -f k8s.yaml

# 3) smoke-test the contract run.js expects
curl -s -X POST https://launch.bit-habit.com/launch \
  -H 'Content-Type: application/json' -d '{"app":"agent"}'
curl -s https://launch.bit-habit.com/status/agent   # …repeat until "ready"
open https://agent.bit-habit.com                     # the live terminal
```

## Wire the button

Once the smoke test passes, set in `docs/run.js`:

```js
const LAUNCHER_BASE = "https://launch.bit-habit.com";
```

and bump `run.js?v=` on the pages. The button then goes
**클릭 → ⏳ Starting… → ✅ Ready**, embeds the app in an iframe right inside
the page, and the reaper shuts the pod down after 20 idle minutes.

## Security posture

- The launcher's ServiceAccount can **only get/scale deployments in the
  `llm-app-lab` namespace** (Role in `k8s.yaml`) — it cannot create pods, read
  secrets, or touch other namespaces.
- `/launch` accepts only allowlisted app names hard-coded in `app.py`.
- The agent container runs unprivileged; its tools are read-only by
  construction (`run_query` = SELECT-only, `mode=ro` SQLite — see 5D).
- CORS is pinned to `https://llm-app-lab.bit-habit.com`.
