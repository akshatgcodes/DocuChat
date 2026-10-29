# Decisions

### 1. A similarity threshold decides whether to answer at all
**Context:** Retrieval always returns the k closest passages, even for questions the document never mentions. Given those, a model will often produce a plausible answer.
**Decision:** If the best passage's cosine similarity is below `MIN_SIMILARITY`, return "not enough information" without calling the model. Only passages above the threshold go into the prompt.
**Why:** It's cheap, deterministic, and stops the most common hallucination: answering an off-topic question from loosely related text.

#### Calibration

Measured with `bge-small-en-v1.5` on *Attention Is All You Need* (15 pages, 70 passages), best-passage similarity:

| Question | Score | |
|---|---|---|
| How many layers does the encoder have? | 0.817 | in document |
| What BLEU score did the big model get on English-to-German? | 0.815 | in document |
| What optimizer was used for training? | 0.813 | in document |
| Why use self-attention instead of recurrence? | 0.786 | in document |
| What is multi-head attention? | 0.769 | in document |
| What is the dropout rate? | 0.620 | in document |
| How do vaccines train the immune system? | 0.593 | not in document |
| What is the price of Bitcoin? | 0.581 | not in document |
| How does photosynthesis work? | 0.530 | not in document |
| Who won the 2018 FIFA World Cup? | 0.480 | not in document |
| What is the capital of Australia? | 0.457 | not in document |
| How do I bake sourdough bread? | 0.444 | not in document |

The default is **0.55**: every in-document question passes, and four of six unrelated ones are stopped before generation. The two that get through are handled by decision 2. `HIGH_SIMILARITY` (0.70) only affects the label shown.
**Trade-off:** The numbers are for one model and one document. A different embedding model needs re-measuring, and dense documents may need a different cut-off; it's an environment variable for that reason.

### 2. The model is also allowed to decline
**Decision:** The system prompt says to use only the excerpts, cite them, and reply exactly `NOT_IN_DOCUMENT` when they don't contain the answer. That reply becomes "not enough information" with reason `model_declined`.
**Why:** Similarity measures topic, not whether the specific fact is there ("What colour is the logo?" scores well against passages about the model). The model catches that case; the threshold catches the off-topic case without spending a call.

### 3. Passages are built from PDF blocks
**Decision:** PyMuPDF text blocks are merged into passages of up to 1000 characters, on one page, ending at short blocks (headings, page numbers). Longer blocks are split by LangChain's `RecursiveCharacterTextSplitter` with 150 characters of overlap.
**Why:** Each passage keeps the rectangles of its blocks, so the source can be highlighted exactly, and passages don't mix sections.
**Trade-off:** A sentence that continues onto the next page is split in two.

### 4. Highlighted pages are rendered on the server
**Decision:** `GET /pages/{n}.png?chunk=` draws the passage's rectangles on the page with PyMuPDF and returns a PNG.
**Why:** No PDF.js bundle in the browser and no coordinate mapping in JavaScript; works the same on phones.
**Trade-off:** Text in the image can't be selected; the source text is shown in the chat instead.

### 5. Local embeddings, hosted generation
**Decision:** fastembed with `BAAI/bge-small-en-v1.5` (ONNX, ~70 MB, CPU). Generation goes through LangChain's `ChatOpenAI` pointed at Groq (default), OpenAI or Ollama.
**Why:** The threshold depends on embedding scores staying the same, and embedding runs for every passage; local makes it free and stable. One OpenAI-compatible client covers all three generation options.
**Note:** bge models suggest a query prefix. On the paper above, the gap between the lowest in-document score and the highest unrelated score was 0.027 without the prefix and 0.013 with it, so queries are embedded as-is.

### 6. ChromaDB with a per-document filter
**Decision:** One Chroma collection, cosine space, every vector tagged with `document_id`; searches filter on it.
**Why:** Simple, and deleting a document removes its vectors by id. Chroma persists to `DATA_DIR/chroma`.

### 7. Each question stands alone
**Decision:** No conversation memory in retrieval or the prompt.
**Why:** Follow-ups like "and the second one?" retrieve badly without rewriting the question first, and a wrong rewrite produces confident wrong answers. Rewriting is the v2 plan; until then the UI says each question is answered on its own.

### 8. Tests need no model and no key
**Decision:** `EMBEDDINGS=hash` swaps in a hashing bag-of-words embedder, and tests replace `rag.chat_model` with a fake that records prompts.
**Why:** CI stays fast and offline, and the tests can still check what reached the prompt and that off-topic questions never call the model.

---

<div align="center">

<h3>Akshat Gupta</h3>

<a href="https://akshatgcodes.in"><img src="https://img.shields.io/badge/Website-akshatgcodes.in-111111?style=flat-square&logo=googlechrome&logoColor=white" alt="Website"></a>
<a href="https://linkedin.com/in/akshatgcodes"><img src="https://img.shields.io/badge/LinkedIn-akshatgcodes-0A66C2?style=flat-square" alt="LinkedIn"></a>
<a href="https://github.com/akshatgcodes"><img src="https://img.shields.io/badge/GitHub-akshatgcodes-181717?style=flat-square&logo=github&logoColor=white" alt="GitHub"></a>
<a href="mailto:akshatgcodes@gmail.com"><img src="https://img.shields.io/badge/Email-akshatgcodes%40gmail.com-EA4335?style=flat-square&logo=gmail&logoColor=white" alt="Email"></a>

</div>
