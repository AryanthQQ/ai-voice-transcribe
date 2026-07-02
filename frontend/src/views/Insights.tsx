import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { BarChart3, Globe, Clock3, Flame, Activity } from "lucide-react";
import { Card, CardHeader } from "../components/ui";
import { WordCloud } from "../components/WordCloud";
import { DAILY_TREND, SCAM_PHRASES, ABUSE_PHRASES } from "../data/mock";
import { cn } from "../utils/cn";

const LANGUAGES = [
  { lang: "Hindi", calls: 6420, pct: 34, abuse: 48 },
  { lang: "English", calls: 4810, pct: 26, abuse: 22 },
  { lang: "Tamil", calls: 2120, pct: 11, abuse: 9 },
  { lang: "Telugu", calls: 1860, pct: 10, abuse: 7 },
  { lang: "Bengali", calls: 1430, pct: 8, abuse: 6 },
  { lang: "Marathi", calls: 1180, pct: 6, abuse: 5 },
  { lang: "Others", calls: 609, pct: 5, abuse: 3 },
];

const HOURLY = [8, 6, 4, 3, 2, 3, 9, 24, 58, 72, 81, 76, 64, 70, 85, 92, 88, 79, 60, 42, 31, 22, 16, 11];

function heatColor(v: number): string {
  if (v >= 80) return "#4f46e5";
  if (v >= 60) return "#6366f1";
  if (v >= 40) return "#818cf8";
  if (v >= 20) return "#a5b4fc";
  if (v >= 8) return "#c7d2fe";
  return "#e0e7ff";
}

function ChartTooltip({ active, payload, label }: any) {
  if (!active || !payload?.length) return null;
  return (
    <div className="rounded-xl border border-slate-200 bg-white px-3 py-2 shadow-lg">
      <p className="mb-1 text-xs font-semibold text-slate-700">{label}</p>
      {payload.map((p: any) => (
        <p key={p.dataKey} className="flex items-center gap-2 text-xs text-slate-600">
          <span className="h-2 w-2 rounded-full" style={{ backgroundColor: p.color }} />
          <span className="capitalize">{p.name}:</span>
          <span className="font-semibold text-slate-900">{p.value.toLocaleString()}</span>
        </p>
      ))}
    </div>
  );
}

export function Insights() {
  const maxHour = Math.max(...HOURLY);
  const combinedPhrases = [...SCAM_PHRASES, ...ABUSE_PHRASES].sort((a, b) => b.count - a.count);

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        {[
          { label: "Languages Covered", value: "99", icon: Globe, sub: "Whisper large-v3" },
          { label: "Avg. Call Duration", value: "3:12", icon: Clock3, sub: "across all calls" },
          { label: "Escalation Rate", value: "9.2%", icon: Activity, sub: "sent to QA" },
          { label: "Peak Abuse Window", value: "3–5 PM", icon: Flame, sub: "highest profanity" },
        ].map((s) => (
          <Card key={s.label} className="p-4">
            <div className="flex items-center gap-2 text-slate-400">
              <s.icon size={16} />
              <span className="text-xs font-medium">{s.label}</span>
            </div>
            <p className="mt-2 text-xl font-bold text-slate-900">{s.value}</p>
            <p className="text-xs text-slate-400">{s.sub}</p>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 gap-4 xl:grid-cols-3">
        <Card className="xl:col-span-2">
          <CardHeader title="Detection Trend" subtitle="Flagged calls vs. scam attempts · 14 days" icon={<BarChart3 size={18} />} />
          <div className="px-2 pb-4 pt-3">
            <ResponsiveContainer width="100%" height={260}>
              <AreaChart data={DAILY_TREND} margin={{ top: 8, right: 16, left: -8, bottom: 0 }}>
                <defs>
                  <linearGradient id="iFlag" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#fb7185" stopOpacity={0.35} />
                    <stop offset="100%" stopColor="#fb7185" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#eef2f6" />
                <XAxis dataKey="day" tickLine={false} axisLine={false} tick={{ fontSize: 11, fill: "#94a3b8" }} />
                <YAxis tickLine={false} axisLine={false} tick={{ fontSize: 11, fill: "#94a3b8" }} width={44} />
                <Tooltip content={<ChartTooltip />} />
                <Area type="monotone" dataKey="flagged" name="Flagged" stroke="#fb7185" strokeWidth={2.5} fill="url(#iFlag)" />
                <Area type="monotone" dataKey="scams" name="Scams" stroke="#f97316" strokeWidth={2.5} fill="transparent" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </Card>

        <Card>
          <CardHeader title="Calls by Language" subtitle="Volume and abuse share" icon={<Globe size={18} />} />
          <div className="space-y-3.5 px-5 pb-5 pt-4">
            {LANGUAGES.map((l) => (
              <div key={l.lang}>
                <div className="mb-1 flex items-center justify-between text-xs">
                  <span className="font-medium text-slate-700">{l.lang}</span>
                  <span className="text-slate-400">
                    {l.calls.toLocaleString()} · <span className="font-semibold text-rose-500">{l.abuse}%</span> abuse
                  </span>
                </div>
                <div className="h-2 w-full overflow-hidden rounded-full bg-slate-100">
                  <div className="h-full rounded-full bg-indigo-500" style={{ width: `${l.pct}%` }} />
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>

      <Card>
        <CardHeader title="Call Volume by Hour" subtitle="When risky conversations peak (24h, IST)" icon={<Clock3 size={18} />} />
        <div className="px-5 pb-5 pt-4">
          <div className="flex items-end gap-1">
            {HOURLY.map((v, h) => (
              <div key={h} className="group flex flex-1 flex-col items-center gap-1">
                <div
                  className="w-full rounded-md transition-all duration-300 hover:opacity-80"
                  style={{
                    height: `${(v / maxHour) * 120 + 8}px`,
                    backgroundColor: heatColor(v),
                  }}
                  title={`${h}:00 — ${v} calls`}
                />
                {h % 3 === 0 && <span className="text-[9px] text-slate-400">{h}</span>}
              </div>
            ))}
          </div>
          <div className="mt-4 flex items-center justify-end gap-2 text-[10px] text-slate-400">
            <span>Low</span>
            {["#e0e7ff", "#c7d2fe", "#a5b4fc", "#818cf8", "#6366f1", "#4f46e5"].map((c) => (
              <span key={c} className={cn("h-3 w-5 rounded")} style={{ backgroundColor: c }} />
            ))}
            <span>High</span>
          </div>
        </div>
      </Card>

      <Card>
        <CardHeader title="Most Frequent Risk Phrases" subtitle="Aggregated scam and abuse terms" icon={<Flame size={18} />} />
        <div className="px-5 pb-5 pt-4">
          <WordCloud items={combinedPhrases} max={16} />
        </div>
      </Card>
    </div>
  );
}
