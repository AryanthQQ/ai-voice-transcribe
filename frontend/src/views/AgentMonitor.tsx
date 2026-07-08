import { useEffect, useRef, useState } from "react";
import {
  Users,
  Link2,
  UserCog,
  Loader2,
  Play,
  AlertTriangle,
  Phone,
  Flame,
  ShieldAlert,
  Copy,
  Check,
  Webhook,
  ScanText,
  Eye,
  EyeOff,
  Radio,
} from "lucide-react";
import { Card, CardHeader, RiskBadge } from "../components/ui";
import { HighlightedTranscript } from "../components/HighlightedTranscript";
import { TranscribeSettings } from "../components/TranscribeSettings";
import { RiskGauge } from "../components/RiskGauge";
import { Field, FlagTile } from "../components/AgentUi";
import { Activity, Clock, VolumeX, Mic } from "lucide-react";
import { useTranscribeSettings } from "../lib/useTranscribeSettings";
import { transcribeUrl, TranscribeError } from "../lib/transcribe";
import { analyze, CATEGORY_META } from "../lib/analyzer";
import { buildPayload, FLAG_TONES, type AgentResult } from "./agentHelpers";
import { cn } from "../utils/cn";

export function AgentMonitor() {
  const { config, setProvider, update, isReady } = useTranscribeSettings();
  const [adviserId, setAdviserId] = useState("");
  const [userId, setUserId] = useState("");
  const [voiceUrl, setVoiceUrl] = useState("");
  const [status, setStatus] = useState<"idle" | "working" | "done" | "error">("idle");
  const [error, setError] = useState("");
  const [result, setResult] = useState<AgentResult | null>(null);
  const [maskPii, setMaskPii] = useState(true);
  const [copied, setCopied] = useState(false);
  const [stage, setStage] = useState("");

  const process = async (advId: string, usrId: string, vUrl: string) => {
    setError("");
    setResult(null);
    setStatus("working");
    setStage("📥 Downloading audio file...");
    
    // Stage ticker - updates message every few seconds so user knows it's alive
    const stages = [
      "📥 Downloading audio file...",
      "🎙️ AI is transcribing the recording... (this can take 1-3 mins)",
      "🔍 Running speaker diarization...",
      "🧠 Analyzing for violations, threats & PII...",
      "📊 Almost done, building report...",
    ];
    let stageIdx = 0;
    const stageTicker = setInterval(() => {
      stageIdx = Math.min(stageIdx + 1, stages.length - 1);
      setStage(stages[stageIdx]);
    }, 20000); // update every 20 seconds

    // 60-minute timeout (diarization + whisper on CPU can take a long time for big files)
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 60 * 60 * 1000);
    
    try {
      const fd = new FormData();
      fd.append("sender_ref_code", usrId);
      fd.append("reciever_ref_code", advId);
      fd.append("voice_url", vUrl);

      const res = await fetch("http://localhost:8001/api/analyze-call", {
        method: "POST",
        body: fd,
        signal: controller.signal,
      });
      
      clearTimeout(timeoutId);
      clearInterval(stageTicker);

      if (!res.ok) {
        throw new Error(`Backend returned HTTP ${res.status}`);
      }
      
      let data = await res.json();
      
      // If the backend returns a job_id, it is operating in asynchronous mode. Polling is required.
      if (data.job_id) {
        let isDone = false;
        while (!isDone) {
          await new Promise(r => setTimeout(r, 3000)); // Poll every 3 seconds
          const statusRes = await fetch(`http://localhost:8001/api/analyze-status/${data.job_id}`, {
            signal: controller.signal
          });
          const statusData = await statusRes.json();
          
          if (statusData.status === "COMPLETED") {
            data = statusData.result; // Extract the final AnalyzeCallResponse payload
            isDone = true;
          } else if (statusData.status === "FAILED") {
            throw new Error(statusData.error || "Background job failed during transcription");
          }
          // If status is PENDING or PROCESSING, it will naturally continue the loop
        }
      }

      if (data.success === false) {
        throw new Error(data.error?.message || data.error || "Backend analysis failed");
      }
      
      // We still run the client-side analysis engine to get the UI badges & highlights
      // even though the backend already ran its own analysis.
      setStage("✅ Rendering detection engine results...");
      const analysis = analyze(data.transcript);
      
      setResult({
        adviserId: advId,
        userId: usrId,
        voiceUrl: vUrl,
        transcript: data.transcript,
        language: data.language || "en",
        analysis,
        turns: data.turns,
      });
      setStatus("done");
    } catch (error: any) {
      clearTimeout(timeoutId);
      clearInterval(stageTicker);
      setStatus("error");
      if (error.name === 'AbortError') {
        setError('Request timed out after 20 minutes. The backend may be overloaded. Please try again.');
      } else {
        setError(error?.message || "Something went wrong.");
      }
    }
  };


  const run = () => process(adviserId, userId, voiceUrl);

  // n8n integration: read adviser_id / user_id / voice_url from the URL.
  // Add &auto=1 to run automatically once the Whisper key is configured.
  const autoRan = useRef(false);
  useEffect(() => {
    if (autoRan.current) return;
    const p = new URLSearchParams(window.location.search);
    const adv = p.get("reciever_ref_code") || p.get("adviser_id") || p.get("adviserId") || "";
    const usr = p.get("sender_ref_code") || p.get("user_id") || p.get("userId") || "";
    const vUrl = p.get("voice_url") || p.get("voiceUrl") || "";
    if (!vUrl) return;
    setAdviserId(adv);
    setUserId(usr);
    setVoiceUrl(vUrl);
    if (p.get("auto") === "1") {
      autoRan.current = true;
      // small delay so isReady (localStorage) is settled before processing
      setTimeout(() => process(adv, usr, vUrl), 300);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const canRun = !!voiceUrl.trim() && isReady;

  const base = typeof window !== "undefined" ? window.location.origin + window.location.pathname : "";
  const triggerUrl =
    `${base}?view=monitor` +
    `&reciever_ref_code={{$json.reciever_ref_code}}` +
    `&sender_ref_code={{$json.sender_ref_code}}` +
    `&voice_url={{$json.voice_url}}` +
    `&auto=1`;
  const payload = result ? buildPayload(result, config) : null;

  const copyPayload = async () => {
    if (!payload) return;
    try {
      await navigator.clipboard.writeText(JSON.stringify(payload, null, 2));
      setCopied(true);
      setTimeout(() => setCopied(false), 1800);
    } catch {
      /* ignore */
    }
  };

  return (
    <div className="space-y-6">
      <Card className="overflow-hidden">
        <div className="flex flex-col gap-4 bg-gradient-to-br from-indigo-600 to-violet-600 p-6 text-white sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 className="flex items-center gap-2 text-lg font-bold">
              <Webhook size={20} /> Friendship Call Monitor
            </h2>
            <p className="mt-1 max-w-xl text-sm text-indigo-100">
              Built for n8n. Receive reciever_ref_code, sender_ref_code and a voice_url — transcribe with Whisper and flag shared phone numbers, abuse and threats.
            </p>
          </div>
          <div className="flex items-center gap-2 rounded-xl bg-white/10 px-3 py-2 text-xs font-medium ring-1 ring-white/20">
            <span className={cn("h-2 w-2 rounded-full", isReady ? "bg-emerald-400" : "bg-amber-300")} />
            {isReady ? "Whisper ready" : "Add API key"}
          </div>
        </div>
      </Card>

      {/* n8n trigger */}
      <Card className="p-4">
        <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex items-start gap-2">
            <Webhook size={15} className="mt-0.5 text-indigo-500" />
            <p className="text-xs text-slate-500">
              <span className="font-semibold text-slate-700">Trigger from n8n</span> — open this URL with query params
              (add <code className="font-mono text-indigo-600">&amp;auto=1</code> to run instantly):
            </p>
          </div>
          <code className="block overflow-x-auto rounded-lg bg-slate-900 px-3 py-2 text-[10px] leading-relaxed text-slate-100">
            {triggerUrl}
          </code>
        </div>
      </Card>

      <Card className="p-5">
        <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
          <Field icon={<UserCog size={13} className="text-slate-400" />} label="Receiver Ref Code (Adviser)" value={adviserId} onChange={setAdviserId} placeholder="adviser_8741" />
          <Field icon={<Users size={13} className="text-slate-400" />} label="Sender Ref Code (Customer)" value={userId} onChange={setUserId} placeholder="user_30912" />
          <Field icon={<Link2 size={13} className="text-slate-400" />} label="Voice recording URL" value={voiceUrl} onChange={setVoiceUrl} placeholder="https://cdn.app/recordings/call_30912.mp3" />
        </div>
        <div className="mt-4 flex flex-wrap items-center gap-3">
          <button
            onClick={run}
            disabled={!canRun || status === "working"}
            className="inline-flex items-center gap-2 rounded-xl bg-indigo-600 px-5 py-2.5 text-sm font-semibold text-white shadow-sm shadow-indigo-200 transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {status === "working" ? <Loader2 size={16} className="animate-spin" /> : <Play size={16} />}
            {status === "working" ? "Processing..." : "Transcribe & analyze"}
          </button>
          {status === "done" && (
            <button onClick={() => { setStatus("idle"); setResult(null); }} className="text-sm font-medium text-slate-500 hover:text-slate-700">Clear result</button>
          )}
          {!isReady && (
            <span className="text-xs text-amber-600">⚠ Configure the Whisper engine below to enable transcription.</span>
          )}
        </div>
      </Card>

      <TranscribeSettings config={config} setProvider={setProvider} update={update} defaultOpen={!isReady} />

      {status === "error" && (
        <div className="flex items-start gap-3 rounded-2xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700">
          <AlertTriangle size={18} className="mt-0.5 shrink-0" />
          <div>
            <p className="font-semibold">Transcription failed</p>
            <p className="mt-0.5 text-rose-600">{error}</p>
          </div>
        </div>
      )}

      {status === "working" && (
        <Card className="p-6">
          <div className="flex items-center gap-3 text-sm text-slate-600">
            <Loader2 size={18} className="animate-spin text-indigo-500" />
            {stage}
          </div>
          <div className="mt-3 h-1.5 w-full overflow-hidden rounded-full bg-slate-100">
            <div className="h-full w-1/3 animate-pulse rounded-full bg-gradient-to-r from-indigo-500 to-violet-500" />
          </div>
        </Card>
      )}

      {status === "done" && result && payload && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <FlagTile
              icon={Phone}
              label="Phone number shared"
              count={result.analysis.pii.filter((p) => p.type === "phone" || p.type === "sensitive-number").length}
              desc="Digits (4+) spoken in the call"
              tone={FLAG_TONES[payload.flags.phone_shared ? "blue" : "muted"]}
              active={payload.flags.phone_shared}
            />
            <FlagTile
              icon={Flame}
              label="Abuse / Gali"
              count={result.analysis.stats.profanity}
              desc="Profanity across languages"
              tone={FLAG_TONES[payload.flags.abuse_detected ? "amber" : "muted"]}
              active={payload.flags.abuse_detected}
            />
            <FlagTile
              icon={ShieldAlert}
              label="Threat / Dhamki"
              count={result.analysis.stats.threat}
              desc="Violent or intimidating words"
              tone={FLAG_TONES[payload.flags.threat_detected ? "red" : "muted"]}
              active={payload.flags.threat_detected}
            />
          </div>

          <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
            <Card className="flex flex-col items-center justify-center p-5">
              <RiskGauge score={result.analysis.riskScore} />
              <div className="mt-1">
                <RiskBadge level={result.analysis.riskLevel} />
              </div>
              <div className="mt-3 flex flex-wrap justify-center gap-1.5">
                {(["profanity", "threat", "self-harm", "scam", "pii"] as const).map((c) => (
                  <span key={c} className={cn("inline-flex items-center gap-1 rounded-md px-2 py-0.5 text-[11px] font-semibold", CATEGORY_META[c].bg, CATEGORY_META[c].text)}>
                    <span className={cn("h-1.5 w-1.5 rounded-full", CATEGORY_META[c].dot)} />
                    {result.analysis.stats[c]}
                  </span>
                ))}
              </div>
            </Card>
            
            {result.metrics && (
              <Card className="flex flex-col p-5 lg:col-span-2">
                <CardHeader title="Speech Analytics" subtitle="Talk-time and silence breakdown" icon={<Activity size={18} />} />
                <div className="mt-4 grid grid-cols-3 gap-4">
                  <div className="rounded-xl border border-indigo-100 bg-indigo-50/50 p-4">
                    <div className="flex items-center gap-2 text-sm font-medium text-indigo-600">
                      <Mic size={16} /> Agent Talk Time
                    </div>
                    <div className="mt-2 text-2xl font-bold text-slate-800">
                      {Math.round(result.metrics.agent_talk_time)}s
                    </div>
                    <div className="text-xs text-slate-500">
                      {Math.round((result.metrics.agent_talk_time / result.metrics.total_time) * 100)}% of call
                    </div>
                  </div>
                  <div className="rounded-xl border border-sky-100 bg-sky-50/50 p-4">
                    <div className="flex items-center gap-2 text-sm font-medium text-sky-600">
                      <Users size={16} /> Customer Talk Time
                    </div>
                    <div className="mt-2 text-2xl font-bold text-slate-800">
                      {Math.round(result.metrics.customer_talk_time)}s
                    </div>
                    <div className="text-xs text-slate-500">
                      {Math.round((result.metrics.customer_talk_time / result.metrics.total_time) * 100)}% of call
                    </div>
                  </div>
                  <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
                    <div className="flex items-center gap-2 text-sm font-medium text-slate-600">
                      <VolumeX size={16} /> Dead Air (Silence)
                    </div>
                    <div className="mt-2 text-2xl font-bold text-slate-800">
                      {Math.round(result.metrics.silence_time)}s
                    </div>
                    <div className="text-xs text-slate-500">
                      {Math.round((result.metrics.silence_time / result.metrics.total_time) * 100)}% of call
                    </div>
                  </div>
                </div>
              </Card>
            )}

            <Card className="lg:col-span-3">
              <CardHeader
                title="n8n-ready payload"
                subtitle="The JSON your workflow receives back"
                icon={<Webhook size={18} />}
                action={
                  <button onClick={copyPayload} className="inline-flex items-center gap-1.5 rounded-lg bg-indigo-600 px-3 py-1.5 text-xs font-semibold text-white transition hover:bg-indigo-700">
                    {copied ? <Check size={13} /> : <Copy size={13} />}
                    {copied ? "Copied" : "Copy JSON"}
                  </button>
                }
              />
              <div className="max-h-[280px] overflow-auto px-5 pb-5 pt-3">
                <pre className="rounded-xl bg-slate-900 p-4 text-[11px] leading-relaxed text-slate-100">
                  <code>{JSON.stringify(payload, null, 2)}</code>
                </pre>
              </div>
            </Card>
          </div>

          <Card>
            <CardHeader
              title="Analyzed Transcript"
              subtitle={
                "adviser " + (result.adviserId || "—") +
                " · user " + (result.userId || "—") +
                (result.language ? " · lang " + result.language : "") +
                " · numbers " + (maskPii ? "masked" : "revealed")
              }
              icon={<ScanText size={18} />}
              action={
                <button onClick={() => setMaskPii((v) => !v)} className="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 px-2.5 py-1.5 text-xs font-semibold text-slate-600 transition hover:bg-slate-50">
                  {maskPii ? <EyeOff size={13} /> : <Eye size={13} />}
                  {maskPii ? "Masked" : "Revealed"}
                </button>
              }
            />
            <div className="p-5">
              {result.turns && result.turns.length > 0 ? (
                <div className="space-y-4">
                  {result.turns.map((t, i) => {
                    const turnResult = analyze(t.text);
                    const isAgent = t.speaker === "agent";
                    
                    const formatTime = (sec?: number) => {
                      if (sec === undefined) return "00:00.00";
                      const m = Math.floor(sec / 60).toString().padStart(2, '0');
                      const s = Math.floor(sec % 60).toString().padStart(2, '0');
                      const ms = Math.floor((sec % 1) * 100).toString().padStart(2, '0');
                      return `${m}:${s}.${ms}`;
                    };

                    return (
                      <div key={i} className="mb-6 flex flex-col font-sans text-sm text-slate-800">
                        <div className="font-semibold text-slate-900">
                          {isAgent ? "Speaker 0" : "Speaker 1"}
                        </div>
                        <div className="mb-1 font-mono text-slate-500">
                          {formatTime(t.start_time)}
                        </div>
                        <div className="text-base text-slate-800">
                          <HighlightedTranscript text={t.text} findings={turnResult.findings} pii={turnResult.pii} maskPii={maskPii} />
                        </div>
                        <div className="mt-1 font-mono text-slate-500">
                          {formatTime(t.end_time)}
                        </div>
                      </div>
                    );
                  })}
                </div>
              ) : (
                <div className="rounded-xl bg-slate-50 p-5 text-sm">
                  <HighlightedTranscript text={result.transcript} findings={result.analysis.findings} pii={result.analysis.pii} maskPii={maskPii} />
                </div>
              )}
            </div>
          </Card>
        </div>
      )}

      {status === "idle" && (
        <Card className="p-8">
          <div className="flex flex-col items-center justify-center text-center">
            <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-indigo-50 text-indigo-600">
              <Radio size={26} />
            </div>
            <h3 className="mt-4 text-base font-semibold text-slate-900">Ready to monitor a call</h3>
            <p className="mt-1 max-w-md text-sm text-slate-500">
              Enter the adviser ID, user ID and voice recording URL above, then run. The agent transcribes with Whisper and immediately highlights any shared phone numbers, abuse or threats.
            </p>
          </div>
        </Card>
      )}
    </div>
  );
}
