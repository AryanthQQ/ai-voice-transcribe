import { useState } from "react";
import {
  ChevronDown,
  KeyRound,
  ExternalLink,
  Globe,
  Sparkles,
  Activity,
  CheckCircle2,
  Loader2,
  Server,
  Code2,
  Copy,
  Check,
  Cpu,
} from "lucide-react";
import { Card } from "./ui";
import { cn } from "../utils/cn";
import { PROVIDER_PRESETS, testConnection, type Provider, type TranscribeConfig } from "../lib/transcribe";

const BACKEND_CODE = `# app.py — faster-whisper large-v3 (int8), offline, $0/min
# pip install fastapi uvicorn faster-whisper python-multipart
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from faster_whisper import WhisperModel

app = FastAPI()
app.add_middleware(
    CORSMiddleware, allow_origins=["*"],
    allow_methods=["*"], allow_headers=["*"],
)

# int8 = runs on CPU/laptop without crashing or a GPU
model = WhisperModel("large-v3", device="cpu", compute_type="int8")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/transcribe")
async def transcribe(
    file: UploadFile = File(...),
    translate: bool = Form(False),
    language: str = Form(None),
    vad_filter: bool = Form(True),
):
    task = "translate" if translate else "transcribe"
    segments, info = model.transcribe(
        file.file, beam_size=5, vad_filter=vad_filter,
        language=language or None, task=task,
    )
    text = " ".join(s.text for s in segments).strip()
    return {"text": text, "language": info.language, "duration": info.duration}

# run:  uvicorn app:app --host 0.0.0.0 --port 8000`;

export function TranscribeSettings({
  config,
  setProvider,
  update,
  defaultOpen = false,
}: {
  config: TranscribeConfig;
  setProvider: (p: Provider) => void;
  update: (patch: Partial<TranscribeConfig>) => void;
  defaultOpen?: boolean;
}) {
  const [open, setOpen] = useState(defaultOpen);
  const [showCode, setShowCode] = useState(false);
  const [copiedCode, setCopiedCode] = useState(false);
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<{ ok: boolean; message: string } | null>(null);
  const preset = PROVIDER_PRESETS[config.provider];
  const isLocal = config.provider === "local" || config.provider === "custom";

  const runTest = async () => {
    setTesting(true);
    setTestResult(null);
    const r = await testConnection(config);
    setTestResult(r);
    setTesting(false);
  };

  const copyCode = async () => {
    try {
      await navigator.clipboard.writeText(BACKEND_CODE);
      setCopiedCode(true);
      setTimeout(() => setCopiedCode(false), 1800);
    } catch {
      /* ignore */
    }
  };

  const statusLabel = isLocal
    ? config.endpoint
      ? "endpoint set"
      : "endpoint required"
    : config.apiKey
    ? "configured"
    : "API key required";

  return (
    <Card className="overflow-hidden">
      <button
        onClick={() => setOpen((v) => !v)}
        className="flex w-full items-center justify-between px-5 py-4 text-left transition hover:bg-slate-50/60"
      >
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-indigo-50 text-indigo-600">
            <KeyRound size={17} />
          </div>
          <div>
            <p className="text-sm font-semibold text-slate-900">Whisper engine settings</p>
            <p className="text-xs text-slate-500">{preset.label} · {statusLabel}</p>
          </div>
        </div>
        <ChevronDown size={18} className={cn("text-slate-400 transition", open && "rotate-180")} />
      </button>

      {open && (
        <div className="space-y-4 border-t border-slate-100 px-5 py-4">
          {/* Provider */}
          <div>
            <label className="mb-1.5 block text-xs font-semibold text-slate-600">Provider</label>
            <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
              {(Object.keys(PROVIDER_PRESETS) as Provider[]).map((p) => {
                const meta = PROVIDER_PRESETS[p];
                const active = config.provider === p;
                return (
                  <button
                    key={p}
                    onClick={() => setProvider(p)}
                    className={cn(
                      "relative rounded-xl border p-3 text-left transition",
                      active
                        ? "border-indigo-400 bg-indigo-50/60 ring-1 ring-indigo-200"
                        : "border-slate-200 bg-white hover:border-slate-300"
                    )}
                  >
                    {p === "local" && (
                      <span className="absolute right-2 top-2 rounded-full bg-emerald-100 px-1.5 py-0.5 text-[9px] font-bold uppercase text-emerald-700">
                        Recommended
                      </span>
                    )}
                    <p className="flex items-center gap-1.5 pr-16 text-xs font-bold text-slate-900">
                      {p === "local" && <Cpu size={12} className="text-emerald-600" />}
                      {meta.label}
                    </p>
                    <p className="mt-0.5 text-[11px] leading-snug text-slate-500">{meta.blurb}</p>
                  </button>
                );
              })}
            </div>
          </div>

          {/* API key (hidden for local) */}
          {!isLocal && (
            <div>
              <label className="mb-1 flex items-center justify-between text-xs font-semibold text-slate-600">
                <span>{preset.keyLabel}</span>
                {preset.keyUrl && (
                  <a
                    href={preset.keyUrl}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center gap-1 font-medium text-indigo-600 hover:text-indigo-700"
                  >
                    Get key <ExternalLink size={11} />
                  </a>
                )}
              </label>
              <input
                type="password"
                value={config.apiKey}
                onChange={(e) => update({ apiKey: e.target.value })}
                placeholder="Paste your API key..."
                spellCheck={false}
                autoComplete="off"
                className="w-full rounded-lg border border-slate-200 bg-slate-50/50 px-3 py-2 font-mono text-xs text-slate-700 outline-none focus:border-indigo-300 focus:bg-white focus:ring-2 focus:ring-indigo-100"
              />
            </div>
          )}

          {/* Endpoint + model */}
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            <div>
              <label className="mb-1 block text-xs font-semibold text-slate-600">Endpoint URL</label>
              <input
                value={config.endpoint}
                onChange={(e) => update({ endpoint: e.target.value })}
                spellCheck={false}
                className="w-full rounded-lg border border-slate-200 bg-slate-50/50 px-3 py-2 font-mono text-xs text-slate-700 outline-none focus:border-indigo-300 focus:bg-white focus:ring-2 focus:ring-indigo-100"
              />
            </div>
            <div>
              <label className="mb-1 block text-xs font-semibold text-slate-600">Model</label>
              <input
                value={config.model}
                onChange={(e) => update({ model: e.target.value })}
                spellCheck={false}
                className="w-full rounded-lg border border-slate-200 bg-slate-50/50 px-3 py-2 font-mono text-xs text-slate-700 outline-none focus:border-indigo-300 focus:bg-white focus:ring-2 focus:ring-indigo-100"
              />
            </div>
          </div>

          {/* Test connection (local only) */}
          {isLocal && (
            <div className="rounded-xl border border-slate-200 bg-slate-50/50 p-3">
              <div className="flex items-center justify-between gap-3">
                <div className="flex items-center gap-2 text-xs font-semibold text-slate-600">
                  <Server size={14} className="text-slate-400" /> Backend status
                </div>
                <button
                  onClick={runTest}
                  disabled={testing}
                  className="inline-flex items-center gap-1.5 rounded-lg bg-slate-900 px-3 py-1.5 text-xs font-semibold text-white transition hover:bg-slate-800 disabled:opacity-50"
                >
                  {testing ? <Loader2 size={13} className="animate-spin" /> : <Activity size={13} />}
                  Test connection
                </button>
              </div>
              {testResult && (
                <div
                  className={cn(
                    "mt-2 flex items-start gap-2 rounded-lg px-2.5 py-1.5 text-xs",
                    testResult.ok ? "bg-emerald-50 text-emerald-700" : "bg-rose-50 text-rose-700"
                  )}
                >
                  {testResult.ok ? (
                    <CheckCircle2 size={14} className="mt-0.5 shrink-0" />
                  ) : (
                    <Server size={14} className="mt-0.5 shrink-0" />
                  )}
                  <span>{testResult.message}</span>
                </div>
              )}
            </div>
          )}

          {/* Options */}
          <div className="flex flex-wrap items-center gap-3">
            <label className="flex cursor-pointer items-center gap-2 rounded-lg border border-slate-200 px-3 py-2 text-xs font-medium text-slate-600">
              <input
                type="checkbox"
                checked={config.translate}
                onChange={(e) => update({ translate: e.target.checked })}
                className="h-3.5 w-3.5 accent-indigo-600"
              />
              <Globe size={13} /> Translate to English
            </label>
            {isLocal && (
              <label className="flex cursor-pointer items-center gap-2 rounded-lg border border-slate-200 px-3 py-2 text-xs font-medium text-slate-600">
                <input
                  type="checkbox"
                  checked={config.vadFilter}
                  onChange={(e) => update({ vadFilter: e.target.checked })}
                  className="h-3.5 w-3.5 accent-indigo-600"
                />
                <Activity size={13} /> VAD filter
              </label>
            )}
            <select
              value={config.language || ""}
              onChange={(e) => update({ language: e.target.value })}
              disabled={config.translate}
              className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-xs text-slate-600 outline-none disabled:opacity-50"
            >
              <option value="">Auto-detect language</option>
              <option value="en">English</option>
              <option value="hi">Hindi</option>
              <option value="ta">Tamil</option>
              <option value="te">Telugu</option>
              <option value="bn">Bengali</option>
              <option value="mr">Marathi</option>
              <option value="es">Spanish</option>
            </select>
            <span className="flex items-center gap-1 text-[11px] text-slate-400">
              <Sparkles size={11} /> Saved locally in this browser only.
            </span>
          </div>

          {/* Backend code (local only) */}
          {isLocal && (
            <div className="rounded-xl border border-slate-200">
              <button
                onClick={() => setShowCode((v) => !v)}
                className="flex w-full items-center justify-between px-4 py-2.5 text-left transition hover:bg-slate-50/60"
              >
                <span className="flex items-center gap-2 text-xs font-semibold text-slate-700">
                  <Code2 size={14} className="text-indigo-500" /> Matching faster-whisper server (int8 / large-v3)
                </span>
                <ChevronDown size={15} className={cn("text-slate-400 transition", showCode && "rotate-180")} />
              </button>
              {showCode && (
                <div className="border-t border-slate-100 p-3">
                  <div className="mb-2 flex justify-end">
                    <button
                      onClick={copyCode}
                      className="inline-flex items-center gap-1.5 rounded-lg bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-600 transition hover:bg-slate-200"
                    >
                      {copiedCode ? <Check size={12} /> : <Copy size={12} />}
                      {copiedCode ? "Copied" : "Copy"}
                    </button>
                  </div>
                  <pre className="max-h-72 overflow-auto rounded-lg bg-slate-900 p-3 text-[10.5px] leading-relaxed text-slate-100">
                    <code>{BACKEND_CODE}</code>
                  </pre>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </Card>
  );
}
