"""Chroma, through LangChain, holding one vector per chunk tagged with its document."""

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from langchain_chroma import Chroma

from app.config import settings
from app.embeddings import get_embeddings


@dataclass
class Hit:
    chunk_id: int
    score: float  # cosine similarity, higher is closer


@lru_cache
def get_store() -> Chroma:
    return Chroma(
        collection_name="chunks",
        embedding_function=get_embeddings(),
        persist_directory=str(Path(settings.data_dir) / "chroma"),
        # Cosine distance, so 1 - distance is the similarity the thresholds talk about
        collection_metadata={"hnsw:space": "cosine"},
    )


def add(document_id: int, chunks: list[tuple[int, int, str]]) -> None:
    """chunks: (chunk_id, page, text)"""
    if not chunks:
        return
    get_store().add_texts(
        texts=[text for _, _, text in chunks],
        metadatas=[{"document_id": document_id, "page": page} for _, page, _ in chunks],
        ids=[str(cid) for cid, _, _ in chunks],
    )


def search(document_id: int, query: str, k: int) -> list[Hit]:
    results = get_store().similarity_search_with_score(
        query, k=k, filter={"document_id": document_id}
    )
    return [Hit(int(doc.id), round(1 - distance, 4)) for doc, distance in results]


def remove(chunk_ids: list[int]) -> None:
    if chunk_ids:
        get_store().delete(ids=[str(c) for c in chunk_ids])
