import type { ReactNode } from "react";
import { CheckCircle2 } from "lucide-react";
import { cn } from "../utils/cn";

export function Field({
  icon,
  label,
  value,
  onChange,
  placeholder,
}: {
  icon: ReactNode;
  label: string;
  value: string;
  onChange: (v: string) => void;
  placeholder: string;
}) {
  return (
    <div>
      <label className="mb-1.5 flex items-center gap-1.5 text-xs font-semibold text-slate-600">
        {icon} {label}
      </label>
      <input
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        spellCheck={false}
        className="w-full rounded-xl border border-slate-200 bg-slate-50/50 px-3.5 py-2.5 text-sm text-slate-700 outline-none transition focus:border-indigo-300 focus:bg-white focus:ring-2 focus:ring-indigo-100"
      />
    </div>
  );
}

export interface FlagTileProps {
  icon: React.ComponentType<{ size?: number; className?: string }>;
  label: string;
  count: number;
  desc: string;
  tone: string;
  active: boolean;
}

export function FlagTile({ icon: Icon, label, count, desc, tone, active }: FlagTileProps) {
  return (
    <div className={cn("relative overflow-hidden rounded-2xl border p-5 transition", tone, active && "shadow-sm")}>
      <div className="flex items-center justify-between">
        <Icon size={22} />
        {active ? (
          <span className="rounded-full bg-white/70 px-2 py-0.5 text-[10px] font-bold uppercase tracking-wide">Detected</span>
        ) : (
          <CheckCircle2 size={18} className="text-emerald-500" />
        )}
      </div>
      <p className="mt-3 text-3xl font-extrabold">{count}</p>
      <p className="text-sm font-semibold">{label}</p>
      <p className="mt-0.5 text-xs opacity-70">{desc}</p>
    </div>
  );
}
