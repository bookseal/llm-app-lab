"""Bare-bones Claude-powered chat backend.

Intentionally minimal — see the README for what's missing.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()  # picks up ANTHROPIC_API_KEY from .env

app = Flask(__name__)
CORS(app)
client = Anthropic()  # reads ANTHROPIC_API_KEY from the env


@app.route("/api/chat", methods=["POST"])
def chat():
    user_message = request.json["message"]

    resp = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        system="You are a helpful assistant. Keep replies brief.",
        messages=[{"role": "user", "content": user_message}],
    )

    return jsonify({"reply": resp.content[0].text})


if __name__ == "__main__":
    app.run(port=5001, debug=True)
