import { CATEGORY_META, type Category } from "../lib/analyzer";
import { cn } from "../utils/cn";

interface WordCloudItem {
  phrase: string;
  count: number;
  category: Category;
}

/**
 * Lightweight tag-cloud. Font-size scales with frequency.
 * Uses a deterministic seed so layout is stable between renders.
 */
export function WordCloud({ items, max = 12 }: { items: WordCloudItem[]; max?: number }) {
  const top = [...items].sort((a, b) => b.count - a.count).slice(0, max);
  if (top.length === 0) return <p className="text-sm text-slate-400">No phrases detected.</p>;
  const maxCount = top[0].count;
  const minCount = top[top.length - 1].count;

  return (
    <div className="flex flex-wrap items-center gap-2.5">
      {top.map((w, i) => {
        const ratio = (w.count - minCount) / Math.max(1, maxCount - minCount);
        const size = 0.78 + ratio * 1.1; // 0.78rem .. 1.88rem
        const meta = CATEGORY_META[w.category];
        return (
          <span
            key={w.phrase}
            title={`${w.count} occurrences`}
            className={cn(
              "inline-flex items-center gap-1.5 rounded-lg px-2.5 py-1 font-semibold leading-none ring-1 ring-inset transition hover:-translate-y-0.5",
              meta.bg,
              meta.text,
              meta.ring
            )}
            style={{ fontSize: `${size}rem`, animationDelay: `${i * 30}ms` }}
          >
            {w.phrase}
            <span className="rounded bg-white/70 px-1 text-[0.6em] font-bold text-slate-500">
              {w.count}
            </span>
          </span>
        );
      })}
    </div>
  );
}
