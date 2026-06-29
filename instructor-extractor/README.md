# instructor-extractor

Module 3(Tools & Structure)의 `extract-starter`를 실제 웹앱으로 확장한 예제.
강사 구인 글(이메일·카톡 복붙)을 붙여넣으면 구조화 필드로 추출하고, 빈 필드는 ⚠️ 누락으로
표시하며, 누락 정보를 되묻는 follow-up 이메일 초안까지 Claude가 작성합니다.

![데모](../docs/assets/instructor-extractor.png)

## 기능

- **추출** (`/api/extract`) — forced `tool_use`로 자유 텍스트를 구조화 필드로
  (`course_title` · `location` · `datetime` · `pay` · `contact`, 전부 nullable).
- **누락 표시** — null 필드는 화면에서 ⚠️ missing으로 강조.
- **스프레드시트 복사** — 값들을 TSV 한 줄로 클립보드에 복사(누락은 빈 셀).
- **follow-up 이메일** (`/api/draft-email`) — 백엔드가 누락 필드를 판단해, 그것만
  정중히 되묻는 영어 이메일을 자유 텍스트로 생성(서명 Jungmin Hong). 누락 없으면 버튼 비활성.
- **예시 페이지** (`/examples`) — 붙여넣기용 샘플 텍스트 10종(카드별 복사).

## 실행

```bash
# 저장소 루트의 venv 사용 (python 3.10+ 필요)
cp ../extract-starter/.env .env        # 또는 .env.example 복사 후 ANTHROPIC_API_KEY 입력
../.venv/bin/pip install -r requirements.txt
../.venv/bin/python app.py             # http://localhost:5001
```

브라우저에서 **http://localhost:5001** 접속 → 텍스트 붙여넣고 [Extract].

## 구조

```
instructor-extractor/
├── app.py                    Flask 서버 (추출 + 이메일 + 예시 라우트)
├── requirements.txt          flask, flask-cors, anthropic, python-dotenv
├── .env.example              ANTHROPIC_API_KEY=... 양식 (.env는 gitignore)
├── example_email_text.html   붙여넣기용 샘플 10종
└── templates/
    └── index.html            UI (textarea + 결과 + 이메일 박스)
```

## 두 방향의 LLM 사용

- **추출** = 글 → 데이터: 출력이 기계가 읽을 구조라 `tool_choice`로 **양식을 강제**.
- **이메일** = 데이터 → 글: 출력이 사람이 읽을 문장이라 **자유 텍스트**(tool 미사용).

출력이 무엇이냐에 따라 tool 강제 여부가 갈린다 — 이 대비가 이 예제의 핵심 학습 포인트.
