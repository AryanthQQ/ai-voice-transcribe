// ============================================================================
//  Whisper transcription service
//  Sends an audio URL/file to a Whisper-compatible endpoint and returns text.
//  Default + recommended provider is a LOCAL faster-whisper server running the
//  large-v3 model in int8 compute type (offline, $0 per minute). Also supports
//  Groq (large-v3) and OpenAI as cloud fallbacks. Works from the browser.
// ============================================================================

export type Provider = "local" | "groq" | "openai" | "custom";

export interface TranscribeConfig {
  provider: Provider;
  apiKey: string;
  endpoint: string;
  model: string;
  translate: boolean; // translate audio to English instead of native transcription
  vadFilter: boolean; // Voice Activity Detection — drop silence, prevent hallucination
  language?: string; // optional ISO hint (e.g. "hi")
}

export interface TranscribeOutput {
  text: string;
  language?: string;
  durationSec?: number;
  turns?: Array<{ speaker: string; time: string; text: string }>;
}

export interface ProviderPreset {
  label: string;
  blurb: string;
  defaultEndpoint: string;
  defaultModel: string;
  keyUrl: string;
  keyLabel: string;
}

export const PROVIDER_PRESETS: Record<Provider, ProviderPreset> = {
  local: {
    label: "Local faster-whisper",
    blurb: "large-v3 · int8 · offline · $0/min. Runs on your own CPU/laptop.",
    defaultEndpoint: "http://localhost:8001/transcribe",
    defaultModel: "large-v3",
    keyUrl: "",
    keyLabel: "API Key (optional)",
  },
  groq: {
    label: "Groq — Whisper large-v3",
    blurb: "Cloud fallback. Fastest hosted large-v3, free tier.",
    defaultEndpoint: "https://api.groq.com/openai/v1/audio/transcriptions",
    defaultModel: "whisper-large-v3",
    keyUrl: "https://console.groq.com/keys",
    keyLabel: "Groq API Key",
  },
  openai: {
    label: "OpenAI — Whisper",
    blurb: "Official OpenAI Whisper API.",
    defaultEndpoint: "https://api.openai.com/v1/audio/transcriptions",
    defaultModel: "whisper-1",
    keyUrl: "https://platform.openai.com/api-keys",
    keyLabel: "OpenAI API Key",
  },
  custom: {
    label: "Custom endpoint",
    blurb: "Any OpenAI-compatible /audio/transcriptions endpoint.",
    defaultEndpoint: "http://localhost:8001/transcribe",
    defaultModel: "whisper-large-v3",
    keyUrl: "",
    keyLabel: "API Key (optional)",
  },
};

function extFromType(type: string): string {
  const t = (type || "").toLowerCase();
  if (t.includes("webm")) return "webm";
  if (t.includes("mp4") || t.includes("m4a") || t.includes("aac")) return "m4a";
  if (t.includes("mpeg") || t.includes("mp3")) return "mp3";
  if (t.includes("wav")) return "wav";
  if (t.includes("ogg")) return "ogg";
  if (t.includes("flac")) return "flac";
  return "webm";
}

function extFromUrl(url: string): string | null {
  try {
    const u = new URL(url);
    const last = u.pathname.split("/").filter(Boolean).pop() || "";
    const m = last.match(/\.([a-z0-9]{2,4})$/i);
    return m ? m[1].toLowerCase() : null;
  } catch {
    return null;
  }
}

export class TranscribeError extends Error {
  hint?: string;
  constructor(message: string, hint?: string) {
    super(message);
    this.name = "TranscribeError";
    this.hint = hint;
  }
}

/**
 * Transcribe an audio Blob/File via a Whisper-compatible endpoint.
 */
export async function transcribeBlob(
  blob: Blob,
  filename: string,
  config: TranscribeConfig
): Promise<TranscribeOutput> {
  if (!config.endpoint) throw new TranscribeError("No transcription endpoint set.");

  const isLocal = config.provider === "local" || config.provider === "custom";

  // Hosted providers (Groq/OpenAI) handle English translation via a separate
  // /audio/translations endpoint. Local faster-whisper handles it via the
  // `translate` form field (task="translate").
  let endpoint = config.endpoint;
  if (config.translate && !isLocal) {
    endpoint = config.endpoint.replace("/transcriptions", "/translations");
  }

  const fd = new FormData();
  fd.append("file", blob, filename);
  fd.append("model", config.model);
  if (!isLocal) fd.append("response_format", "json");

  // faster-whisper native params (harmless if the server ignores unknown ones)
  if (isLocal) {
    fd.append("translate", String(config.translate));
    fd.append("vad_filter", String(config.vadFilter));
    if (config.language) fd.append("language", config.language);
  } else {
    if (config.language && !config.translate) fd.append("language", config.language);
  }

  const headers: Record<string, string> = {};
  if (config.apiKey) headers["Authorization"] = `Bearer ${config.apiKey}`;

  let res: Response;
  try {
    res = await fetch(endpoint, { method: "POST", headers, body: fd });
  } catch {
    throw new TranscribeError(
      `Could not reach the endpoint at ${endpoint}.`,
      isLocal
        ? "Start your faster-whisper FastAPI server and enable CORS for this page."
        : "Check the endpoint URL and your network connection."
    );
  }

  if (!res.ok) {
    let detail = "";
    try {
      const err = await res.json();
      detail = err?.error?.message || err?.message || err?.detail || JSON.stringify(err);
    } catch {
      detail = await res.text().catch(() => "");
    }
    if (res.status === 401) {
      throw new TranscribeError("Authentication failed (401).", "Check your API key for the selected provider.");
    }
    if (res.status === 404) {
      throw new TranscribeError(
        `Endpoint not found (404) at ${endpoint}.`,
        isLocal ? "Make sure the server exposes POST /transcribe at this URL." : undefined
      );
    }
    if (res.status === 413) {
      throw new TranscribeError("Audio file too large for this endpoint.", "Trim or compress the recording.");
    }
    throw new TranscribeError(
      `Endpoint returned ${res.status} ${res.statusText}${detail ? `: ${detail}` : ""}`,
      detail ? undefined : "Verify the endpoint URL and model name."
    );
  }

  const ct = res.headers.get("content-type") || "";
  if (ct.includes("application/json")) {
    const data = await res.json();
    let text = "";
    if (Array.isArray(data.segments)) text = data.segments.map((s: any) => s.text).join(" ");
    text = (text || data.text || data.transcription || data.transcript || data.result || "").trim();
    return {
      text,
      language: data.language || data.detected_language,
      durationSec: typeof data.duration === "number" ? data.duration : undefined,
      turns: data.turns,
    };
  }
  return { text: (await res.text()).trim() };
}

/**
 * Fetch audio from a URL and transcribe it. The URL must allow CORS reads
 * (most cloud storage / signed URLs do).
 */
export async function transcribeUrl(
  audioUrl: string,
  config: TranscribeConfig
): Promise<TranscribeOutput> {
  let blob: Blob;
  try {
    const audioRes = await fetch(audioUrl);
    if (!audioRes.ok) {
      throw new TranscribeError(
        `Could not download audio (HTTP ${audioRes.status}).`,
        "Check that the voice recording URL is valid and publicly readable."
      );
    }
    blob = await audioRes.blob();
  } catch (e: any) {
    if (e instanceof TranscribeError) throw e;
    throw new TranscribeError(
      "Failed to fetch the voice recording URL.",
      "CORS may be blocking the download. Host the audio on a CORS-enabled bucket, or pass a direct downloadable URL."
    );
  }

  const ext = extFromUrl(audioUrl) || extFromType(blob.type);
  const name = `recording.${ext}`;
  return transcribeBlob(blob, name, config);
}

/**
 * Lightweight reachability check for a local backend. Tries common health
 * paths and a bare OPTIONS to the endpoint. Returns ok + a short message.
 */
export async function testConnection(
  config: TranscribeConfig
): Promise<{ ok: boolean; message: string }> {
  if (!config.endpoint) return { ok: false, message: "No endpoint set." };

  let base: string;
  try {
    const u = new URL(config.endpoint);
    base = `${u.protocol}//${u.host}`;
  } catch {
    return { ok: false, message: "Invalid endpoint URL." };
  }

  const candidates = [
    `${base}/health`,
    `${base}/`,
    `${base}/docs`,
    config.endpoint,
  ];

  for (const url of candidates) {
    try {
      const res = await fetch(url, { method: "GET", mode: "cors" });
      // Any successful HTTP exchange means the server is reachable.
      if (res.status < 500) {
        return {
          ok: true,
          message: `Reachable — server responded ${res.status} at ${new URL(url).pathname}.`,
        };
      }
    } catch {
      // try next candidate
    }
  }
  return {
    ok: false,
    message: `No response from ${base}. Start the faster-whisper server and enable CORS.`,
  };
}
