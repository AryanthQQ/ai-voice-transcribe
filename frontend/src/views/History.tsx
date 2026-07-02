import { useMemo, useState } from "react";
import { Search, Filter, Clock, PhoneCall, ChevronDown } from "lucide-react";
import { Card, RiskBadge, CategoryBadge, Avatar } from "../components/ui";
import { CALL_HISTORY } from "../data/mock";
import { formatDuration } from "../data/samples";
import { cn } from "../utils/cn";
import type { Category } from "../lib/analyzer";

const RISK_FILTERS = ["All", "Critical", "High", "Moderate", "Safe"] as const;

function dotColor(cat: Category): string {
  const map: Record<Category, string> = {
    profanity: "#f59e0b",
    threat: "#ef4444",
    "self-harm": "#e11d48",
    scam: "#f97316",
    pii: "#3b82f6",
  };
  return map[cat];
}

export function History({ onAnalyze }: { onAnalyze: () => void }) {
  const [query, setQuery] = useState("");
  const [risk, setRisk] = useState<(typeof RISK_FILTERS)[number]>("All");
  const [expanded, setExpanded] = useState<string | null>(CALL_HISTORY[0].id);

  const filtered = useMemo(() => {
    return CALL_HISTORY.filter((c) => {
      const matchesQuery =
        !query ||
        `${c.customer} ${c.agent} ${c.id} ${c.language}`.toLowerCase().includes(query.toLowerCase());
      const matchesRisk = risk === "All" || c.riskLevel === risk;
      return matchesQuery && matchesRisk;
    });
  }, [query, risk]);

  return (
    <div className="space-y-5">
      <Card className="p-4">
        <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
          <div className="relative flex-1 lg:max-w-sm">
            <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search customer, agent, call ID…"
              className="w-full rounded-xl border border-slate-200 bg-slate-50/50 py-2.5 pl-9 pr-3 text-sm outline-none transition focus:border-indigo-300 focus:bg-white focus:ring-2 focus:ring-indigo-100"
            />
          </div>
          <div className="flex items-center gap-2">
            <Filter size={15} className="text-slate-400" />
            <div className="flex flex-wrap gap-1.5">
              {RISK_FILTERS.map((r) => (
                <button
                  key={r}
                  onClick={() => setRisk(r)}
                  className={cn(
                    "rounded-lg px-3 py-1.5 text-xs font-semibold transition",
                    risk === r ? "bg-slate-900 text-white" : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                  )}
                >
                  {r}
                </button>
              ))}
            </div>
          </div>
        </div>
      </Card>

      <Card className="overflow-hidden">
        <div className="hidden grid-cols-12 gap-4 border-b border-slate-100 bg-slate-50/60 px-5 py-3 text-[11px] font-semibold uppercase tracking-wide text-slate-500 md:grid">
          <div className="col-span-4">Call</div>
          <div className="col-span-2">Language</div>
          <div className="col-span-2">Duration</div>
          <div className="col-span-2">Signals</div>
          <div className="col-span-2 text-right">Risk</div>
        </div>
        <div className="divide-y divide-slate-100">
          {filtered.length === 0 && (
            <div className="py-16 text-center">
              <p className="text-sm text-slate-400">No calls match your filters.</p>
            </div>
          )}
          {filtered.map((c) => {
            const isOpen = expanded === c.id;
            return (
              <div key={c.id}>
                <button
                  onClick={() => setExpanded(isOpen ? null : c.id)}
                  className="grid w-full grid-cols-1 items-center gap-3 px-5 py-4 text-left transition hover:bg-slate-50/60 md:grid-cols-12"
                >
                  <div className="col-span-4 flex items-center gap-3">
                    <Avatar initials={c.agentInitials} color="bg-slate-700" />
                    <div className="min-w-0">
                      <p className="truncate text-sm font-semibold text-slate-900">{c.customer}</p>
                      <p className="truncate text-xs text-slate-500">
                        {c.agent} · {c.id} · {c.when}
                      </p>
                    </div>
                  </div>
                  <div className="col-span-2 text-sm text-slate-600">{c.language}</div>
                  <div className="col-span-2 flex items-center gap-1.5 text-sm text-slate-600">
                    <Clock size={14} className="text-slate-400" />
                    {formatDuration(c.durationSec)}
                  </div>
                  <div className="col-span-2 flex flex-wrap gap-1">
                    {c.categories.length === 0 ? (
                      <span className="text-xs text-slate-300">—</span>
                    ) : (
                      c.categories.slice(0, 2).map((cat: Category) => (
                        <span
                          key={cat}
                          className="h-2 w-2 rounded-full"
                          style={{ backgroundColor: dotColor(cat) }}
                          title={cat}
                        />
                      ))
                    )}
                  </div>
                  <div className="col-span-2 flex items-center justify-end gap-2">
                    <span className="text-sm font-bold text-slate-900">{c.riskScore}</span>
                    <RiskBadge level={c.riskLevel} />
                    <ChevronDown size={16} className={cn("text-slate-400 transition", isOpen && "rotate-180")} />
                  </div>
                </button>
                {isOpen && (
                  <div className="bg-slate-50/40 px-5 py-4">
                    <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
                      <div className="lg:col-span-2">
                        <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-400">AI Summary</p>
                        <p className="text-sm leading-relaxed text-slate-600">{c.summary}</p>
                        <div className="mt-3 flex flex-wrap gap-1.5">
                          {c.categories.length === 0 ? (
                            <span className="rounded-full bg-emerald-50 px-2.5 py-1 text-xs font-medium text-emerald-700">
                              Clean call
                            </span>
                          ) : (
                            c.categories.map((cat) => <CategoryBadge key={cat} category={cat} />)
                          )}
                        </div>
                      </div>
                      <div className="rounded-xl border border-slate-200 bg-white p-4">
                        <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-400">Actions</p>
                        <div className="space-y-2">
                          <button className="flex w-full items-center gap-2 rounded-lg bg-indigo-600 px-3 py-2 text-xs font-semibold text-white transition hover:bg-indigo-700">
                            <PhoneCall size={14} /> Open full transcript
                          </button>
                          <button className="flex w-full items-center gap-2 rounded-lg border border-slate-200 px-3 py-2 text-xs font-medium text-slate-600 transition hover:bg-slate-50">
                            Export report (PDF)
                          </button>
                          <button className="flex w-full items-center gap-2 rounded-lg border border-slate-200 px-3 py-2 text-xs font-medium text-slate-600 transition hover:bg-slate-50">
                            Assign to QA queue
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </Card>

      <div className="flex items-center justify-between px-1 text-xs text-slate-400">
        <span>
          Showing {filtered.length} of {CALL_HISTORY.length} calls
        </span>
        <button onClick={onAnalyze} className="font-medium text-indigo-600 hover:text-indigo-700">
          Analyze a new call →
        </button>
      </div>
    </div>
  );
}
