import { useEffect, useRef, useState, type DragEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "../api";
import TopBar from "../components/TopBar";
import { formatBytes } from "../lib/answer";
import type { Doc } from "../types";

export default function Library() {
  const [docs, setDocs] = useState<Doc[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [uploading, setUploading] = useState<string | null>(null);
  const [over, setOver] = useState(false);
  const input = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();

  useEffect(() => {
    api.documents().then(setDocs).catch((e: Error) => setError(e.message));
  }, []);

  const upload = async (file: File) => {
    setError(null);
    if (!/\.pdf$/i.test(file.name) && file.type !== "application/pdf") {
      setError(`${file.name} isn't a PDF`);
      return;
    }
    setUploading(file.name);
    try {
      const doc = await api.upload(file);
      navigate(`/d/${doc.id}`);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setUploading(null);
    }
  };

  const onDrop = (e: DragEvent) => {
    e.preventDefault();
    setOver(false);
    const file = e.dataTransfer.files[0];
    if (file) upload(file);
  };

  const remove = async (d: Doc) => {
    if (!confirm(`Delete "${d.title}" and its chat history?`)) return;
    await api.remove(d.id);
    setDocs((list) => list?.filter((x) => x.id !== d.id) ?? null);
  };

  return (
    <div className="shell">
      <TopBar />
      <main className="page">
        <h1>Your documents</h1>
        <p className="muted">Upload a PDF, then ask questions. Every answer links to the passage it came from.</p>

        <div
          className={`dropzone ${over ? "over" : ""} ${uploading ? "busy" : ""}`}
          onDragOver={(e) => {
            e.preventDefault();
            setOver(true);
          }}
          onDragLeave={() => setOver(false)}
          onDrop={onDrop}
        >
          {uploading ? (
            <>
              <div className="spinner" aria-hidden />
              <p>
                Reading <strong>{uploading}</strong>…
              </p>
              <p className="muted small">Splitting it into passages and embedding them. Large PDFs take a few seconds.</p>
            </>
          ) : (
            <>
              <p>
                <strong>Drop a PDF here</strong> or
              </p>
              <button className="btn btn-primary" onClick={() => input.current?.click()}>
                Choose a file
              </button>
              <p className="muted small">Up to 20 MB and 300 pages. Text PDFs only; scanned pages aren't read.</p>
            </>
          )}
          <input
            ref={input}
            type="file"
            accept="application/pdf,.pdf"
            hidden
            onChange={(e) => {
              const f = e.target.files?.[0];
              if (f) upload(f);
              e.target.value = "";
            }}
          />
        </div>
        {error && (
          <p className="error" role="alert">
            {error}
          </p>
        )}

        {docs && docs.length > 0 && (
          <ul className="doc-list">
            {docs.map((d) => (
              <li key={d.id} className="doc-row">
                <Link to={`/d/${d.id}`} className="doc-link">
                  <span className="doc-icon" aria-hidden>
                    PDF
                  </span>
                  <span>
                    <span className="doc-title">{d.title}</span>
                    <span className="muted small">
                      {d.filename} · {d.pages} {d.pages === 1 ? "page" : "pages"} · {d.chunks} passages · {formatBytes(d.size)}
                    </span>
                  </span>
                </Link>
                <button className="icon-btn" aria-label={`Delete ${d.title}`} onClick={() => remove(d)}>
                  ✕
                </button>
              </li>
            ))}
          </ul>
        )}
        {docs === null && !error && <p className="muted">Loading…</p>}
      </main>
    </div>
  );
}
