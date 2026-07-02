import type { AnalysisResult } from "../lib/analyzer";
import type { TranscribeConfig } from "../lib/transcribe";

export interface AgentResult {
  adviserId: string;
  userId: string;
  voiceUrl: string;
  transcript: string;
  language?: string;
  analysis: AnalysisResult;
  turns?: Array<{ speaker: string; text: string; time: string }>;
  metrics?: {
    agent_talk_time: number;
    customer_talk_time: number;
    silence_time: number;
    total_time: number;
  };
}

export function buildPayload(r: AgentResult, config: TranscribeConfig) {
  const a = r.analysis;
  const phoneItems = a.pii.filter((p) => p.type === "phone" || p.type === "sensitive-number");
  const abuse = a.findings.filter((f) => f.category === "profanity");
  const threats = a.findings.filter((f) => f.category === "threat");
  return {
    reciever_ref_code: r.adviserId,
    sender_ref_code: r.userId,
    adviser_id: r.adviserId,
    user_id: r.userId,
    voice_url: r.voiceUrl,
    model: config.model,
    provider: config.provider,
    detected_language: r.language || null,
    transcript: r.transcript,
    risk_score: a.riskScore,
    risk_level: a.riskLevel,
    flags: {
      phone_shared: phoneItems.length > 0,
      abuse_detected: abuse.length > 0,
      threat_detected: threats.length > 0,
      self_harm_detected: a.stats["self-harm"] > 0,
      scam_detected: a.stats.scam > 0,
    },
    phone_numbers: phoneItems.map((p) => p.masked),
    abuse_terms: abuse.map((f) => f.match),
    threat_phrases: threats.map((f) => f.match),
    counts: a.stats,
    metrics: r.metrics,
    findings: a.findings.map((f) => ({
      category: f.category,
      label: f.label,
      match: f.match,
      severity: f.severity,
      language: f.language,
    })),
  };
}

export const FLAG_TONES: Record<string, string> = {
  blue: "border-blue-300 bg-blue-50 text-blue-700",
  amber: "border-amber-300 bg-amber-50 text-amber-700",
  red: "border-rose-300 bg-rose-50 text-rose-700",
  muted: "border-slate-200 bg-white text-slate-400",
};
