import type { Site } from "./types";

export const site: Site = {
  name: "DocuChat",
  letter: "D",
  title: "DocuChat — answers from a PDF, or an honest \"not in here\"",
  description:
    "Ask questions about a PDF. Answers cite the exact passage, highlighted on the page, or say the document doesn't cover it.",
  meta: ["live", "PDF question answering", "GPLv3"],
  headline: ["Answers from your PDF,", "or an honest \"not in here\"."],
  intro:
    "Upload a PDF and ask it questions. Every claim in the answer cites a passage; click it and the page opens with that passage highlighted. And when the document doesn't cover the question, DocuChat says so instead of making something up.",
  primary: { label: "Open DocuChat", href: "/app/" },
  repo: "https://github.com/akshatgcodes/DocuChat",
  note: "Demo password: `demo1234`. The demo runs on free hosting, so the first visit can take a minute to wake up.",
  xfactor: {
    title: "It knows when it doesn't know.",
    intro:
      "Most RAG demos always answer. DocuChat measures how close the best passage is to the question first, and tells you which kind of \"no\" it is.",
    features: [
      {
        icon: "◔",
        title: "Retrieval confidence",
        body: "If even the closest passage isn't similar enough, it answers \"I don't have enough information in this document\" and never calls the model.",
      },
      {
        icon: "✋",
        title: "A second guard",
        body: "When passages are related but don't contain the answer, the model is told to decline too, and the UI says which of the two happened.",
      },
      {
        icon: "▣",
        title: "Highlighted on the page",
        body: "Passages are whole PDF blocks with exact coordinates, so the server renders the page with the source boxed. No PDF viewer to load.",
      },
    ],
  },
  preview: {
    intro: "A cited answer with its passage highlighted on page 7, and a question the paper doesn't cover, declined.",
    shots: [
      { src: "/shots/answer.png", alt: "A cited answer beside the PDF page with the source passage highlighted", caption: "Cited answer" },
      { src: "/shots/declined.png", alt: "A question the document doesn't cover, declined with an explanation", caption: "Declined" },
    ],
  },
  stack: ["React 19", "TypeScript", "Vite", "FastAPI", "LangChain", "PyMuPDF", "Chroma", "pgvector", "fastembed", "Groq", "PostgreSQL", "pytest", "Vitest"],
  concepts: [
    { title: "Threshold by measurement", body: "With the local embedding model on a 15-page paper, answerable questions scored 0.62–0.82 and unrelated ones 0.44–0.59. The ranges overlap, hence the second guard." },
    { title: "Blocks, not windows", body: "Passages are built from whole PDF blocks on one page and stop at headings, so each has exact coordinates and stays in one section." },
    { title: "Confidence on every answer", body: "High, medium or low, with the best passage's similarity, so you know how much to trust it." },
    { title: "Chat history", body: "Questions and answers are kept per document, across reloads." },
    { title: "Any OpenAI-compatible model", body: "Groq by default, or OpenAI, or a local Ollama, chosen in `.env`." },
    { title: "Two storage setups", body: "Locally: Chroma on disk and local ONNX embeddings, no key needed. On a small host (like this demo): pgvector in Postgres and an embeddings API." },
  ],
  run: {
    title: "Run your own",
    intro: "Embeddings run locally, so only the answer model needs a key. Groq has a free tier.",
    blocks: [
      {
        title: "API",
        steps: [
          { text: "Install, then set `APP_PASSWORD` and `LLM_API_KEY` in `.env`:", cmd: "cd backend && uv sync\ncp .env.example .env" },
          { text: "Start it on port 8000:", cmd: "uv run uvicorn app.main:app --reload" },
        ],
      },
      {
        title: "App",
        steps: [
          { text: "Install and start Vite:", cmd: "cd frontend && npm install\nnpm run dev" },
          { text: "Open it and upload a PDF:", cmd: "http://localhost:5173" },
        ],
      },
    ],
  },
  tagline: "PDF answers with citations, or an honest decline.",
};
