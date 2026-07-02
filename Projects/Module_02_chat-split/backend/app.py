from datetime import datetime, timezone

from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # allow the frontend (different origin in dev) to call this API


@app.route("/api/hello", methods=["GET"])
def hello():
    return jsonify(message="Hello from Flask")


@app.route("/api/time", methods=["GET"])
def server_time():
    # TODO(human): 현재 서버 시각을 JSON으로 반환하세요. 프론트는 t.time을 읽습니다.
    #   예) return jsonify(time=<여기에 시각 표현>)
    # 표현 방식을 직접 결정해 보세요 — 이게 이 과제의 핵심 설계 결정입니다.
    raise NotImplementedError("server_time() not implemented yet")


if __name__ == "__main__":
    # 5000 is hijacked by macOS AirPlay Receiver (AirTunes), so use 5001.
    app.run(port=5001, debug=True)
