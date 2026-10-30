"""pgvector backend for app/store.py, for hosts without a persistent disk: vectors live
in the same Postgres database as everything else. Same functions, same scores (cosine
similarity), so the rest of the app doesn't know which backend it's using."""

from functools import lru_cache

from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, Integer, MetaData, Table, delete, select, text

from app.db import engine
from app.embeddings import get_embeddings

metadata = MetaData()

# No dimension on the column: it follows whatever the embedding model returns
vectors_table = Table(
    "chunk_vectors",
    metadata,
    Column("chunk_id", Integer, primary_key=True),
    Column("document_id", Integer, nullable=False, index=True),
    Column("embedding", Vector(), nullable=False),
)


@lru_cache
def init() -> None:
    with engine.begin() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    metadata.create_all(engine)


def add(document_id: int, chunks: list[tuple[int, int, str]]) -> None:
    init()
    vecs = get_embeddings().embed_documents([t for _, _, t in chunks])
    rows = [
        {"chunk_id": c, "document_id": document_id, "embedding": v}
        for (c, _, _), v in zip(chunks, vecs, strict=True)
    ]
    with engine.begin() as conn:
        ids = [r["chunk_id"] for r in rows]
        conn.execute(delete(vectors_table).where(vectors_table.c.chunk_id.in_(ids)))
        conn.execute(vectors_table.insert(), rows)


def search(document_id: int, query: str, k: int) -> list[tuple[int, float]]:
    """(chunk_id, cosine similarity), closest first."""
    init()
    distance = vectors_table.c.embedding.cosine_distance(get_embeddings().embed_query(query))
    stmt = (
        select(vectors_table.c.chunk_id, distance)
        .where(vectors_table.c.document_id == document_id)
        .order_by(distance)
        .limit(k)
    )
    with engine.connect() as conn:
        return [(c, round(1 - dist, 4)) for c, dist in conn.execute(stmt)]


def remove(chunk_ids: list[int]) -> None:
    init()
    with engine.begin() as conn:
        conn.execute(delete(vectors_table).where(vectors_table.c.chunk_id.in_(chunk_ids)))


def reset() -> None:
    init()
    with engine.begin() as conn:
        conn.execute(delete(vectors_table))
