import os

from flask import Flask, render_template, request, jsonify, send_file
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
                      "course_title": {"type": ["string", "null"]},
                      "location":     {"type": ["string", "null"]},
                      "datetime":     {"type": ["string", "null"]},
                      "pay":          {"type": ["string", "null"]},
                      "contact":      {"type": ["string", "null"]},
              },
              "required": ["course_title", "location", "datetime", "pay", "contact"],
      },
}

SYSTEM_PROMPT = """Extract the listed fields from the instructor job posting.

Fields:
- course_title: the subject or title of the class being taught
- location: the venue or address where the class is held; null if online or not stated
- datetime: when the class happens (date and/or time), copied as written
- pay: the instructor's pay/compensation, copied as written (e.g. "시급 5만원")
- contact: how to reach the organizer (email, phone, or name)

Return null for any field that is not stated, rather than guessing.
"""


@app.route("/")
def index():
	return render_template("index.html")


@app.route("/examples")
def examples():
	# example_email_text.html lives next to app.py (app.root_path), not in templates/
	return send_file(os.path.join(app.root_path, "example_email_text.html"))


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


# human-readable labels for the email (keys come from EXTRACT_TOOL)
FIELD_LABELS = {
	"course_title": "the course title or subject",
	"location": "the class location or venue",
	"datetime": "the date and time",
	"pay": "the pay or compensation",
	"contact": "the best point of contact",
}

EMAIL_SYSTEM_PROMPT = """You help an instructor named Jungmin Hong write a brief, \
polite follow-up email to a course organizer who posted an instructor job. Some \
details were missing from the posting. Write a concise, professional email that \
asks ONLY for the missing details listed by the user. Keep it warm and short, \
include a Subject line, and sign off as "Jungmin Hong". Output only the email text."""


@app.route("/api/draft-email", methods=["POST"])
def draft_email():
	data = request.json.get("data", {})
	missing = [key for key, value in data.items() if value in (None, "")]
	if not missing:
		return jsonify({"email": None, "message": "No missing fields — nothing to ask about."})

	missing_labels = [FIELD_LABELS.get(key, key) for key in missing]
	known = {k: v for k, v in data.items() if v not in (None, "")}
	user_msg = (
		"Missing details to ask about: " + ", ".join(missing_labels) + ".\n"
		"Already known: " + (", ".join(f"{k} = {v}" for k, v in known.items()) or "(nothing)") + "."
	)

	resp = client.messages.create(
		model="claude-sonnet-4-6",
		max_tokens=512,
		system=EMAIL_SYSTEM_PROMPT,
		messages=[{"role": "user", "content": user_msg}],
	)
	return jsonify({"email": resp.content[0].text})


if __name__ == "__main__":
	app.run(port=5001, debug=True)
