import {
  CheckCircle2,
  Users,
  HeartPulse,
  Radio,
  Cloud,
  Sparkles,
  LayoutDashboard,
  Cpu,
  Globe2,
  ShieldCheck,
  Plug,
  Workflow,
} from "lucide-react";
import { Card } from "../components/ui";
import { cn } from "../utils/cn";

const BUILT = [
  { icon: Workflow, title: "Dual Architecture", desc: "Next.js orchestrator + FastAPI ML backend" },
  { icon: Cpu, title: "Whisper large-v3", desc: "State-of-the-art transcription engine" },
  { icon: Globe2, title: "99-Language Translation", desc: "Auto-detect and translate to English" },
  { icon: ShieldCheck, title: "VAD Filter", desc: "Halts hallucinations during silence" },
  { icon: Sparkles, title: "Detection Engine", desc: "Profanity, threats, self-harm, scams, PII" },
  { icon: Plug, title: "REST + MCP Server", desc: "n8n, Make.com, Claude and Cursor ready" },
];

const ROADMAP = [
  {
    icon: Users,
    title: "Speaker Diarization",
    desc: "Separate Speaker 1 (Customer) and Speaker 2 (Agent) so we know who said what — the most critical next step for call centers.",
    status: "In Progress",
    progress: 55,
    accent: "from-indigo-500 to-violet-500",
  },
  {
    icon: HeartPulse,
    title: "Emotion and Tone Analysis",
    desc: "Listen to tone of voice, not just text. Flag screaming or crying as Highly Agitated even with no bad words.",
    status: "Planned",
    progress: 20,
    accent: "from-rose-500 to-pink-500",
  },
  {
    icon: Radio,
    title: "Real-Time Streaming Alerts",
    desc: "WebSocket live-call monitoring. Instant pop-up when a scammer asks for an OTP so managers can disconnect.",
    status: "Planned",
    progress: 15,
    accent: "from-orange-500 to-amber-500",
  },
  {
    icon: Cloud,
    title: "Cloud GPU Scaling",
    desc: "Deploy to GCP/AWS on NVIDIA T4/L4 GPUs. Cut processing from minutes to seconds, handle 500MB+ files via buckets.",
    status: "In Progress",
    progress: 40,
    accent: "from-sky-500 to-cyan-500",
  },
  {
    icon: Sparkles,
    title: "LLM Call Summarization",
    desc: "GPT-4 / Claude 3.5 generates a crisp 3-line summary of a 1-hour call with topics, resolution and sentiment.",
    status: "In Progress",
    progress: 65,
    accent: "from-emerald-500 to-teal-500",
  },
  {
    icon: LayoutDashboard,
    title: "Analytics Dashboard",
    desc: "Live metrics: abuse percent, top agents handling aggression, scam word clouds. You are looking at it!",
    status: "Shipped",
    progress: 100,
    accent: "from-violet-500 to-fuchsia-500",
  },
] as const;

const STATUS_STYLE: Record<string, string> = {
  Shipped: "bg-emerald-50 text-emerald-700 ring-emerald-200",
  "In Progress": "bg-amber-50 text-amber-700 ring-amber-200",
  Planned: "bg-slate-100 text-slate-600 ring-slate-200",
};

export function Roadmap() {
  return (
    <div className="space-y-6">
      <Card className="overflow-hidden">
        <div className="border-b border-slate-100 bg-gradient-to-r from-slate-50 to-white px-6 py-5">
          <div className="flex items-center gap-2">
            <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-emerald-500 text-white">
              <CheckCircle2 size={16} />
            </span>
            <h3 className="text-base font-semibold text-slate-900">What's Built</h3>
          </div>
          <p className="mt-1 text-sm text-slate-500">The production foundation that's live and working today.</p>
        </div>
        <div className="grid grid-cols-1 gap-px bg-slate-100 sm:grid-cols-2 lg:grid-cols-3">
          {BUILT.map((b) => (
            <div key={b.title} className="bg-white p-5">
              <div className="flex items-start gap-3">
                <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-indigo-50 text-indigo-600">
                  <b.icon size={18} />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <p className="text-sm font-semibold text-slate-900">{b.title}</p>
                    <CheckCircle2 size={14} className="text-emerald-500" />
                  </div>
                  <p className="mt-0.5 text-xs leading-snug text-slate-500">{b.desc}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </Card>

      <div className="flex items-center justify-between px-1">
        <div>
          <h3 className="text-base font-semibold text-slate-900">Product Roadmap</h3>
          <p className="text-sm text-slate-500">The path from prototype to enterprise SaaS.</p>
        </div>
      </div>
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2 xl:grid-cols-3">
        {ROADMAP.map((r) => (
          <Card key={r.title} className="flex flex-col p-5 transition hover:shadow-md hover:shadow-slate-200/60">
            <div className="flex items-start justify-between">
              <div
                className={cn(
                  "flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br text-white shadow-sm",
                  r.accent
                )}
              >
                <r.icon size={20} />
              </div>
              <span
                className={cn("rounded-full px-2.5 py-1 text-[11px] font-semibold ring-1 ring-inset", STATUS_STYLE[r.status])}
              >
                {r.status}
              </span>
            </div>
            <h4 className="mt-4 text-sm font-bold text-slate-900">{r.title}</h4>
            <p className="mt-1.5 flex-1 text-xs leading-relaxed text-slate-500">{r.desc}</p>
            <div className="mt-4">
              <div className="mb-1.5 flex items-center justify-between text-[11px]">
                <span className="font-medium text-slate-400">Progress</span>
                <span className="font-bold text-slate-600">{r.progress}%</span>
              </div>
              <div className="h-2 w-full overflow-hidden rounded-full bg-slate-100">
                <div
                  className={cn("h-full rounded-full bg-gradient-to-r transition-all duration-700", r.accent)}
                  style={{ width: `${r.progress}%` }}
                />
              </div>
            </div>
          </Card>
        ))}
      </div>

      <Card className="p-6">
        <h3 className="mb-1 text-base font-semibold text-slate-900">System Architecture</h3>
        <p className="mb-5 text-sm text-slate-500">Audio in then transcription, translation, diarization and analytics.</p>
        <div className="flex flex-col items-stretch gap-3 lg:flex-row lg:items-center">
          {[
            { label: "Audio Upload", icon: Radio, color: "bg-slate-700" },
            { label: "Whisper + VAD", icon: Cpu, color: "bg-indigo-600" },
            { label: "Translation", icon: Globe2, color: "bg-violet-600" },
            { label: "Diarization", icon: Users, color: "bg-fuchsia-600" },
            { label: "Analytics + PII", icon: ShieldCheck, color: "bg-emerald-600" },
          ].map((node, i, arr) => (
            <div key={node.label} className="flex flex-1 items-center gap-3">
              <div className="flex flex-1 flex-col items-center gap-2 rounded-xl border border-slate-200 bg-slate-50/60 px-3 py-4">
                <span className={cn("flex h-10 w-10 items-center justify-center rounded-xl text-white", node.color)}>
                  <node.icon size={18} />
                </span>
                <span className="text-xs font-semibold text-slate-700">{node.label}</span>
              </div>
              {i < arr.length - 1 && (
                <div className="hidden text-slate-300 lg:block">
                  <span className="text-xl">→</span>
                </div>
              )}
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
