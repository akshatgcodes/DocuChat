import { useEffect, useRef, useState, type FormEvent } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../api";
import MessageView from "../components/MessageView";
import PageViewer from "../components/PageViewer";
import TopBar from "../components/TopBar";
import type { Answer, Doc, Source } from "../types";

export default function Chat() {
  const id = Number(useParams().id);
  const [doc, setDoc] = useState<Doc | null>(null);
  const [msgs, setMsgs] = useState<Answer[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [question, setQuestion] = useState("");
  const [pending, setPending] = useState<string | null>(null);
  const [active, setActive] = useState<{ msg: number; source: Source } | null>(null);
  const [viewerOpen, setViewerOpen] = useState(false);
  const end = useRef<HTMLDivElement>(null);

  useEffect(() => {
    Promise.all([api.document(id), api.messages(id)])
      .then(([d, m]) => {
        setDoc(d);
        setMsgs(m);
      })
      .catch((e: Error) => setError(e.message));
  }, [id]);

  useEffect(() => {
    end.current?.scrollIntoView({ block: "end" });
  }, [msgs.length, pending]);

  const show = (msg: Answer, source: Source) => {
    setActive({ msg: msg.id, source });
    setViewerOpen(true);
  };

  const ask = async (e: FormEvent) => {
    e.preventDefault();
    const q = question.trim();
    if (!q || pending) return;
    setPending(q);
    setQuestion("");
    setError(null);
    try {
      const answer = await api.ask(id, q);
      setMsgs((m) => [...m, answer]);
      const first = answer.sources.find((s) => s.cited) ?? (answer.answerable ? answer.sources[0] : undefined);
      if (first) setActive({ msg: answer.id, source: first });
    } catch (err) {
      setError((err as Error).message);
      setQuestion(q);
    } finally {
      setPending(null);
    }
  };

  if (error && !doc)
    return (
      <div className="center">
        <p className="error">{error}</p>
        <Link to="/">Back to documents</Link>
      </div>
    );
  if (!doc) return <div className="center muted">Loading…</div>;

  return (
    <div className="chat-shell">
      <TopBar>
        <span className="doc-name" title={doc.filename}>
          {doc.title}
        </span>
      </TopBar>
      <div className={`chat-layout ${viewerOpen ? "viewer-open" : ""}`}>
        <section className="chat" aria-label="Conversation">
          <div className="thread">
            {msgs.length === 0 && !pending && (
              <div className="intro">
                <h2>Ask anything about this document</h2>
                <p className="muted">
                  {doc.pages} pages, {doc.chunks} passages indexed. Each answer cites the passages it used; click a number to see it highlighted on
                  the page. If the document doesn't cover your question, DocuChat says so instead of guessing.
                </p>
              </div>
            )}
            {msgs.map((m) => (
              <MessageView key={m.id} msg={m} active={active ? { msg: active.msg, n: active.source.n } : null} onSource={(s) => show(m, s)} />
            ))}
            {pending && (
              <article className="turn">
                <p className="question">{pending}</p>
                <div className="answer thinking" aria-live="polite">
                  <span className="dots" aria-hidden>
                    <i />
                    <i />
                    <i />
                  </span>
                  Searching the document…
                </div>
              </article>
            )}
            <div ref={end} />
          </div>
          <form className="composer" onSubmit={ask}>
            {error && (
              <p className="error small" role="alert">
                {error}
              </p>
            )}
            <div className="composer-row">
              <textarea
                aria-label="Question"
                placeholder="Ask a question about the document…"
                rows={1}
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    e.currentTarget.form?.requestSubmit();
                  }
                }}
                maxLength={2000}
              />
              <button className="btn btn-primary" type="submit" disabled={!question.trim() || !!pending}>
                Ask
              </button>
            </div>
            <div className="composer-foot muted small">
              <span>Each question is answered on its own, from this document only.</span>
              {msgs.length > 0 && (
                <button
                  type="button"
                  className="link-btn small"
                  onClick={async () => {
                    if (!confirm("Clear this conversation?")) return;
                    await api.clear(id);
                    setMsgs([]);
                    setActive(null);
                  }}
                >
                  Clear chat
                </button>
              )}
              <button type="button" className="link-btn small show-page" onClick={() => setViewerOpen(true)}>
                View pages
              </button>
            </div>
          </form>
        </section>
        <PageViewer doc={doc} source={active?.source ?? null} onClose={() => setViewerOpen(false)} />
      </div>
    </div>
  );
}
