import pymupdf
import pytest

from app import pdf
from tests.conftest import make_pdf


def test_passages_keep_page_and_position():
    with pdf.open_pdf(make_pdf()) as doc:
        ps = pdf.passages(doc)
    assert {p.page for p in ps} == {0, 1}
    # Short blocks (the page number "2") are dropped; paragraphs on a page are merged
    assert all("2" != p.text for p in ps)
    cleaning = next(p for p in ps if "twice a year" in p.text)
    assert cleaning.page == 1 and len(cleaning.rects) == 2
    x0, y0, x1, y1 = cleaning.rects[0]
    assert 60 < x0 < x1 and 60 < y0 < y1 < 800


def test_long_block_is_split():
    long_para = " ".join(f"Sentence number {i} about photovoltaic maintenance." for i in range(60))
    doc = pymupdf.open()
    doc.new_page().insert_textbox(pymupdf.Rect(36, 36, 560, 800), long_para, fontsize=8)
    ps = pdf.passages(pdf.open_pdf(doc.tobytes()))
    assert len(ps) >= 3 and all(len(p.text) <= pdf.CHUNK_CHARS for p in ps)
    assert all(p.rects == ps[0].rects for p in ps)


def test_clean_rejoins_hyphenated_words():
    assert pdf.clean("photo-\nvoltaic   cells\n\nwork") == "photovoltaic cells work"


def test_rejects_non_pdf_and_encrypted():
    with pytest.raises(pdf.PdfError, match="isn't a PDF"):
        pdf.open_pdf(b"hello")
    doc = pymupdf.open()
    doc.new_page()
    locked = doc.tobytes(encryption=pymupdf.PDF_ENCRYPT_AES_256, user_pw="x", owner_pw="y")
    with pytest.raises(pdf.PdfError, match="password"):
        pdf.open_pdf(locked)


def test_title_falls_back_to_filename():
    doc = pymupdf.open()
    doc.new_page()
    assert pdf.title_of(doc, "Annual Report.PDF") == "Annual Report"


def test_render_highlights(tmp_path):
    path = tmp_path / "a.pdf"
    path.write_bytes(make_pdf())
    plain = pdf.render_page(str(path), 1, [])
    marked = pdf.render_page(str(path), 1, [[72, 72, 520, 160]])
    assert plain.startswith(b"\x89PNG") and plain != marked
