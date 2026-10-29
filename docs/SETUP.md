# Setup

## Requirements

- Python 3.12 and [uv](https://docs.astral.sh/uv/)
- Node 18+ (22 recommended)
- A key for Groq or OpenAI, or [Ollama](https://ollama.com) running locally

## Backend

```bash
cd backend
uv sync
cp .env.example .env        # then set APP_PASSWORD, SESSION_SECRET and LLM_API_KEY
uv run uvicorn app.main:app --reload     # http://localhost:8000/docs
```

The first upload downloads the embedding model (~70 MB) into the fastembed cache.

### Using Ollama instead

```bash
ollama pull llama3.2
```

Then in `backend/.env`: `LLM_PROVIDER=ollama` (no key needed). Set `LLM_MODEL` to use a different pulled model.

## Frontend

```bash
cd frontend
npm install
npm run dev                              # http://localhost:5173
```

Vite proxies `/api` to `localhost:8000` (override with `VITE_API_PROXY`).

## Environment variables (`backend/.env`)

| Variable | Default | Purpose |
|---|---|---|
| `APP_PASSWORD` | empty | login password. Login is disabled until set |
| `SESSION_SECRET` | insecure dev value | signs session cookies |
| `LLM_PROVIDER` | `groq` | `groq`, `openai` or `ollama` |
| `LLM_API_KEY` | empty | key for Groq or OpenAI (`GROQ_API_KEY` also works) |
| `LLM_MODEL` | per provider: `openai/gpt-oss-120b`, `gpt-4o-mini`, `llama3.2` | model name |
| `LLM_BASE_URL` | per provider | any other OpenAI-compatible endpoint |
| `MIN_SIMILARITY` | `0.55` | below this, don't answer (see DECISIONS) |
| `HIGH_SIMILARITY` | `0.7` | at or above this, label "high confidence" |
| `TOP_K` | `4` | passages retrieved per question |
| `EMBEDDINGS` | `fastembed` | `hash` is for tests only |
| `DATA_DIR` | `./data` | uploads, Chroma and the SQLite file |
| `DATABASE_URL` | `sqlite:///./data/docuchat.db` | or Postgres |
| `FRONTEND_URL` | `http://localhost:5173` | CORS origin |
| `CROSS_SITE_COOKIES` | `false` | `true` when frontend and API are on different domains |

## Checks

```bash
cd backend && uv run ruff check . && uv run pytest
cd frontend && npm test && npm run build
```

---

<div align="center">

<h3>Akshat Gupta</h3>

<a href="https://akshatgcodes.in"><img src="https://img.shields.io/badge/Website-akshatgcodes.in-111111?style=flat-square&logo=googlechrome&logoColor=white" alt="Website"></a>
<a href="https://linkedin.com/in/akshatgcodes"><img src="https://img.shields.io/badge/LinkedIn-akshatgcodes-0A66C2?style=flat-square" alt="LinkedIn"></a>
<a href="https://github.com/akshatgcodes"><img src="https://img.shields.io/badge/GitHub-akshatgcodes-181717?style=flat-square&logo=github&logoColor=white" alt="GitHub"></a>
<a href="mailto:akshatgcodes@gmail.com"><img src="https://img.shields.io/badge/Email-akshatgcodes%40gmail.com-EA4335?style=flat-square&logo=gmail&logoColor=white" alt="Email"></a>

</div>
