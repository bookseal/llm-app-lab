from flask import Flask, render_template, request, jsonify
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()  # load ANTHROPIC_API_KEY from .env

app = Flask(__name__)
app.json.ensure_ascii = False  # output non-ASCII chars as-is instead of \uXXXX
client = Anthropic()  # reads ANTHROPIC_API_KEY from the environment

# Stage 3: start the tool with a SINGLE field (location).
# Grow it one field at a time so failures stay easy to trace.
EXTRACT_TOOL = {
	"name": "record_posting",
	"description": "Record the structured fields of an instructor job posting.",
	"input_schema": {
		"type": "object",
		"properties": {
			"location": {"type": ["string", "null"]},
		},
		"required": ["location"],
	},
}

SYSTEM_PROMPT = """Extract the listed fields from the instructor job posting.
Return null for any field that is not stated, rather than guessing."""


@app.route("/")
def index():
	return render_template("index.html")


@app.route("/api/extract", methods=["POST"])
def extract():
	text = request.json.get("text", "")

	resp = client.messages.create(
		model="claude-sonnet-4-6",
		max_tokens=1024,
		system=SYSTEM_PROMPT,
		messages=[{"role": "user", "content": text}],
		tools=[EXTRACT_TOOL],
		tool_choice={"type": "tool", "name": EXTRACT_TOOL["name"]},
	)

	block = next((b for b in resp.content if b.type == "tool_use"), None)
	if block is None:
		return jsonify({"error": "Model did not call the tool"}), 500

	return jsonify(block.input)


if __name__ == "__main__":
	app.run(port=5001, debug=True)
