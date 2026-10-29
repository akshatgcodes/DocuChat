# Architecture

```
Upload                                     Ask
──────                                     ───
PDF bytes                                  question
  │ pdf.open_pdf (checks: %PDF, password)    │ store.search(doc, q, k=4)      ── Chroma, cosine, filter document_id
  │ pdf.passages: blocks → passages          │ similarity = 1 - distance
  │   (one page, stop at headings,           │ best < MIN_SIMILARITY ? ──yes──▶ "not enough information" (no LLM call)
  │    long blocks → text splitter)          │        no
  │ SQLite: documents, chunks (+ rects)      │ prompt: numbered excerpts above the threshold
  │ Chroma: one vector per chunk             │ ChatOpenAI (Groq / OpenAI / Ollama)
  │ disk:   data/uploads/<id>.pdf            │ reply == NOT_IN_DOCUMENT ? ──yes──▶ "not enough information"
  ▼                                          │        no
ready to ask                                 ▼ answer + [n] citations → marked on sources, saved as a message
```

## Backend

| File | Role |
|---|---|
| `app/pdf.py` | Open and validate PDFs, build passages with block rectangles, render a page PNG with highlights |
| `app/embeddings.py` | fastembed wrapper (LangChain `Embeddings`), plus a hashing stand-in for tests |
| `app/store.py` | LangChain `Chroma` store: add, search (with similarity), delete |
| `app/rag.py` | Confidence gate, prompt, model call, decline detection, citation parsing |
| `app/routers/documents.py` | Upload, list, delete, page images, ask, history |
| `app/models.py` | `Document`, `Chunk` (page, text, rects), `Message` (question + full result) |

### API

| Method | Path | |
|---|---|---|
| POST | `/api/auth/login`, `/api/auth/logout` · GET `/api/auth/me` | session |
| GET / POST | `/api/documents` | list / upload (multipart `file`) |
| GET / DELETE | `/api/documents/{id}` | details / delete with vectors and file |
| GET | `/api/documents/{id}/pages/{page}.png?chunk={chunk_id}` | page image, chunk highlighted |
| POST | `/api/documents/{id}/ask` | `{question}` → answer |
| GET / DELETE | `/api/documents/{id}/messages` | history / clear |

### `/ask` response

```json
{
  "id": 7,
  "question": "What optimizer was used?",
  "answer": "They used Adam with β1 = 0.9 and β2 = 0.98 [1].",
  "answerable": true,
  "reason": "answered",
  "confidence": {"level": "high", "score": 0.813, "threshold": 0.55},
  "sources": [
    {"n": 1, "chunk_id": 412, "page": 6, "score": 0.813, "text": "We used the Adam optimizer…", "used": true, "cited": true}
  ]
}
```

`reason` is `answered`, `low_similarity` (gate closed, no model call) or `model_declined`. `used` marks passages that were above the threshold and sent to the model; `cited` marks the ones the answer referenced.

## Frontend

| File | Role |
|---|---|
| `src/pages/Library.tsx` | Drop zone and document list |
| `src/pages/Chat.tsx` | Thread, composer, and which source is shown |
| `src/components/MessageView.tsx` | Answer with clickable citations, confidence bar, sources |
| `src/components/PageViewer.tsx` | Server-rendered page image with page navigation |
| `src/lib/answer.ts` | Splits answer text into text and citation segments (tested) |

On narrow screens the page viewer slides up over the chat.

---

<div align="center">

<h3>Akshat Gupta</h3>

<a href="https://akshatgcodes.in"><img src="https://img.shields.io/badge/Website-akshatgcodes.in-111111?style=flat-square&logo=googlechrome&logoColor=white" alt="Website"></a>
<a href="https://linkedin.com/in/akshatgcodes"><img src="https://img.shields.io/badge/LinkedIn-akshatgcodes-0A66C2?style=flat-square" alt="LinkedIn"></a>
<a href="https://github.com/akshatgcodes"><img src="https://img.shields.io/badge/GitHub-akshatgcodes-181717?style=flat-square&logo=github&logoColor=white" alt="GitHub"></a>
<a href="mailto:akshatgcodes@gmail.com"><img src="https://img.shields.io/badge/Email-akshatgcodes%40gmail.com-EA4335?style=flat-square&logo=gmail&logoColor=white" alt="Email"></a>

</div>
