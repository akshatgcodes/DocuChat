export type Segment = { kind: "text"; text: string } | { kind: "cite"; n: number };

/**
 * Split an answer into text and citation markers so [2] can render as a button.
 * Handles [1], [1][2] and [1, 2]; numbers with no matching source stay as text.
 */
export function segments(answer: string, known: Set<number>): Segment[] {
  const out: Segment[] = [];
  const pattern = /\[(\d+(?:\s*,\s*\d+)*)\]/g;
  let last = 0;
  for (const m of answer.matchAll(pattern)) {
    const nums = m[1].split(",").map((s) => Number(s.trim()));
    if (!nums.every((n) => known.has(n))) continue;
    if (m.index > last) out.push({ kind: "text", text: answer.slice(last, m.index) });
    nums.forEach((n) => out.push({ kind: "cite", n }));
    last = m.index + m[0].length;
  }
  if (last < answer.length) out.push({ kind: "text", text: answer.slice(last) });
  return out;
}

export function formatBytes(n: number): string {
  if (n < 1024) return `${n} B`;
  if (n < 1024 * 1024) return `${(n / 1024).toFixed(0)} KB`;
  return `${(n / 1024 / 1024).toFixed(1)} MB`;
}

export const percent = (score: number) => `${Math.round(score * 100)}%`;
