# Backend (Flask)

A single-file Flask API exposing one endpoint.

## Install

From the **project root**, create and activate a virtual environment, then install
the dependencies:

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r backend/requirements.txt
```

## Run

With the `.venv` active:

```bash
python backend/app.py
```

The server listens on **http://localhost:5001**.

> macOS의 AirPlay Receiver가 포트 5000(과 7000)을 점유하므로 5001을 씁니다.
> 5000을 쓰고 싶다면 시스템 설정 → 일반 → AirDrop 및 Handoff에서
> "AirPlay 수신 모드"를 끄세요.

## Endpoint

| Method | Path         | Response                          |
| ------ | ------------ | --------------------------------- |
| GET    | `/api/hello` | `{"message": "Hello from Flask"}` |
