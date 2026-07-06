import { useEffect, useRef, useState } from "react";
import {
  Upload,
  FileText,
  Sparkles,
  Play,
  Phone,
  Mail,
  CreditCard,
  IdCard,
  Hash,
  ShieldAlert,
  CheckCircle2,
  Loader2,
  RotateCcw,
  Lightbulb,
  ScanText,
  Radio,
  Eye,
  EyeOff,
} from "lucide-react";
import { Card, CardHeader, CategoryBadge, SeverityChip } from "../components/ui";
import { RiskGauge } from "../components/RiskGauge";
import { HighlightedTranscript } from "../components/HighlightedTranscript";
import { AudioInput } from "../components/AudioInput";
import { analyze, CATEGORY_META, type AnalysisResult, type Category } from "../lib/analyzer";
import { SAMPLE_CALLS, sampleToRawText, formatDuration, type SampleCall } from "../data/samples";
import { cn } from "../utils/cn";
import { useGlobalStore, globalStore } from "../lib/globalStore";

const STEPS = [
  "Receiving audio stream…",
  "Voice Activity Detection (VAD)…",
  "Transcribing · faster-whisper large-v3 (int8)…",
  "Translating to English…",
  "Speaker diarization…",
  "Analytics & PII engine…",
];

const PII_ICON: Record<string, typeof Phone> = {
  phone: Phone,
  email: Mail,
  "credit-card": CreditCard,
  aadhaar: IdCard,
  ssn: IdCard,
  iban: CreditCard,
  "sensitive-number": Hash,
};

function buildSummary(result: AnalysisResult, sample: SampleCall | null): string[] {
  const s = result.stats;
  const parts: string[] = [];

  if (sample) {
    parts.push(
      `Conversation between a ${sample.detectedLanguage.toUpperCase()} customer and a support agent (${formatDuration(
        sample.durationSec
      )}).`
    );
  } else {
    parts.push(`Analyzed ${result.wordCount} words of transcribed speech.`);
  }

  const flags: string[] = [];
  if (s.profanity) flags.push(`${s.profanity} profane term${s.profanity > 1 ? "s" : ""}`);
  if (s.threat) flags.push(`${s.threat} violent threat${s.threat > 1 ? "s" : ""}`);
  if (s["self-harm"]) flags.push(`${s["self-harm"]} self-harm signal${s["self-harm"] > 1 ? "s" : ""}`);
  if (s.scam) flags.push(`${s.scam} scam / fraud cue${s.scam > 1 ? "s" : ""}`);
  if (s.pii) flags.push(`${s.pii} PII item${s.pii > 1 ? "s" : ""}`);

  if (flags.length) parts.push(`Detected: ${flags.join(", ")}.`);
  else parts.push("No risk signals detected — conversation is clean.");

  if (result.riskLevel === "Critical")
    parts.push("Recommended: immediate supervisor escalation and account protection hold.");
  else if (result.riskLevel === "High") parts.push("Recommended: flag for QA review and agent support.");
  else if (result.riskLevel === "Safe") parts.push("No action required — log as compliant.");

  return parts;
}

export function Analyze() {
  const [mode, setMode] = useState<"sample" | "paste" | "audio">("sample");
  const [selectedId, setSelectedId] = useState(SAMPLE_CALLS[0].id);
  const [pasted, setPasted] = useState("");
  const [maskPii, setMaskPii] = useState(true);

  const { status, error, step, result, analyzedText, analyzedSample, sourceLabel } = useGlobalStore();

  const selected = SAMPLE_CALLS.find((s) => s.id === selectedId)!;

  const run = () => {
    const text = mode === "sample" ? sampleToRawText(selected) : pasted.trim();
    if (!text) return;
    globalStore.runAnalysisSequence(
      text, 
      mode === "sample" ? selected : null, 
      mode === "sample" ? `Sample call: ${selected.title}` : "Pasted transcript"
    );
  };

  const reset = () => {
    globalStore.reset();
  };

  // Transcripts arriving from the AudioInput live mic capture
  const handleAudioComplete = (transcript: string, label: string) => {
    globalStore.handleRawText(transcript, label);
  };

  const canAnalyze = mode === "sample" || (mode === "paste" && pasted.trim().length > 0);
  const summary = result ? buildSummary(result, analyzedSample) : [];
  const orderedCats: Category[] = ["threat", "self-harm", "scam", "profanity", "pii"];

  return (
    <div className="space-y-6">
      {/* Input */}
      <Card>
        <div className="flex flex-col gap-4 p-5">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <h2 className="flex items-center gap-2 text-base font-semibold text-slate-900">
                <Sparkles size={18} className="text-indigo-500" /> Transcribe &amp; Analyze
              </h2>
              <p className="mt-0.5 text-sm text-slate-500">
                Run the full pipeline — Whisper transcription, diarization, and the live detection engine.
              </p>
            </div>
            <div className="flex rounded-xl bg-slate-100 p-1">
              <button
                onClick={() => setMode("sample")}
                className={cn(
                  "flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-sm font-medium transition",
                  mode === "sample" ? "bg-white text-slate-900 shadow-sm" : "text-slate-500 hover:text-slate-700"
                )}
              >
                <FileText size={15} /> Sample calls
              </button>
              <button
                onClick={() => setMode("paste")}
                className={cn(
                  "flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-sm font-medium transition",
                  mode === "paste" ? "bg-white text-slate-900 shadow-sm" : "text-slate-500 hover:text-slate-700"
                )}
              >
                <ScanText size={15} /> Paste transcript
              </button>
              <button
                onClick={() => setMode("audio")}
                className={cn(
                  "flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-sm font-medium transition",
                  mode === "audio" ? "bg-white text-slate-900 shadow-sm" : "text-slate-500 hover:text-slate-700"
                )}
              >
                <Radio size={15} /> Upload / Record
              </button>
            </div>
          </div>

          {mode === "sample" ? (
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-4">
              {SAMPLE_CALLS.map((s) => (
                <button
                  key={s.id}
                  onClick={() => setSelectedId(s.id)}
                  className={cn(
                    "rounded-xl border p-4 text-left transition",
                    selectedId === s.id
                      ? "border-indigo-400 bg-indigo-50/60 ring-1 ring-indigo-200"
                      : "border-slate-200 bg-white hover:border-slate-300 hover:bg-slate-50"
                  )}
                >
                  <div className="flex items-center justify-between">
                    <span className="rounded-md bg-slate-100 px-1.5 py-0.5 text-[10px] font-bold uppercase tracking-wide text-slate-500">
                      {s.language}
                    </span>
                    <span className="text-xs text-slate-400">{formatDuration(s.durationSec)}</span>
                  </div>
                  <p className="mt-2 text-sm font-semibold text-slate-900">{s.title}</p>
                  <p className="mt-1 text-xs leading-snug text-slate-500">{s.description}</p>
                </button>
              ))}
            </div>
          ) : mode === "paste" ? (
            <div>
              <textarea
                value={pasted}
                onChange={(e) => setPasted(e.target.value)}
                rows={6}
                placeholder="Paste a raw transcript here. The engine detects profanity, threats, self-harm, scams and PII (try: 'share your OTP and CVV, my number is +91 98765 43210')."
                className="w-full resize-y rounded-xl border border-slate-200 bg-slate-50/50 p-4 text-sm text-slate-700 outline-none transition placeholder:text-slate-400 focus:border-indigo-300 focus:bg-white focus:ring-2 focus:ring-indigo-100"
              />
              <button
                onClick={() => setPasted(sampleToRawText(SAMPLE_CALLS[0]))}
                className="mt-2 text-xs font-medium text-indigo-600 hover:text-indigo-700"
              >
                + Load example transcript
              </button>
            </div>
          ) : (
            <AudioInput onComplete={handleAudioComplete} />
          )}

          {mode !== "audio" && (
            <div className="flex flex-wrap items-center gap-3 border-t border-slate-100 pt-4">
              <button
                onClick={run}
                disabled={!canAnalyze || status === "processing"}
                className="inline-flex items-center gap-2 rounded-xl bg-indigo-600 px-5 py-2.5 text-sm font-semibold text-white shadow-sm shadow-indigo-200 transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {status === "processing" ? <Loader2 size={16} className="animate-spin" /> : <Play size={16} />}
                {status === "processing" ? "Processing…" : status === "done" ? "Re-run analysis" : "Run analysis"}
              </button>
              {status === "done" && (
                <button
                  onClick={reset}
                  className="inline-flex items-center gap-2 rounded-xl border border-slate-200 px-4 py-2.5 text-sm font-medium text-slate-600 transition hover:bg-slate-50"
                >
                  <RotateCcw size={15} /> Reset
                </button>
              )}
              <span className="text-xs text-slate-400">
                {mode === "sample" ? "Audio is simulated; analysis runs on the real transcript." : "Runs entirely client-side."}
              </span>
            </div>
          )}
        </div>
      </Card>

      {/* Processing */}
      {status === "processing" && (
        <Card className="p-6">
          <div className="mx-auto max-w-md">
            <div className="mb-4 flex items-center justify-between">
              <span className="text-sm font-semibold text-slate-700">Processing pipeline</span>
              <span className="text-xs font-medium text-indigo-600">{Math.round(((step + 1) / STEPS.length) * 100)}%</span>
            </div>
            <div className="mb-5 h-2 w-full overflow-hidden rounded-full bg-slate-100">
              <div
                className="h-full rounded-full bg-gradient-to-r from-indigo-500 to-violet-500 transition-all duration-300"
                style={{ width: `${((step + 1) / STEPS.length) * 100}%` }}
              />
            </div>
            <div className="space-y-2.5">
              {STEPS.map((label, i) => (
                <div key={label} className="flex items-center gap-3 text-sm">
                  {i < step ? (
                    <CheckCircle2 size={16} className="text-emerald-500" />
                  ) : i === step ? (
                    <Loader2 size={16} className="animate-spin text-indigo-500" />
                  ) : (
                    <div className="h-4 w-4 rounded-full border-2 border-slate-200" />
                  )}
                  <span className={i <= step ? "text-slate-700" : "text-slate-400"}>{label}</span>
                </div>
              ))}
            </div>
          </div>
        </Card>
      )}

      {/* Error State */}
      {status === "error" && (
        <Card className="border-rose-100 bg-rose-50/50 p-6 text-center">
          <div className="mx-auto max-w-md">
            <ShieldAlert className="mx-auto h-12 w-12 text-rose-500" />
            <h3 className="mt-4 text-base font-bold text-slate-900">Transcription Failed</h3>
            <p className="mt-2 text-sm leading-relaxed text-rose-600">{error}</p>
            <button
              onClick={reset}
              className="mt-5 inline-flex items-center gap-2 rounded-xl bg-slate-900 px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-slate-800"
            >
              <RotateCcw size={15} /> Try again
            </button>
          </div>
        </Card>
      )}
 
      {/* Results */}
      {status === "done" && result && (
        <div className="space-y-6">
          {/* Headline */}
          <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
            <Card className="flex flex-col items-center justify-center p-5">
              <p className="mb-1 text-xs font-semibold uppercase tracking-wide text-slate-400">Risk Score</p>
              <RiskGauge score={result.riskScore} />
              <div
                className={cn(
                  "mt-1 rounded-full px-3 py-1 text-sm font-bold",
                  result.riskLevel === "Critical"
                    ? "bg-rose-100 text-rose-700"
                    : result.riskLevel === "High"
                    ? "bg-orange-100 text-orange-700"
                    : result.riskLevel === "Moderate"
                    ? "bg-amber-100 text-amber-700"
                    : "bg-emerald-100 text-emerald-700"
                )}
              >
                {result.riskLevel}
              </div>
            </Card>

            <Card className="p-5 lg:col-span-2">
              <div className="mb-3 flex items-center gap-2">
                <Lightbulb size={16} className="text-amber-500" />
                <h3 className="text-sm font-semibold text-slate-900">AI Summary</h3>
                <span className="rounded-md bg-indigo-50 px-1.5 py-0.5 text-[10px] font-bold text-indigo-600">
                  AUTO-GENERATED
                </span>
              </div>
              <ul className="space-y-2">
                {summary.map((line, i) => (
                  <li key={i} className="flex gap-2 text-sm leading-relaxed text-slate-600">
                    <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-indigo-400" />
                    {line}
                  </li>
                ))}
              </ul>
              <div className="mt-4 flex flex-wrap gap-2 border-t border-slate-100 pt-4">
                {orderedCats.map((cat) => (
                  <div
                    key={cat}
                    className={cn(
                      "flex items-center gap-2 rounded-lg px-3 py-1.5 text-xs",
                      CATEGORY_META[cat].bg,
                      CATEGORY_META[cat].text
                    )}
                  >
                    <span className={cn("h-2 w-2 rounded-full", CATEGORY_META[cat].dot)} />
                    <span className="font-medium">{CATEGORY_META[cat].label}</span>
                    <span className="font-bold">{result.stats[cat]}</span>
                  </div>
                ))}
              </div>
            </Card>
          </div>

          {/* Findings + PII */}
          <div className="grid grid-cols-1 gap-4 xl:grid-cols-3">
            <Card className="xl:col-span-2">
              <CardHeader
                title="Detected Findings"
                subtitle={`${result.findings.length} signal${result.findings.length !== 1 ? "s" : ""} across the transcript`}
                icon={<ShieldAlert size={18} />}
              />
              <div className="max-h-[420px] space-y-2 overflow-y-auto p-4">
                {result.findings.length === 0 ? (
                  <div className="flex flex-col items-center justify-center py-12 text-center">
                    <CheckCircle2 size={32} className="text-emerald-500" />
                    <p className="mt-2 text-sm font-medium text-slate-600">No risky language detected</p>
                    <p className="text-xs text-slate-400">This transcript is clean.</p>
                  </div>
                ) : (
                  result.findings.map((f) => {
                    const meta = CATEGORY_META[f.category];
                    return (
                      <div
                        key={f.id}
                        className="flex items-center gap-3 rounded-xl border border-slate-100 bg-slate-50/50 p-3 transition hover:bg-white hover:shadow-sm"
                      >
                        <span className={cn("h-8 w-1.5 shrink-0 rounded-full", meta.dot)} />
                        <div className="min-w-0 flex-1">
                          <div className="flex items-center gap-2">
                            <p className="truncate text-sm font-semibold text-slate-800">&ldquo;{f.match}&rdquo;</p>
                            <SeverityChip severity={f.severity} />
                          </div>
                          <p className="text-xs text-slate-500">
                            {f.label} · {f.language}
                          </p>
                        </div>
                        <CategoryBadge category={f.category} />
                      </div>
                    );
                  })
                )}
              </div>
            </Card>

            <Card>
              <CardHeader
                title="PII Extracted"
                subtitle={`${result.pii.length} sensitive item${result.pii.length !== 1 ? "s" : ""} masked`}
                icon={<CreditCard size={18} />}
              />
              <div className="max-h-[420px] space-y-2 overflow-y-auto p-4">
                {result.pii.length === 0 ? (
                  <p className="py-8 text-center text-sm text-slate-400">No PII found.</p>
                ) : (
                  result.pii.map((p) => {
                    const Icon = PII_ICON[p.type] ?? IdCard;
                    return (
                      <div key={p.id} className="flex items-center gap-3 rounded-xl border border-slate-100 p-3">
                        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-blue-50 text-blue-600">
                          <Icon size={16} />
                        </div>
                        <div className="min-w-0 flex-1">
                          <p className="text-sm font-semibold text-slate-800">{p.masked}</p>
                          <p className="text-xs capitalize text-slate-500">{p.type.replace("-", " ")}</p>
                        </div>
                      </div>
                    );
                  })
                )}
              </div>
            </Card>
          </div>

          {/* Transcript */}
          <Card>
            <CardHeader
              title="Analyzed Transcript"
              subtitle={
                (analyzedSample ? "Speaker-separated · " : "") +
                "numbers highlighted & " +
                (maskPii ? "masked" : "revealed") +
                (sourceLabel ? ` · ${sourceLabel}` : "")
              }
              icon={<ScanText size={18} />}
              action={
                <button
                  onClick={() => setMaskPii((v) => !v)}
                  className="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 px-2.5 py-1.5 text-xs font-semibold text-slate-600 transition hover:bg-slate-50"
                  title={maskPii ? "Reveal PII in transcript" : "Mask PII in transcript"}
                >
                  {maskPii ? <EyeOff size={13} /> : <Eye size={13} />}
                  {maskPii ? "Masked" : "Revealed"}
                </button>
              }
            />
            <div className="p-5">
              {analyzedSample ? (
                <div className="space-y-4">
                  {analyzedSample.turns.map((t, i) => {
                    const turnResult = analyze(t.text);
                    const isAgent = t.speaker === "agent";
                    return (
                      <div key={i} className={cn("flex gap-3", isAgent && "flex-row-reverse")}>
                        <div
                          className={cn(
                            "flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-xs font-bold text-white",
                            isAgent ? "bg-indigo-500" : "bg-slate-600"
                          )}
                        >
                          {isAgent ? "A" : "C"}
                        </div>
                        <div className="max-w-[80%]">
                          <div className="mb-1 flex items-center gap-2">
                            <span className="text-xs font-semibold text-slate-700">
                              {isAgent ? "Agent" : "Customer"}
                            </span>
                            <span className="text-[10px] text-slate-400">{t.time}</span>
                          </div>
                          <div className={cn("rounded-2xl px-4 py-2.5 text-sm", isAgent ? "bg-indigo-50" : "bg-slate-100")}>
                            <HighlightedTranscript
                              text={t.text}
                              findings={turnResult.findings}
                              pii={turnResult.pii}
                              maskPii={maskPii}
                            />
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              ) : (
                <div className="rounded-xl bg-slate-50 p-5 text-sm">
                  <HighlightedTranscript
                    text={analyzedText}
                    findings={result.findings}
                    pii={result.pii}
                    maskPii={maskPii}
                  />
                </div>
              )}
            </div>
          </Card>
        </div>
      )}

      {/* Idle hero */}
      {status === "idle" && (
        <Card className="overflow-hidden">
          <div className="grid grid-cols-1 items-center gap-6 p-8 md:grid-cols-2">
            <div>
              <div className="mb-3 inline-flex items-center gap-2 rounded-full bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-700">
                <Sparkles size={13} /> faster-whisper large-v3 · int8 · offline · $0/min
              </div>
              <h3 className="text-xl font-bold text-slate-900">Drop a call, get a full risk breakdown</h3>
              <p className="mt-2 text-sm leading-relaxed text-slate-500">
                Pick a sample call or paste a transcript, then run the pipeline. The detection engine flags profanity
                (Hindi &amp; English), violent threats, self-harm cues, financial scams, and extracts &amp; masks PII in
                real time — entirely in your browser.
              </p>
              <div className="mt-4 flex flex-wrap gap-2">
                {(["profanity", "threat", "self-harm", "scam", "pii"] as Category[]).map((c) => (
                  <CategoryBadge key={c} category={c} />
                ))}
              </div>
            </div>
            <div className="flex items-center justify-center">
              <div className="relative">
                <div className="flex h-40 w-40 items-center justify-center rounded-3xl bg-gradient-to-br from-indigo-500 to-violet-600 text-white shadow-xl shadow-indigo-200">
                  <Upload size={56} />
                </div>
                <div className="absolute -right-3 -top-3 rounded-xl bg-white px-3 py-1.5 text-xs font-bold text-emerald-600 shadow-md ring-1 ring-emerald-100">
                  ⚡ 1.8s avg
                </div>
              </div>
            </div>
          </div>
        </Card>
      )}
    </div>
  );
}
