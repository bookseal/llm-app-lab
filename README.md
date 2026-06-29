# llm-app-lab

**KSEPT Summer Program — Building with LLMs** 실습 저장소.
LLM API 한 줄 호출에서 시작해 도구 사용·RAG·에이전트·프로덕션까지, LLM 애플리케이션을
직접 만들며 배우는 핸즈온 랩입니다.

> 📚 **학습 사이트 (GitHub Pages): <https://bookseal.github.io/llm-app-lab/>**
> 한글 개념 노트 + Mermaid 다이어그램 + 모듈별 미니 퀴즈. 원본 슬라이드
> ([ksetp.netlify.app](https://ksetp.netlify.app/))를 *작동 원리* 중심으로 다시 정리했습니다.
>
> 📑 **전체 커리큘럼 한 파일:** [TUTORIAL.md](TUTORIAL.md) — 7개 모듈 전문(코드 포함).

## 이 저장소의 구성

```
.
├── backend/      Flask API (GET /api/hello)          — 풀스택 hello-world
├── frontend/     React + Vite 앱 (mount 시 fetch)     — 풀스택 hello-world
├── docs/         학습 사이트 소스 (GitHub Pages로 서빙)
├── scripts/      docs 자동 생성 스크립트
├── .github/      Pages 빌드 워크플로
└── TUTORIAL.md   커리큘럼 전문 레퍼런스
```

루트의 `backend/` + `frontend/`는 Module 2의 출발점인 풀스택 hello-world이고,
모듈별 예제 앱(chat-app, rag-starter, agent-app 등)은 각자 스타터 zip으로 받아 실습합니다.

## 이걸 어떻게 공부하면 좋은가

### 1. 순서대로 한 모듈씩

학습 사이트의 [개념 지도](https://bookseal.github.io/llm-app-lab/)를 목차 삼아, 각 모듈을
**개념 노트(docs) → 원본 슬라이드 → 스타터 앱 실습 → 미니 퀴즈** 순으로 통과합니다.

| # | 모듈 | 한 줄 |
|---|------|------|
| 1 | Setup | 도구 6종 설치 + 공유 `.env`에 API 키 한 번 저장 |
| 2 | Foundations | 첫 API 호출, 챗 앱, **결함 5종 직접 수정**, SSE 스트리밍 |
| 3 | Tools & Structure | 출력 구조화 4단계: parseable → schema → tool-loop → MCP |
| 4 | Context | 인덱싱 파이프라인 + RAG(청킹·임베딩·벡터 스토어·인용) |
| 5 | Architecture & Agents | ~20줄 agent loop, subagents, memory scope, 멀티모델 |
| 6 | Production | eval 사다리, prompt injection 방어, observability |
| 7 | Workshop | 끝낼 수 있을 만큼 작은 걸 직접 빌드 |

### 2. 이 코스가 가르치는 "학습 루프"

각 모듈의 스타터는 **일부러 결함이 있는** 코드예요. 핵심은 답을 받아 적는 게 아니라
다음 루프를 도는 것입니다:

1. **재현** — 결함을 직접 눈으로 본다 (예: 봇이 이전 대화를 기억 못 함).
2. **진단** — *왜* 그런지 메커니즘을 설명할 수 있을 때까지 판다.
3. **수정** — Claude Code엔 구현이 아니라 *원하는 동작*을 말하고, 먼저 계획을 물어본다.
4. **diff 읽기** — 수락 전에 무엇이 바뀌는지 읽고 이해한다.
5. **검증** — 1번의 실패 시나리오를 다시 돌려 고쳐졌는지 확인한다.
6. **커밋** — `git commit -am "fix: <결함>"`. 수정 하나당 커밋 하나.

→ 그러면 `git log`가 곧 **당신의 학습 일지**가 됩니다. 발표할 땐 `git show <hash>`로
커밋을 하나씩 "걸으며"(walk the diff) 각 수정을 설명하면 돼요.

### 3. 막히면

- 개념이 안 잡히면 → 학습 사이트의 해당 모듈 노트(비유 우선 + Mermaid)부터.
- "서버는 떴는데 안 된다" 류 → 프로세스 기동 로그가 아니라 **엔드포인트에 실제 요청**을
  쏴서 상태코드와 응답 본문으로 판정 (`curl -i ...`).

## 로컬에서 실행 (풀스택 hello-world)

서버가 두 개라 **터미널 2개**가 필요합니다.

### Terminal 1 — backend

```bash
python -m venv .venv          # first time only
source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r backend/requirements.txt
python backend/app.py         # serves on http://localhost:5001
```

### Terminal 2 — frontend

```bash
cd frontend
npm install                   # first time only
npm run dev                   # serves on http://localhost:5173
```

**http://localhost:5173** 을 열면 페이지가 `/api/hello`(Flask로 프록시)를 호출해
`Hello from Flask`를 표시합니다.

자세한 내용은 [backend/README.md](backend/README.md), [frontend/README.md](frontend/README.md) 참고.

## 학습 사이트 & 변경 이력 (GitHub Pages)

[`docs/`](docs/) 폴더가 **<https://bookseal.github.io/llm-app-lab/>** 로 서빙됩니다.

- **개념 지도** (`docs/index.html`): 모듈별 노트(setup · foundations · chat-app ·
  tools · context · agents · production · workshop)로 이어지는 멀티페이지 학습 사이트.
  한글 설명 + 영어 Mermaid 다이어그램 + 즉시 채점 미니 퀴즈.
- **변경 이력** (`docs/history.html`): `main`에 push할 때마다 GitHub Actions가
  `git log`를 읽어 자동 생성합니다 ([scripts/gen_history.py](scripts/gen_history.py),
  워크플로는 [.github/workflows/pages.yml](.github/workflows/pages.yml)).

로컬에서 이력 페이지를 미리 보려면:

```bash
python3 scripts/gen_history.py   # docs/history.html 생성 (git 저장소 안에서)
```
