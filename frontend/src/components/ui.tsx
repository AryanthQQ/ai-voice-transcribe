import type { ReactNode } from "react";
import { cn } from "../utils/cn";
import { CATEGORY_META, type Category, type Severity } from "../lib/analyzer";

// --------------------------------------------------------------------------
//  Card
// --------------------------------------------------------------------------
export function Card({
  children,
  className,
  ...rest
}: { children: ReactNode; className?: string } & React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        "rounded-2xl border border-slate-200/80 bg-white shadow-sm shadow-slate-200/40",
        className
      )}
      {...rest}
    >
      {children}
    </div>
  );
}

export function CardHeader({
  title,
  subtitle,
  icon,
  action,
}: {
  title: string;
  subtitle?: string;
  icon?: ReactNode;
  action?: ReactNode;
}) {
  return (
    <div className="flex items-start justify-between gap-4 px-5 pt-5">
      <div className="flex items-start gap-3">
        {icon && (
          <div className="mt-0.5 flex h-9 w-9 items-center justify-center rounded-lg bg-slate-100 text-slate-600">
            {icon}
          </div>
        )}
        <div>
          <h3 className="text-sm font-semibold text-slate-900">{title}</h3>
          {subtitle && <p className="mt-0.5 text-xs text-slate-500">{subtitle}</p>}
        </div>
      </div>
      {action}
    </div>
  );
}

// --------------------------------------------------------------------------
//  KPI / Stat card
// --------------------------------------------------------------------------
export function StatCard({
  label,
  value,
  icon,
  change,
  accent = "indigo",
  hint,
}: {
  label: string;
  value: string;
  icon: ReactNode;
  change?: number;
  accent?: "indigo" | "rose" | "emerald" | "amber" | "blue";
  hint?: string;
}) {
  const accents: Record<string, string> = {
    indigo: "bg-indigo-50 text-indigo-600",
    rose: "bg-rose-50 text-rose-600",
    emerald: "bg-emerald-50 text-emerald-600",
    amber: "bg-amber-50 text-amber-600",
    blue: "bg-blue-50 text-blue-600",
  };
  const positiveGood = change !== undefined && change >= 0;
  return (
    <Card className="p-5 transition hover:shadow-md hover:shadow-slate-200/60">
      <div className="flex items-center justify-between">
        <div className={cn("flex h-10 w-10 items-center justify-center rounded-xl", accents[accent])}>
          {icon}
        </div>
        {change !== undefined && (
          <span
            className={cn(
              "inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-semibold",
              positiveGood ? "bg-emerald-50 text-emerald-600" : "bg-rose-50 text-rose-600"
            )}
          >
            {positiveGood ? "▲" : "▼"} {Math.abs(change)}%
          </span>
        )}
      </div>
      <p className="mt-4 text-2xl font-bold tracking-tight text-slate-900">{value}</p>
      <p className="mt-1 text-sm font-medium text-slate-500">{label}</p>
      {hint && <p className="mt-0.5 text-xs text-slate-400">{hint}</p>}
    </Card>
  );
}

// --------------------------------------------------------------------------
//  Badges
// --------------------------------------------------------------------------
export function CategoryBadge({ category, count }: { category: Category; count?: number }) {
  const m = CATEGORY_META[category];
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-medium ring-1 ring-inset",
        m.bg,
        m.text,
        m.ring
      )}
    >
      <span className={cn("h-1.5 w-1.5 rounded-full", m.dot)} />
      {m.label}
      {count !== undefined && <span className="font-bold">{count}</span>}
    </span>
  );
}

const RISK_STYLE: Record<string, { bg: string; text: string; dot: string; ring: string }> = {
  Critical: { bg: "bg-rose-50", text: "text-rose-700", dot: "bg-rose-500", ring: "ring-rose-200" },
  High: { bg: "bg-orange-50", text: "text-orange-700", dot: "bg-orange-500", ring: "ring-orange-200" },
  Moderate: { bg: "bg-amber-50", text: "text-amber-700", dot: "bg-amber-500", ring: "ring-amber-200" },
  Safe: { bg: "bg-emerald-50", text: "text-emerald-700", dot: "bg-emerald-500", ring: "ring-emerald-200" },
};

export function RiskBadge({ level }: { level: "Critical" | "High" | "Moderate" | "Safe" }) {
  const s = RISK_STYLE[level];
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold ring-1 ring-inset",
        s.bg,
        s.text,
        s.ring
      )}
    >
      <span className={cn("h-1.5 w-1.5 rounded-full", s.dot)} />
      {level}
    </span>
  );
}

export function SeverityChip({ severity }: { severity: Severity }) {
  const map: Record<Severity, string> = {
    critical: "bg-rose-100 text-rose-700",
    high: "bg-orange-100 text-orange-700",
    medium: "bg-amber-100 text-amber-700",
    low: "bg-slate-100 text-slate-600",
  };
  return (
    <span className={cn("rounded-md px-1.5 py-0.5 text-[10px] font-bold uppercase tracking-wide", map[severity])}>
      {severity}
    </span>
  );
}

// --------------------------------------------------------------------------
//  Misc
// --------------------------------------------------------------------------
export function ProgressBar({ value, color = "#6366f1" }: { value: number; color?: string }) {
  return (
    <div className="h-2 w-full overflow-hidden rounded-full bg-slate-100">
      <div
        className="h-full rounded-full transition-all duration-700"
        style={{ width: `${Math.min(100, Math.max(0, value))}%`, backgroundColor: color }}
      />
    </div>
  );
}

export function Avatar({ initials, color = "bg-slate-700" }: { initials: string; color?: string }) {
  return (
    <div
      className={cn(
        "flex h-9 w-9 shrink-0 items-center justify-center rounded-full text-xs font-bold text-white",
        color
      )}
    >
      {initials}
    </div>
  );
}
