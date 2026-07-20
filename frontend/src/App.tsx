import { useState } from "react";
import {
  LayoutDashboard,
  AudioLines,
  History,
  BarChart3,
  Map,
  Menu,
  X,
  Search,
  Bell,
  ShieldCheck,
  CircleDot,
  Webhook,
} from "lucide-react";
import { cn } from "./utils/cn";
import { Dashboard } from "./views/Dashboard";
import { Analyze } from "./views/Analyze";
import { Insights } from "./views/Insights";
import { Roadmap } from "./views/Roadmap";
import { AgentMonitor } from "./views/AgentMonitor";

type ViewId = "dashboard" | "analyze" | "monitor" | "insights" | "roadmap";

const NAV: { id: ViewId; label: string; icon: typeof LayoutDashboard; title: string; subtitle: string }[] = [
  { id: "dashboard", label: "Dashboard", icon: LayoutDashboard, title: "Overview", subtitle: "Real-time speech analytics across your contact center" },
  { id: "analyze", label: "Transcribe and Analyze", icon: AudioLines, title: "Transcribe and Analyze", subtitle: "Run the Whisper pipeline with the live detection engine" },
  { id: "monitor", label: "Call Monitor (n8n)", icon: Webhook, title: "Friendship Call Monitor", subtitle: "n8n-ready: adviser_id, user_id & voice_url transcription" },
  { id: "insights", label: "Insights", icon: BarChart3, title: "Insights", subtitle: "Language coverage, trends and peak risk windows" },
  { id: "roadmap", label: "Roadmap", icon: Map, title: "Project Roadmap", subtitle: "From prototype to enterprise-grade SaaS" },
];

function initialView(): ViewId {
  if (typeof window === "undefined") return "dashboard";
  const v = new URLSearchParams(window.location.search).get("view");
  return (v && NAV.some((n) => n.id === v) ? v : "dashboard") as ViewId;
}

export default function App() {
  const [view, setView] = useState<ViewId>(initialView);
  const [navOpen, setNavOpen] = useState(false);
  const active = NAV.find((n) => n.id === view)!;
  const go = (id: ViewId) => {
    setView(id);
    setNavOpen(false);
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <aside
        className={cn(
          "fixed inset-y-0 left-0 z-50 flex w-64 flex-col bg-slate-900 transition-transform duration-300 lg:translate-x-0",
          navOpen ? "translate-x-0" : "-translate-x-full"
        )}
      >
        <div className="flex items-center justify-between px-5 py-5">
          <div className="flex items-center gap-2.5">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-500 to-violet-600 shadow-lg shadow-indigo-900/40">
              <AudioLines size={18} className="text-white" />
            </div>
            <div>
              <p className="text-sm font-bold leading-tight text-white">SpeechIQ</p>
              <p className="text-[10px] leading-tight text-slate-400">Analytics Agent</p>
            </div>
          </div>
          <button onClick={() => setNavOpen(false)} className="text-slate-400 lg:hidden">
            <X size={20} />
          </button>
        </div>

        <nav className="flex-1 space-y-1 px-3 py-2">
          <p className="px-3 pb-2 pt-3 text-[10px] font-semibold uppercase tracking-wider text-slate-500">Workspace</p>
          {NAV.map((n) => {
            const isActive = view === n.id;
            return (
              <button
                key={n.id}
                onClick={() => go(n.id)}
                className={cn(
                  "group flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition",
                  isActive ? "bg-indigo-600 text-white shadow-sm shadow-indigo-900/40" : "text-slate-400 hover:bg-slate-800 hover:text-white"
                )}
              >
                <n.icon size={18} className={cn(isActive ? "text-white" : "text-slate-500 group-hover:text-slate-300")} />
                {n.label}
              </button>
            );
          })}
        </nav>

        <div className="px-3 pb-5">
          <div className="rounded-xl border border-slate-800 bg-slate-800/50 p-3">
            <div className="flex items-center gap-2">
              <span className="relative flex h-2 w-2">
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75" />
                <span className="relative inline-flex h-2 w-2 rounded-full bg-emerald-500" />
              </span>
              <p className="text-xs font-semibold text-slate-200">FastAPI Backend</p>
            </div>
            <p className="mt-1 text-[10px] text-slate-500">faster-whisper large-v3 · int8 · offline</p>
            <div className="mt-2 flex items-center gap-1.5 text-[10px] text-slate-500">
              <CircleDot size={11} className="text-emerald-500" />
              {import.meta.env.VITE_API_URL ? new URL(import.meta.env.VITE_API_URL).host : "online"}
            </div>
          </div>
        </div>
      </aside>

      {navOpen && <div className="fixed inset-0 z-40 bg-slate-900/40 lg:hidden" onClick={() => setNavOpen(false)} />}

      <div className="lg:pl-64">
        <header className="sticky top-0 z-30 border-b border-slate-200 bg-white/80 backdrop-blur">
          <div className="flex items-center gap-4 px-5 py-4 lg:px-8">
            <button onClick={() => setNavOpen(true)} className="text-slate-500 lg:hidden">
              <Menu size={22} />
            </button>
            <div className="min-w-0 flex-1">
              <h1 className="truncate text-lg font-bold tracking-tight text-slate-900">{active.title}</h1>
              <p className="truncate text-xs text-slate-500">{active.subtitle}</p>
            </div>
            <div className="hidden items-center gap-2 md:flex">
              <div className="relative">
                <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                <input
                  placeholder="Search calls..."
                  className="w-44 rounded-lg border border-slate-200 bg-slate-50 py-2 pl-8 pr-3 text-sm outline-none transition focus:w-56 focus:border-indigo-300 focus:bg-white focus:ring-2 focus:ring-indigo-100"
                />
              </div>
              <button className="relative rounded-lg border border-slate-200 p-2 text-slate-500 transition hover:bg-slate-50">
                <Bell size={16} />
                <span className="absolute right-1.5 top-1.5 h-1.5 w-1.5 rounded-full bg-rose-500" />
              </button>
            </div>
            <div className="flex items-center gap-2 rounded-xl border border-slate-200 bg-white py-1.5 pl-1.5 pr-3">
              <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-gradient-to-br from-indigo-500 to-violet-600 text-xs font-bold text-white">
                QA
              </div>
              <div className="hidden leading-tight sm:block">
                <p className="text-xs font-semibold text-slate-800">QA Lead</p>
                <p className="flex items-center gap-1 text-[10px] text-emerald-600">
                  <ShieldCheck size={10} /> Secure session
                </p>
              </div>
            </div>
          </div>
        </header>

        <main className="px-5 py-6 lg:px-8">
          <div className="mx-auto max-w-[1400px]">
            {view === "dashboard" && <Dashboard />}
            {view === "analyze" && <Analyze />}
            {view === "monitor" && <AgentMonitor />}
            {view === "insights" && <Insights />}
            {view === "roadmap" && <Roadmap />}
          </div>
        </main>
      </div>
    </div>
  );
}
