from sqlalchemy import select

from app import rag, store
from app.db import SessionLocal
from app.models import Chunk
from tests.conftest import make_pdf


def test_needs_login(client):
    assert client.get("/api/documents").status_code == 401


def test_upload_and_list(owner, doc):
    assert doc["title"] == "Solar Guide" and doc["pages"] == 2 and doc["chunks"] >= 2
    listed = owner.get("/api/documents").json()
    assert [d["id"] for d in listed] == [doc["id"]]


def test_upload_rejects_bad_files(owner):
    r = owner.post("/api/documents", files={"file": ("x.pdf", b"not a pdf", "application/pdf")})
    assert r.status_code == 422 and "isn't a PDF" in r.json()["detail"]
    blank = make_pdf(pages=[[]])
    r = owner.post("/api/documents", files={"file": ("scan.pdf", blank, "application/pdf")})
    assert r.status_code == 422 and "OCR" in r.json()["detail"]


def test_answer_with_citations(owner, doc, fake_llm):
    llm = fake_llm("Clean them twice a year with water and a soft brush [1].")
    r = owner.post(
        f"/api/documents/{doc['id']}/ask",
        json={"question": "How often should the panels be cleaned?"},
    )
    body = r.json()
    assert r.status_code == 200 and body["answerable"] and body["reason"] == "answered"
    top = body["sources"][0]
    assert top["n"] == 1 and top["page"] == 1 and "twice a year" in top["text"] and top["cited"]
    assert body["confidence"]["score"] == top["score"] >= 0.2
    # Only passages above the threshold went into the prompt, numbered like the sources
    prompt = llm.calls[0][1].content
    assert "[1] (page 2)" in prompt and "How often should the panels be cleaned?" in prompt
    for s in body["sources"]:
        assert (f"[{s['n']}]" in prompt) == s["used"]


def test_off_topic_question_never_reaches_the_model(owner, doc, fake_llm):
    llm = fake_llm("should not be called")
    body = owner.post(
        f"/api/documents/{doc['id']}/ask", json={"question": "Who won the football world cup?"}
    ).json()
    assert not body["answerable"] and body["reason"] == "low_similarity" and body["answer"] is None
    assert body["confidence"]["level"] == "low"
    assert llm.calls == []


def test_model_can_decline(owner, doc, fake_llm):
    fake_llm(rag.DECLINE)
    body = owner.post(
        f"/api/documents/{doc['id']}/ask", json={"question": "What colour are the solar panels?"}
    ).json()
    assert body["reason"] == "model_declined" and body["confidence"]["level"] == "low"


def test_missing_key_is_explained(owner, doc):
    r = owner.post(
        f"/api/documents/{doc['id']}/ask", json={"question": "How often should panels be cleaned?"}
    )
    assert r.status_code == 502 and "LLM_API_KEY" in r.json()["detail"]


def test_history_is_kept_and_clearable(owner, doc, fake_llm):
    fake_llm("Twenty five years [1].")
    owner.post(f"/api/documents/{doc['id']}/ask", json={"question": "How long is the warranty?"})
    msgs = owner.get(f"/api/documents/{doc['id']}/messages").json()
    assert [m["question"] for m in msgs] == ["How long is the warranty?"]
    assert owner.delete(f"/api/documents/{doc['id']}/messages").status_code == 204
    assert owner.get(f"/api/documents/{doc['id']}/messages").json() == []


def test_page_image_with_highlight(owner, doc, fake_llm):
    fake_llm("ok [1]")
    src = owner.post(
        f"/api/documents/{doc['id']}/ask", json={"question": "panels cleaned twice a year"}
    ).json()["sources"][0]
    url = f"/api/documents/{doc['id']}/pages/{src['page']}.png"
    r = owner.get(url, params={"chunk": src["chunk_id"]})
    assert r.status_code == 200 and r.headers["content-type"] == "image/png"
    assert (
        owner.get(
            f"/api/documents/{doc['id']}/pages/{1 - src['page']}.png",
            params={"chunk": src["chunk_id"]},
        ).status_code
        == 404
    )
    assert owner.get(f"/api/documents/{doc['id']}/pages/9.png").status_code == 404


def test_delete_removes_vectors(owner, doc):
    assert store.search(doc["id"], "solar panels", 4)
    assert owner.delete(f"/api/documents/{doc['id']}").status_code == 204
    assert store.search(doc["id"], "solar panels", 4) == []
    assert owner.get(f"/api/documents/{doc['id']}").status_code == 404


def test_search_is_scoped_to_one_document(owner, doc):
    other = make_pdf(
        pages=[["Sourdough bread needs a starter fed with flour and water every day."]],
        title="Bread",
    )
    oid = owner.post(
        "/api/documents", files={"file": ("bread.pdf", other, "application/pdf")}
    ).json()["id"]
    with SessionLocal() as db:
        owned = {c.id: c.document_id for c in db.scalars(select(Chunk))}
    # The bread question is closest to the bread chunk, but the solar search mustn't see it
    assert {owned[h.chunk_id] for h in store.search(doc["id"], "sourdough bread flour", 4)} == {
        doc["id"]
    }
    assert {owned[h.chunk_id] for h in store.search(oid, "solar panels", 4)} == {oid}


def test_citation_parser():
    assert rag.citations("A [1]. B [2][3]. C [4, 5]. D [12]") == {1, 2, 3, 4, 5, 12}
    assert rag.citations("no refs") == set()
