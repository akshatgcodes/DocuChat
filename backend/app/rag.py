"""Retrieve, decide whether there's enough to go on, then generate with citations.

Two guards against made-up answers:
1. Retrieval confidence. If the best chunk's cosine similarity is under MIN_SIMILARITY
   the question is about something the document doesn't cover, and the LLM is never
   called.
2. The prompt tells the model to reply NOT_IN_DOCUMENT when the excerpts it was given
   don't contain the answer (related words, but not the fact asked for).
"""

import re
from dataclasses import dataclass

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import store
from app.config import settings
from app.models import Chunk

DECLINE = "NOT_IN_DOCUMENT"

SYSTEM = f"""You answer questions about one document using only the numbered excerpts \
provided.

Rules:
- Use only the excerpts. No outside knowledge, even if you know the answer.
- After each sentence, cite the excerpts that support it, like [1] or [2][3].
- If the excerpts don't contain the answer, reply with exactly {DECLINE} and nothing else.
- Be concise: a few sentences, or a short list when the question asks for several items."""


class GenerationError(Exception):
    pass


def chat_model() -> BaseChatModel:
    """Tests replace this with a fake model."""
    from langchain_openai import ChatOpenAI

    base_url, model, key = settings.llm
    if not key:
        raise GenerationError("No LLM API key. Set LLM_API_KEY (or GROQ_API_KEY) in backend/.env")
    return ChatOpenAI(base_url=base_url, model=model, api_key=key, temperature=0, timeout=60)


@dataclass
class Source:
    n: int
    chunk_id: int
    page: int
    score: float
    text: str
    used: bool  # sent to the model as context
    cited: bool = False

    def as_dict(self) -> dict:
        return self.__dict__.copy()


def level(score: float) -> str:
    if score >= settings.high_similarity:
        return "high"
    if score >= settings.min_similarity:
        return "medium"
    return "low"


def citations(answer: str) -> set[int]:
    return {
        int(n)
        for group in re.findall(r"\[(\d+(?:\s*[,\]\[]\s*\d+)*)\]", answer)
        for n in re.findall(r"\d+", group)
    }


def normalize_citations(answer: str) -> str:
    """Some models (gpt-oss on Groq) cite as 【1】 or 【1†source】 despite the prompt."""
    return re.sub(r"【\s*(\d+)(?:\s*†[^】]*)?】", r"[\1]", answer)


def build_prompt(question: str, sources: list[Source]) -> list:
    excerpts = "\n\n".join(f"[{s.n}] (page {s.page + 1}) {s.text}" for s in sources if s.used)
    return [
        SystemMessage(SYSTEM),
        HumanMessage(f"Excerpts:\n\n{excerpts}\n\nQuestion: {question}"),
    ]


def ask(db: Session, document_id: int, question: str) -> dict:
    hits = store.search(document_id, question, settings.top_k)
    chunks = {
        c.id: c for c in db.scalars(select(Chunk).where(Chunk.id.in_([h.chunk_id for h in hits])))
    }
    sources = [
        Source(
            n=i + 1,
            chunk_id=h.chunk_id,
            page=chunks[h.chunk_id].page,
            score=h.score,
            text=chunks[h.chunk_id].text,
            used=h.score >= settings.min_similarity,
        )
        for i, h in enumerate(hit for hit in hits if hit.chunk_id in chunks)
    ]
    top = max((s.score for s in sources), default=0.0)
    confidence = {"level": level(top), "score": top, "threshold": settings.min_similarity}

    def result(answer: str | None, reason: str) -> dict:
        return {
            "answer": answer,
            "answerable": reason == "answered",
            "reason": reason,
            "confidence": confidence,
            "sources": [s.as_dict() for s in sources],
        }

    if not any(s.used for s in sources):
        return result(None, "low_similarity")

    try:
        reply = chat_model().invoke(build_prompt(question, sources))
    except GenerationError:
        raise
    except Exception as e:
        raise GenerationError(f"The language model call failed: {e}") from e
    text = reply.content if isinstance(reply.content, str) else str(reply.content)
    text = normalize_citations(text.strip())

    if not text or DECLINE in text:
        confidence["level"] = "low"
        return result(None, "model_declined")

    cited = citations(text)
    for s in sources:
        s.cited = s.used and s.n in cited
    return result(text, "answered")
