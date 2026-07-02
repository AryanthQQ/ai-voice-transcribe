import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import {
  AlertTriangle,
  Headphones,
  ShieldCheck,
  ShieldAlert,
  CreditCard,
  TrendingUp,
  Flame,
  Languages,
} from "lucide-react";
import { Card, CardHeader, StatCard, CategoryBadge, RiskBadge, Avatar } from "../components/ui";
import { WordCloud } from "../components/WordCloud";
import { CATEGORY_META } from "../lib/analyzer";
import {
  ABUSE_PHRASES,
  CALL_HISTORY,
  CATEGORY_BREAKDOWN,
  DAILY_TREND,
  KPIS,
  RISK_DISTRIBUTION,
  SCAM_PHRASES,
  TOP_AGENTS,
} from "../data/mock";
import { formatDuration } from "../data/samples";

function ChartTooltip({ active, payload, label }: any) {
  if (!active || !payload?.length) return null;
  return (
    <div className="rounded-xl border border-slate-200 bg-white px-3 py-2 shadow-lg">
      {label && <p className="mb-1 text-xs font-semibold text-slate-700">{label}</p>}
      {payload.map((p: any) => (
        <p key={p.dataKey} className="flex items-center gap-2 text-xs text-slate-600">
          <span className="h-2 w-2 rounded-full" style={{ backgroundColor: p.color || p.fill }} />
          <span className="capitalize">{p.name}:</span>
          <span className="font-semibold text-slate-900">{p.value.toLocaleString()}</span>
        </p>
      ))}
    </div>
  );
}

const PIE_COLORS = CATEGORY_BREAKDOWN.map((c) => CATEGORY_META[c.category].color);

export function Dashboard({ onOpenHistory }: { onOpenHistory: () => void }) {
  const totalCategory = CATEGORY_BREAKDOWN.reduce((s, c) => s + c.count, 0);
  const recent = CALL_HISTORY.slice(0, 5);

  return (
    <div className="space-y-6">
      {/* KPIs */}
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-5">
        <StatCard
          label="Calls Analyzed"
          value={KPIS.totalCalls.toLocaleString()}
          icon={<Headphones size={20} />}
          change={KPIS.callsChange}
          accent="indigo"
          hint="Last 14 days"
        />
        <StatCard
          label="Flagged Rate"
          value={`${KPIS.flaggedRate}%`}
          icon={<ShieldAlert size={20} />}
          change={KPIS.flaggedChange}
          accent="rose"
          hint="Contain ≥1 risk signal"
        />
        <StatCard
          label="Scams Intercepted"
          value={KPIS.scamBlocked.toLocaleString()}
          icon={<AlertTriangle size={20} />}
          change={KPIS.scamChange}
          accent="amber"
          hint="Fraud attempts detected"
        />
        <StatCard
          label="PII Extracted"
          value={KPIS.piiExtracted.toLocaleString()}
          icon={<CreditCard size={20} />}
          change={KPIS.piiChange}
          accent="blue"
          hint="Phone · email · cards"
        />
        <StatCard
          label="Avg. Risk Score"
          value={`${KPIS.avgRisk}`}
          icon={<ShieldCheck size={20} />}
          change={KPIS.avgRiskChange}
          accent="emerald"
          hint="Lower is healthier"
        />
      </div>

      {/* Trend + Donut */}
      <div className="grid grid-cols-1 gap-4 xl:grid-cols-3">
        <Card className="xl:col-span-2">
          <CardHeader
            title="Call Volume & Risk Trend"
            subtitle="Daily analyzed calls vs. flagged and scam attempts"
            icon={<TrendingUp size={18} />}
            action={
              <div className="flex items-center gap-3 text-xs">
                <span className="flex items-center gap-1.5 text-slate-500">
                  <span className="h-2 w-2 rounded-full bg-indigo-500" /> Analyzed
                </span>
                <span className="flex items-center gap-1.5 text-slate-500">
                  <span className="h-2 w-2 rounded-full bg-rose-400" /> Flagged
                </span>
                <span className="flex items-center gap-1.5 text-slate-500">
                  <span className="h-2 w-2 rounded-full bg-orange-500" /> Scams
                </span>
              </div>
            }
          />
          <div className="px-2 pb-4 pt-3">
            <ResponsiveContainer width="100%" height={280}>
              <AreaChart data={DAILY_TREND} margin={{ top: 8, right: 16, left: -8, bottom: 0 }}>
                <defs>
                  <linearGradient id="gCalls" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#6366f1" stopOpacity={0.35} />
                    <stop offset="100%" stopColor="#6366f1" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="gFlag" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#fb7185" stopOpacity={0.3} />
                    <stop offset="100%" stopColor="#fb7185" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <XAxis dataKey="day" tickLine={false} axisLine={false} tick={{ fontSize: 11, fill: "#94a3b8" }} />
                <YAxis tickLine={false} axisLine={false} tick={{ fontSize: 11, fill: "#94a3b8" }} width={48} />
                <Tooltip content={<ChartTooltip />} />
                <Area type="monotone" dataKey="calls" name="Analyzed" stroke="#6366f1" strokeWidth={2.5} fill="url(#gCalls)" />
                <Area type="monotone" dataKey="flagged" name="Flagged" stroke="#fb7185" strokeWidth={2} fill="url(#gFlag)" />
                <Area type="monotone" dataKey="scams" name="Scams" stroke="#f97316" strokeWidth={2} fill="transparent" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </Card>

        <Card>
          <CardHeader title="Detection Categories" subtitle="Distribution of signals" icon={<Flame size={18} />} />
          <div className="px-5 pb-5 pt-2">
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie
                  data={CATEGORY_BREAKDOWN}
                  dataKey="count"
                  nameKey="category"
                  cx="50%"
                  cy="50%"
                  innerRadius={58}
                  outerRadius={84}
                  paddingAngle={3}
                  stroke="none"
                >
                  {PIE_COLORS.map((c, i) => (
                    <Cell key={i} fill={c} />
                  ))}
                </Pie>
                <Tooltip content={<ChartTooltip />} />
              </PieChart>
            </ResponsiveContainer>
            <div className="mt-2 grid grid-cols-2 gap-2">
              {CATEGORY_BREAKDOWN.map((c) => (
                <div key={c.category} className="flex items-center justify-between gap-2">
                  <CategoryBadge category={c.category} />
                  <span className="text-xs font-bold text-slate-700">
                    {Math.round((c.count / totalCategory) * 100)}%
                  </span>
                </div>
              ))}
            </div>
          </div>
        </Card>
      </div>

      {/* Agents + Risk dist */}
      <div className="grid grid-cols-1 gap-4 xl:grid-cols-3">
        <Card className="xl:col-span-2">
          <CardHeader
            title="Agents Handling Aggressive Calls"
            subtitle="Volume of abusive / threatening interactions per agent"
            icon={<Headphones size={18} />}
          />
          <div className="px-2 pb-4 pt-3">
            <ResponsiveContainer width="100%" height={240}>
              <BarChart data={TOP_AGENTS} margin={{ top: 4, right: 16, left: -8, bottom: 0 }}>
                <XAxis dataKey="initials" tickLine={false} axisLine={false} tick={{ fontSize: 11, fill: "#94a3b8" }} />
                <YAxis tickLine={false} axisLine={false} tick={{ fontSize: 11, fill: "#94a3b8" }} width={36} />
                <Tooltip content={<ChartTooltip />} cursor={{ fill: "#f1f5f9" }} />
                <Bar dataKey="aggressiveCalls" name="Aggressive calls" radius={[6, 6, 0, 0]} barSize={30}>
                  {TOP_AGENTS.map((_, i) => (
                    <Cell key={i} fill={i === 0 ? "#f43f5e" : i === 1 ? "#fb7185" : "#fda4af"} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>

        <Card>
          <CardHeader title="Risk Distribution" subtitle="Share of calls by risk tier" icon={<ShieldCheck size={18} />} />
          <div className="space-y-4 px-5 pb-5 pt-4">
            {RISK_DISTRIBUTION.map((r) => (
              <div key={r.level}>
                <div className="mb-1.5 flex items-center justify-between text-xs">
                  <span className="font-medium text-slate-600">{r.level}</span>
                  <span className="font-bold text-slate-900">{r.value}%</span>
                </div>
                <div className="h-2.5 w-full overflow-hidden rounded-full bg-slate-100">
                  <div
                    className="h-full rounded-full transition-all duration-700"
                    style={{ width: `${r.value}%`, backgroundColor: r.color }}
                  />
                </div>
              </div>
            ))}
            <div className="rounded-xl bg-slate-50 p-3 text-center">
              <p className="text-xs text-slate-500">Avg. processing time</p>
              <p className="text-lg font-bold text-slate-900">1.8s / call</p>
            </div>
          </div>
        </Card>
      </div>

      {/* Word clouds */}
      <div className="grid grid-cols-1 gap-4 xl:grid-cols-2">
        <Card>
          <CardHeader
            title="Top Scam Phrases"
            subtitle="Most frequent fraud signals this period"
            icon={<AlertTriangle size={18} />}
          />
          <div className="px-5 pb-5 pt-4">
            <WordCloud items={SCAM_PHRASES} />
          </div>
        </Card>
        <Card>
          <CardHeader
            title="Top Profanity"
            subtitle="Most common abusive terms detected"
            icon={<Flame size={18} />}
          />
          <div className="px-5 pb-5 pt-4">
            <WordCloud items={ABUSE_PHRASES} />
          </div>
        </Card>
      </div>

      {/* Recent calls */}
      <Card>
        <CardHeader
          title="Recent Flagged Calls"
          subtitle="Latest analyzed interactions requiring review"
          icon={<Languages size={18} />}
          action={
            <button
              onClick={onOpenHistory}
              className="rounded-lg bg-slate-100 px-3 py-1.5 text-xs font-semibold text-slate-600 transition hover:bg-slate-200"
            >
              View all →
            </button>
          }
        />
        <div className="divide-y divide-slate-100 px-2 pb-2 pt-2">
          {recent.map((c) => (
            <div key={c.id} className="flex items-center gap-4 px-3 py-3 transition hover:bg-slate-50/70">
              <Avatar initials={c.agentInitials} color="bg-slate-700" />
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-2">
                  <p className="truncate text-sm font-semibold text-slate-900">{c.customer}</p>
                  <span className="text-xs text-slate-400">· {c.id}</span>
                </div>
                <p className="truncate text-xs text-slate-500">
                  {c.agent} · {c.language} · {formatDuration(c.durationSec)} · {c.when}
                </p>
              </div>
              <div className="hidden flex-wrap items-center justify-end gap-1.5 sm:flex">
                {c.categories.slice(0, 3).map((cat) => (
                  <CategoryBadge key={cat} category={cat} />
                ))}
              </div>
              <div className="flex items-center gap-3">
                <div className="hidden text-right md:block">
                  <p className="text-sm font-bold text-slate-900">{c.riskScore}</p>
                  <p className="text-[10px] text-slate-400">risk</p>
                </div>
                <RiskBadge level={c.riskLevel} />
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
