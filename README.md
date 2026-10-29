<p align="center">
  <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24"
       fill="none" stroke="#2f54eb" stroke-width="1.5"
       stroke-linecap="round" stroke-linejoin="round">
    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
    <path d="M14 2v6h6"/>
    <path d="M8 13h8"/>
    <path d="M8 17h5"/>
  </svg>
</p>

<h1 align="center">DocuChat</h1>

<p align="center">
  <strong>Ask questions about a PDF. Answers cite the exact passage, highlighted on the page, or say the document doesn't cover it.</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/React-20232A?style=flat-square&logo=react&logoColor=61DAFB" alt="React">
  <img src="https://img.shields.io/badge/TypeScript-3178C6?style=flat-square&logo=typescript&logoColor=white" alt="TypeScript">
  <img src="https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/LangChain-1C3C3C?style=flat-square&logo=langchain&logoColor=white" alt="LangChain">
  <img src="https://img.shields.io/badge/ChromaDB-FF6446?style=flat-square" alt="ChromaDB">
  <img src="https://img.shields.io/badge/license-GPL--3.0-2f54eb?style=flat-square" alt="License">
</p>

---

## What is DocuChat?

Upload a PDF and ask it questions. The document is split into passages, embedded into ChromaDB, and each question retrieves the closest passages before a language model answers from them. Every claim in an answer carries a numbered citation; click it and the page opens with that passage highlighted.

The part that separates it from a basic RAG demo is **retrieval confidence**. If even the closest passage isn't similar enough to the question, DocuChat answers *"I don't have enough information in this document to answer that"* and never calls the model. When passages are related but don't contain the answer, the model is told to decline too, and the UI says which of the two happened.

---

## What you get

- **PDF upload** with drag and drop. Text is read with PyMuPDF into paragraph-sized passages that remember their position on the page.
- **Cited answers.** `[1]`, `[2]` in the answer are buttons; sources list the page and similarity score.
- **Highlighted pages.** The server renders the page as an image with the source passage marked, so there's no PDF viewer to load in the browser.
- **Confidence indicator** on every answer (high / medium / low with the best passage's similarity), and a clear explanation when it declines.
- **Chat history** per document, kept across reloads.
- **Any OpenAI-compatible model:** Groq (default), OpenAI, or a local Ollama model, chosen in `.env`.
- **Local embeddings** (`BAAI/bge-small-en-v1.5` via fastembed): no embedding API, same scores every run.

---

## Stack

| Layer | Tech |
|---|---|
| Frontend | React 19 · TypeScript · Vite · React Router |
| Backend | FastAPI · LangChain (splitter, Chroma store, ChatOpenAI) · PyMuPDF |
| Retrieval | ChromaDB (cosine) · fastembed `bge-small-en-v1.5` |
| Generation | Groq / OpenAI / Ollama through the OpenAI-compatible API |
| Storage | SQLite (or Postgres) for documents, passages and chat; files on disk |
| Tooling | uv · pytest · Vitest · ruff · GitHub Actions |

---

## Run it

```bash
# API → http://localhost:8000/docs
cd backend && uv sync && cp .env.example .env    # set APP_PASSWORD and LLM_API_KEY
uv run uvicorn app.main:app --reload

# App → http://localhost:5173
cd frontend && npm install && npm run dev
```

The first upload downloads the embedding model (about 70 MB). Details, including Ollama, in [docs/SETUP.md](docs/SETUP.md).

---

## Engineering Decisions

**How was the threshold chosen?**
By measuring. On a 15-page paper, questions it answers scored 0.62–0.82 against their best passage and unrelated questions scored 0.44–0.59. The default cut-off is 0.55. The ranges overlap, so the threshold alone can't be perfect, which is why there's a second guard in the prompt. The table is in [docs/DECISIONS.md](docs/DECISIONS.md).

**Why chunk by PDF blocks instead of fixed-size text windows?**
A passage made of whole blocks on one page has exact coordinates, so the source can be highlighted precisely. Passages also stop at headings so they don't span two sections. Only blocks longer than a passage go through LangChain's text splitter.

**Why local embeddings with a hosted model for answers?**
Embeddings run on every passage and every question, and the confidence threshold depends on their scores staying stable. A small local model makes that free and repeatable. Answer quality is where a large model matters, so that part is hosted and swappable.

**What would you do differently in v2?**
Rewrite follow-up questions into standalone ones before retrieval (today each question is answered on its own), add OCR for scanned PDFs, and calibrate the threshold per document from its own score distribution.

More in [docs/DECISIONS.md](docs/DECISIONS.md).

---

## Docs

| Document | Description |
|---|---|
| [PRD](docs/PRD.md) | Product requirements: goals, user stories, non-goals |
| [Architecture](docs/ARCHITECTURE.md) | Pipeline, data model, API |
| [Decisions](docs/DECISIONS.md) | Every major technical decision and why |
| [Setup](docs/SETUP.md) | Local dev setup and env vars |
| [Deploy](docs/DEPLOY.md) | Deployment notes |
| [Contributing](CONTRIBUTING.md) | How to propose changes |
| [Changelog](CHANGELOG.md) | What changed in each release |
| [Security](SECURITY.md) | How to report a vulnerability |

---

<div align="center">

<h3>Akshat Gupta</h3>

<a href="https://akshatgcodes.in"><img src="https://img.shields.io/badge/Website-akshatgcodes.in-111111?style=flat-square&logo=googlechrome&logoColor=white" alt="Website"></a>
<a href="https://linkedin.com/in/akshatgcodes"><img src="https://img.shields.io/badge/LinkedIn-akshatgcodes-0A66C2?style=flat-square" alt="LinkedIn"></a>
<a href="https://github.com/akshatgcodes"><img src="https://img.shields.io/badge/GitHub-akshatgcodes-181717?style=flat-square&logo=github&logoColor=white" alt="GitHub"></a>
<a href="mailto:akshatgcodes@gmail.com"><img src="https://img.shields.io/badge/Email-akshatgcodes%40gmail.com-EA4335?style=flat-square&logo=gmail&logoColor=white" alt="Email"></a>

</div>
