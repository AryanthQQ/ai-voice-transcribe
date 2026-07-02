import type { ReactNode } from "react";
import { CATEGORY_META, type Finding, type PIIMatch } from "../lib/analyzer";
import { cn } from "../utils/cn";

interface Segment {
  start: number;
  end: number;
  kind: "text" | "finding" | "pii";
  finding?: Finding;
  pii?: PIIMatch;
}

/**
 * Renders transcript text with inline highlighting of detected findings and
 * PII. PII spans can be masked (default) or revealed for review.
 */
export function HighlightedTranscript({
  text,
  findings,
  pii = [],
  maskPii = true,
}: {
  text: string;
  findings: Finding[];
  pii?: PIIMatch[];
  maskPii?: boolean;
}) {
  // Merge findings + pii into ordered, non-overlapping segments.
  const marks: Segment[] = [
    ...findings.map<Segment>((f) => ({ start: f.start, end: f.end, kind: "finding", finding: f })),
    ...pii.map<Segment>((p) => ({ start: p.start, end: p.end, kind: "pii", pii: p })),
  ].sort((a, b) => a.start - b.start || b.end - a.end - (a.end - a.start));

  const accepted: Segment[] = [];
  for (const m of marks) {
    if (accepted.some((a) => m.start < a.end && m.end > a.start)) continue;
    accepted.push(m);
  }
  accepted.sort((a, b) => a.start - b.start);

  if (accepted.length === 0) {
    return <span className="leading-relaxed text-slate-600">{text}</span>;
  }

  const segments: ReactNode[] = [];
  let cursor = 0;
  accepted.forEach((m, i) => {
    if (m.start > cursor) segments.push(<span key={`t-${i}`}>{text.slice(cursor, m.start)}</span>);
    if (m.kind === "finding" && m.finding) {
      const meta = CATEGORY_META[m.finding.category];
      segments.push(
        <mark
          key={`m-${i}`}
          title={`${meta.label} · ${m.finding.label} (${m.finding.language})`}
          className={cn(
            "cursor-help rounded px-1 py-0.5 font-medium ring-1 ring-inset",
            meta.bg,
            meta.text,
            meta.ring
          )}
        >
          {text.slice(m.start, m.end)}
        </mark>
      );
    } else if (m.kind === "pii" && m.pii) {
      const shown = maskPii ? m.pii.masked : text.slice(m.start, m.end);
      segments.push(
        <mark
          key={`p-${i}`}
          title={`PII · ${m.pii.type.replace("-", " ")}`}
          className="cursor-help rounded bg-blue-100 px-1 py-0.5 font-semibold text-blue-800 ring-1 ring-inset ring-blue-300"
        >
          {shown}
        </mark>
      );
    }
    cursor = Math.max(cursor, m.end);
  });
  if (cursor < text.length) segments.push(<span key="t-end">{text.slice(cursor)}</span>);

  return <span className="leading-relaxed text-slate-700">{segments}</span>;
}
