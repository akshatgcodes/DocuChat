import { useEffect, useState } from "react";
import { api } from "../api";
import type { Doc, Source } from "../types";

interface Props {
  doc: Doc;
  source: Source | null;
  onClose?: () => void;
}

/** One page of the PDF, rendered by the server with the source passage highlighted. */
export default function PageViewer({ doc, source, onClose }: Props) {
  const [page, setPage] = useState(source?.page ?? 0);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    if (source) setPage(source.page);
  }, [source]);

  const highlight = source && source.page === page ? source.chunk_id : undefined;
  const src = api.pageUrl(doc.id, page, highlight);
  useEffect(() => setLoading(true), [src]);

  return (
    <aside className="viewer" aria-label="Document page">
      <div className="viewer-bar">
        <button className="icon-btn" aria-label="Previous page" disabled={page === 0} onClick={() => setPage(page - 1)}>
          ‹
        </button>
        <span className="small">
          Page {page + 1} of {doc.pages}
        </span>
        <button className="icon-btn" aria-label="Next page" disabled={page >= doc.pages - 1} onClick={() => setPage(page + 1)}>
          ›
        </button>
        {source && (
          <span className="muted small viewer-note">{highlight ? `Source ${source.n} highlighted` : `Source ${source.n} is on page ${source.page + 1}`}</span>
        )}
        {onClose && (
          <button className="icon-btn viewer-close" aria-label="Close page" onClick={onClose}>
            ✕
          </button>
        )}
      </div>
      <div className={`viewer-page ${loading ? "loading" : ""}`}>
        <img key={src} src={src} alt={`Page ${page + 1} of ${doc.title}`} onLoad={() => setLoading(false)} />
      </div>
    </aside>
  );
}
