from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, Query, Response, UploadFile
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app import pdf, rag, store
from app.auth import require_owner
from app.config import settings
from app.db import get_db
from app.models import Chunk, Document, Message, PdfFile

router = APIRouter(prefix="/api", tags=["documents"], dependencies=[Depends(require_owner)])


def _doc(db: Session, doc_id: int) -> Document:
    d = db.get(Document, doc_id)
    if d is None:
        raise HTTPException(404, "Document not found")
    return d


def doc_dict(d: Document, chunks: int) -> dict:
    return {
        "id": d.id,
        "filename": d.filename,
        "title": d.title,
        "pages": d.pages,
        "size": d.size,
        "chunks": chunks,
        "created_at": d.created_at,
    }


@router.get("/documents")
def list_documents(db: Session = Depends(get_db)) -> list[dict]:
    counts = dict(
        db.execute(select(Chunk.document_id, func.count()).group_by(Chunk.document_id)).all()
    )
    docs = db.scalars(select(Document).order_by(Document.created_at.desc(), Document.id.desc()))
    return [doc_dict(d, counts.get(d.id, 0)) for d in docs]


@router.post("/documents", status_code=201)
def upload(file: UploadFile = File(...), db: Session = Depends(get_db)) -> dict:
    limit = settings.max_upload_mb * 1024 * 1024
    data = file.file.read(limit + 1)
    if len(data) > limit:
        raise HTTPException(413, f"PDFs up to {settings.max_upload_mb} MB")
    try:
        with pdf.open_pdf(data) as parsed:
            if parsed.page_count > settings.max_pages:
                raise HTTPException(413, f"PDFs up to {settings.max_pages} pages")
            passages = pdf.passages(parsed)
            filename = Path(file.filename or "document.pdf").name[:255]
            title = pdf.title_of(parsed, filename)[:500]
            pages = parsed.page_count
    except pdf.PdfError as e:
        raise HTTPException(422, str(e)) from e
    if not passages:
        raise HTTPException(
            422, "No text found in this PDF. Scanned pages need OCR, which isn't supported."
        )

    d = Document(filename=filename, title=title, pages=pages, size=len(data))
    db.add(d)
    db.flush()
    d.file = PdfFile(document_id=d.id, data=data)
    rows = [
        Chunk(document_id=d.id, idx=i, page=p.page, text=p.text, rects=p.rects)
        for i, p in enumerate(passages)
    ]
    db.add_all(rows)
    db.flush()
    try:
        store.add(d.id, [(c.id, c.page, c.text) for c in rows])
    except Exception:
        db.rollback()
        store.remove([c.id for c in rows])
        raise
    db.commit()
    return doc_dict(d, len(rows))


@router.get("/documents/{doc_id}")
def get_document(doc_id: int, db: Session = Depends(get_db)) -> dict:
    d = _doc(db, doc_id)
    return doc_dict(d, len(d.chunks))


@router.delete("/documents/{doc_id}", status_code=204)
def delete_document(doc_id: int, db: Session = Depends(get_db)) -> Response:
    d = _doc(db, doc_id)
    store.remove([c.id for c in d.chunks])
    db.delete(d)
    db.commit()
    return Response(status_code=204)


@router.get("/documents/{doc_id}/pages/{page}.png")
def page_image(
    doc_id: int,
    page: int,
    chunk: int | None = Query(None, description="Highlight this chunk's blocks"),
    db: Session = Depends(get_db),
) -> Response:
    d = _doc(db, doc_id)
    if not 0 <= page < d.pages:
        raise HTTPException(404, "No such page")
    rects: list[list[float]] = []
    if chunk is not None:
        c = db.get(Chunk, chunk)
        if c is None or c.document_id != doc_id or c.page != page:
            raise HTTPException(404, "That passage isn't on this page")
        rects = c.rects
    png = pdf.render_page(d.file.data, page, rects)
    return Response(png, media_type="image/png", headers={"Cache-Control": "private, max-age=3600"})


class AskIn(BaseModel):
    question: str = Field(min_length=1, max_length=2000)


@router.post("/documents/{doc_id}/ask")
def ask(doc_id: int, body: AskIn, db: Session = Depends(get_db)) -> dict:
    _doc(db, doc_id)
    question = body.question.strip()
    try:
        result = rag.ask(db, doc_id, question)
    except rag.GenerationError as e:
        raise HTTPException(502, str(e)) from e
    m = Message(document_id=doc_id, question=question, result=result)
    db.add(m)
    db.commit()
    return {"id": m.id, "question": question, **result}


@router.get("/documents/{doc_id}/messages")
def messages(doc_id: int, db: Session = Depends(get_db)) -> list[dict]:
    d = _doc(db, doc_id)
    return [{"id": m.id, "question": m.question, **m.result} for m in d.messages]


@router.delete("/documents/{doc_id}/messages", status_code=204)
def clear_messages(doc_id: int, db: Session = Depends(get_db)) -> Response:
    d = _doc(db, doc_id)
    d.messages.clear()
    db.commit()
    return Response(status_code=204)
