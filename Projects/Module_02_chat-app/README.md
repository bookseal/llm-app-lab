# Foundations — Bare-bones Chat App

A minimal Claude-powered chat application. React frontend + Flask backend, deliberately the smallest thing that talks to the API.

## What's in it

```
chat-app/
├── backend/
│   ├── app.py             one endpoint, one Claude call
│   ├── requirements.txt
│   └── .env.example       template for your ANTHROPIC_API_KEY
└── frontend/
    ├── src/App.jsx        chat UI, sends and renders messages
    ├── vite.config.js     proxies /api/* to :5000
    └── package.json
```

## Run

```bash
# from this directory:
python3.11 -m venv .venv
source .venv/bin/activate

# terminal 1 — backend
cd backend
pip install -r requirements.txt
cp .env.example .env
# edit .env and put your real ANTHROPIC_API_KEY in
python app.py

# terminal 2 — frontend
cd frontend
npm install
npm run dev
```

Open <http://localhost:5173>, send a message, watch Claude respond.

## Track your fixes with git

Make this directory a local git repo so each fix you make becomes its own commit. Git works completely locally — no remote, no GitHub account needed.

```bash
cd chat-app
git init && git add . && git commit -m "starter"
```

After each fix you accept from Claude Code:

```bash
git commit -am "fix: <what you fixed>"
```

To walk through your changes:
- **VSCode's Source Control panel** (branch icon in the left rail) gives a visual side-by-side diff.
- `git log --oneline` + `git show <hash>` in a terminal steps through fix-by-fix.

## What's missing on purpose

This is intentionally bare. The exercise here is to read the code, run it, and identify what a production version would need to add. You'll find at least five things missing — each one maps to a topic later in the week.
