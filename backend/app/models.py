from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Integer, LargeBinary, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base, JsonColumn


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    filename: Mapped[str] = mapped_column(String(255))
    title: Mapped[str] = mapped_column(String(500))
    pages: Mapped[int] = mapped_column(Integer)
    size: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    chunks: Mapped[list["Chunk"]] = relationship(
        cascade="all, delete-orphan", order_by="Chunk.idx", back_populates="document"
    )
    messages: Mapped[list["Message"]] = relationship(
        cascade="all, delete-orphan", order_by="Message.id"
    )
    file: Mapped["PdfFile | None"] = relationship(cascade="all, delete-orphan")


class PdfFile(Base):
    """The uploaded PDF itself. In the database rather than on disk, so hosts without a
    persistent disk keep it, and in its own table so listing documents never loads it."""

    __tablename__ = "pdf_files"

    document_id: Mapped[int] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"), primary_key=True
    )
    data: Mapped[bytes] = mapped_column(LargeBinary)


class Chunk(Base):
    """A passage of the PDF. Its vector lives in the vector store under the chunk id; this
    keeps where it sits."""

    __tablename__ = "chunks"

    id: Mapped[int] = mapped_column(primary_key=True)
    document_id: Mapped[int] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"), index=True
    )
    idx: Mapped[int] = mapped_column(Integer)
    page: Mapped[int] = mapped_column(Integer)  # 0-based
    text: Mapped[str] = mapped_column(Text)
    # [[x0, y0, x1, y1], ...] in PDF points: the blocks to highlight
    rects: Mapped[list[list[float]]] = mapped_column(JsonColumn)

    document: Mapped[Document] = relationship(back_populates="chunks")


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    document_id: Mapped[int] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"), index=True
    )
    question: Mapped[str] = mapped_column(Text)
    # The full /ask response: answer, answerable, confidence, sources
    result: Mapped[dict[str, Any]] = mapped_column(JsonColumn)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
