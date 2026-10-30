# Deploy

## Live demo

Live at **https://docuchat.akshatgcodes.in**: one free Render web service (Python runtime, Singapore), connected to this repo, so every push to `main` deploys. The free instance sleeps after 15 minutes idle and takes up to a minute to wake.

The API serves the whole site when `SITE_DIR` is set (`backend/app/site.py`): the landing page (`landing/`, a Next.js static export) at `/`, the React app at `/app/`, and the API at `/api`.

| Setting | Value |
|---|---|
| Build | `pip install uv && cd backend && uv sync --frozen --no-dev && cd ../landing && npm ci && npm run build && cd ../frontend && npm ci && VITE_BASE=/app/ npm run build` |
| Start | `cd backend && .venv/bin/uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| Health check | `/health` |

A 512 MB instance with no persistent disk changes two things (see docs/DECISIONS.md):

- **Vectors** go to Postgres with pgvector (`VECTOR_STORE=pgvector`) instead of Chroma on disk, and uploaded PDFs are stored in the database (they always are).
- **Embeddings** come from Gemini's OpenAI-compatible API instead of the local model, which peaked above 512 MB while embedding a long document.

Environment: `DATABASE_URL` (Neon), `SESSION_SECRET`, `APP_PASSWORD` (`demo1234` on the demo), `LLM_PROVIDER=groq`, `LLM_API_KEY`, `VECTOR_STORE=pgvector`, `EMBEDDINGS=openai`, `EMBEDDINGS_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/`, `EMBEDDING_MODEL=gemini-embedding-001`, `EMBEDDING_DIMENSIONS=768`, `EMBEDDINGS_API_KEY`, `MIN_SIMILARITY` and `HIGH_SIMILARITY` (calibrated for Gemini), `DATA_DIR=/tmp/docuchat`, `SITE_DIR=/opt/render/project/src`, `FRONTEND_URL`, `PYTHON_VERSION`.

## Running it elsewhere

With the defaults (Chroma in `DATA_DIR`, local embeddings), any host with a persistent disk and about 1.2 GB of memory works: `cd backend && uv run uvicorn app.main:app`, with the frontend built separately or served by the API through `SITE_DIR`.

---

<div align="center">

<h3>Akshat Gupta</h3>

<a href="https://akshatgcodes.in"><img src="https://img.shields.io/badge/Website-akshatgcodes.in-111111?style=flat-square&logo=googlechrome&logoColor=white" alt="Website"></a>
<a href="https://linkedin.com/in/akshatgcodes"><img src="https://img.shields.io/badge/LinkedIn-akshatgcodes-0A66C2?style=flat-square" alt="LinkedIn"></a>
<a href="https://github.com/akshatgcodes"><img src="https://img.shields.io/badge/GitHub-akshatgcodes-181717?style=flat-square&logo=github&logoColor=white" alt="GitHub"></a>
<a href="mailto:akshatgcodes@gmail.com"><img src="https://img.shields.io/badge/Email-akshatgcodes%40gmail.com-EA4335?style=flat-square&logo=gmail&logoColor=white" alt="Email"></a>

</div>
