import { useState } from "react";
import { percent, segments } from "../lib/answer";
import type { Answer, Source } from "../types";

interface Props {
  msg: Answer;
  active: { msg: number; n: number } | null;
  onSource: (s: Source) => void;
}

const LEVEL_LABEL = { high: "High confidence", medium: "Medium confidence", low: "Low confidence" };

export default function MessageView({ msg, active, onSource }: Props) {
  const [showAll, setShowAll] = useState(false);
  const byN = new Map(msg.sources.map((s) => [s.n, s]));
  const isActive = (s: Source) => active?.msg === msg.id && active.n === s.n;
  // Answers show what they cited (or, if the model cited nothing, what it was given)
  const cited = msg.sources.filter((s) => s.cited);
  const primary = cited.length ? cited : msg.sources.filter((s) => s.used);
  const listed = msg.answerable && !showAll ? primary : msg.sources;

  return (
    <article className="turn">
      <p className="question">{msg.question}</p>
      <div className={`answer ${msg.answerable ? "" : "declined"}`}>
        {msg.answerable && msg.answer ? (
          <p className="answer-text">
            {segments(msg.answer, new Set(byN.keys())).map((seg, i) =>
              seg.kind === "text" ? (
                <span key={i}>{seg.text}</span>
              ) : (
                <button
                  key={i}
                  className={`cite ${isActive(byN.get(seg.n)!) ? "active" : ""}`}
                  onClick={() => onSource(byN.get(seg.n)!)}
                  aria-label={`Show source ${seg.n} on page ${byN.get(seg.n)!.page + 1}`}
                >
                  {seg.n}
                </button>
              ),
            )}
          </p>
        ) : (
          <>
            <p className="answer-text">I don't have enough information in this document to answer that.</p>
            <p className="muted small why">
              {msg.reason === "low_similarity"
                ? `The closest passage matched ${percent(msg.confidence.score)}, below the ${percent(msg.confidence.threshold)} needed, so no answer was generated.`
                : "The closest passages mention related things, but the model found no answer in them."}
            </p>
          </>
        )}

        <div className="answer-foot">
          <span className={`conf conf-${msg.confidence.level}`} title={`Best passage similarity ${msg.confidence.score.toFixed(3)}`}>
            <span className="conf-bar" aria-hidden>
              <span style={{ width: percent(Math.max(0, Math.min(1, msg.confidence.score))) }} />
            </span>
            {LEVEL_LABEL[msg.confidence.level]} · {percent(msg.confidence.score)}
          </span>
        </div>

        {msg.sources.length > 0 && (
          <div className="sources">
            <p className="label">{msg.answerable ? "Sources" : "Closest passages"}</p>
            {listed.map((s) => (
              <button key={s.n} className={`source ${isActive(s) ? "active" : ""} ${s.used ? "" : "unused"}`} onClick={() => onSource(s)}>
                <span className="source-n">{s.n}</span>
                <span className="source-text">{s.text}</span>
                <span className="source-meta muted small">
                  p. {s.page + 1} · {percent(s.score)}
                </span>
              </button>
            ))}
            {msg.answerable && listed.length < msg.sources.length && (
              <button className="link-btn small" onClick={() => setShowAll(true)}>
                Show all {msg.sources.length} retrieved passages
              </button>
            )}
          </div>
        )}
      </div>
    </article>
  );
}
