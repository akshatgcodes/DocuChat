import os
import tempfile

# Settings are read at import time, so point everything at throwaway locations first
_tmp = tempfile.mkdtemp()
os.environ.update(
    DATABASE_URL=f"sqlite:///{_tmp}/test.db",
    DATA_DIR=_tmp,
    APP_PASSWORD="test-pass",
    EMBEDDINGS="hash",  # no model download in tests
    MIN_SIMILARITY="0.2",  # hash embeddings score lower than real ones
    HIGH_SIMILARITY="0.45",
    LLM_API_KEY="",
    GROQ_API_KEY="",
)

import pymupdf  # noqa: E402
import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from langchain_core.messages import AIMessage  # noqa: E402

from app import rag, store  # noqa: E402
from app.db import Base, engine  # noqa: E402
from app.main import app  # noqa: E402

PAGES = [
    [
        "Solar Panel Owner's Guide",
        "Solar panels convert sunlight into electricity using photovoltaic cells made of "
        "silicon. A typical home system produces between three and eight kilowatts.",
        "The inverter turns the direct current from the panels into alternating current "
        "that household appliances can use.",
        "2",
    ],
    [
        "Panels should be cleaned twice a year with plain water and a soft brush. Never "
        "use a pressure washer, because it can crack the glass and void the warranty.",
        "The warranty covers manufacturing defects for twenty five years and the inverter "
        "for ten years.",
    ],
]


def make_pdf(pages=PAGES, title="Solar Guide") -> bytes:
    doc = pymupdf.open()
    for paragraphs in pages:
        page = doc.new_page()
        y = 72
        for text in paragraphs:
            rect = pymupdf.Rect(72, y, 520, y + 90)
            page.insert_textbox(rect, text, fontsize=11)
            y += 110
    doc.set_metadata({"title": title})
    return doc.tobytes()


class FakeChat:
    def __init__(self, reply: str):
        self.reply = reply
        self.calls: list = []

    def invoke(self, messages):
        self.calls.append(messages)
        return AIMessage(self.reply)


@pytest.fixture
def client():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    store.get_store().reset_collection()
    with TestClient(app) as c:
        yield c


@pytest.fixture
def owner(client):
    assert client.post("/api/auth/login", json={"password": "test-pass"}).status_code == 200
    return client


@pytest.fixture
def fake_llm(monkeypatch):
    def install(reply: str) -> FakeChat:
        fake = FakeChat(reply)
        monkeypatch.setattr(rag, "chat_model", lambda: fake)
        return fake

    return install


@pytest.fixture
def doc(owner):
    r = owner.post("/api/documents", files={"file": ("solar.pdf", make_pdf(), "application/pdf")})
    assert r.status_code == 201, r.text
    return r.json()
