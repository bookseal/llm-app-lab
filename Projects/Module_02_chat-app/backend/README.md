# backend

Minimal Flask server: one endpoint, `POST /api/chat`, that forwards the user's message to the Claude API and returns the reply.

## Setup

```bash
# from the project root (where .venv lives)
source .venv/bin/activate

cd backend
pip install -r requirements.txt

# add your Anthropic API key
cp .env.example .env
# then edit .env and replace the placeholder with your real key

python app.py
# Running on http://localhost:5000
```

## Endpoint

```
POST /api/chat
Content-Type: application/json
{"message": "your text here"}

→ 200 OK
{"reply": "Claude's response text"}
```
