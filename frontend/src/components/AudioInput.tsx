import { useEffect, useRef, useState } from "react";
import {
  Upload,
  Mic,
  Square,
  Loader2,
  AlertCircle,
  FileAudio,
  Radio,
  CheckCircle2,
  RotateCcw,
} from "lucide-react";
import { Card } from "./ui";
import { cn } from "../utils/cn";
import { useTranscribeSettings } from "../lib/useTranscribeSettings";
import { transcribeBlob, TranscribeError } from "../lib/transcribe";
import { TranscribeSettings } from "./TranscribeSettings";
import { useGlobalStore, globalStore } from "../lib/globalStore";

type SubMode = "upload" | "record";

const LANGS = [
  { code: "en-US", label: "English (US)" },
  { code: "en-IN", label: "English (India)" },
  { code: "hi-IN", label: "Hindi" },
  { code: "ta-IN", label: "Tamil" },
  { code: "te-IN", label: "Telugu" },
];

export function AudioInput({
  onComplete,
}: {
  onComplete: (transcript: string, sourceLabel: string) => void;
}) {
  const [mode, setMode] = useState<SubMode>("upload");

  const { config, setProvider, update, isReady } = useTranscribeSettings();

  const [file, setFile] = useState<File | null>(null);
  const [fileUrl, setFileUrl] = useState<string | null>(null);
  const [dragging, setDragging] = useState(false);

  const [listening, setListening] = useState(false);
  const [liveText, setLiveText] = useState("");
  const [lang, setLang] = useState("en-US");
  const recRef = useRef<SpeechRecognition | null>(null);
  const finalRef = useRef<string>("");
  const inputRef = useRef<HTMLInputElement>(null);

  const speechSupported =
    typeof window !== "undefined" && !!(window.SpeechRecognition || window.webkitSpeechRecognition);

  useEffect(() => {
    return () => {
      if (fileUrl) URL.revokeObjectURL(fileUrl);
      recRef.current?.abort();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const onSelectFile = (f: File | null) => {
    if (!f) return;
    if (fileUrl) URL.revokeObjectURL(fileUrl);
    setFile(f);
    setFileUrl(URL.createObjectURL(f));
    globalStore.setState({ status: "idle", error: "" });
  };

  const { status, error, fileMode } = useGlobalStore();

  const transcribeFile = async () => {
    if (!file) return;
    globalStore.transcribeAudioFile(file, file.name, config);
  };

  const startRecording = () => {
    if (!speechSupported) return;
    const Ctor = window.SpeechRecognition || window.webkitSpeechRecognition!;
    const rec = new Ctor();
    rec.lang = lang;
    rec.continuous = true;
    rec.interimResults = true;
    rec.maxAlternatives = 1;

    finalRef.current = "";
    setLiveText("");

    rec.onstart = () => setListening(true);
    rec.onresult = (event: SpeechRecognitionEvent) => {
      let interim = "";
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const r = event.results[i];
        if (r.isFinal) finalRef.current += r[0].transcript + " ";
        else interim += r[0].transcript;
      }
      setLiveText((finalRef.current + interim).trim());
    };
    rec.onerror = (event: SpeechRecognitionErrorEvent) => {
      if (event.error === "no-speech") return;
      if (event.error === "not-allowed" || event.error === "service-not-allowed") {
        globalStore.setState({
          error: "Microphone permission denied. Allow mic access and try again.",
          status: "error"
        });
      }
    };
    rec.onend = () => setListening(false);

    recRef.current = rec;
    rec.start();
  };

  const stopRecording = () => {
    recRef.current?.stop();
    const text = finalRef.current.trim();
    if (text) onComplete(text, "Live recording (mic)");
    else {
      globalStore.setState({
        error: "No speech was captured. Try again and speak clearly.",
        status: "error"
      });
    }
  };

  return (
    <Card className="p-5">
      <div className="mb-5 flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="flex items-center gap-2 text-base font-semibold text-slate-900">
            <Radio size={18} className="text-indigo-500" /> Audio Input
          </h2>
          <p className="mt-0.5 text-sm text-slate-500">
            Upload an audio file (transcribed by your Whisper backend) or record live from the mic.
          </p>
        </div>
        <div className="flex rounded-xl bg-slate-100 p-1">
          <button
            onClick={() => setMode("upload")}
            className={cn(
              "flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-sm font-medium transition",
              mode === "upload" ? "bg-white text-slate-900 shadow-sm" : "text-slate-500 hover:text-slate-700"
            )}
          >
            <Upload size={15} /> Upload file
          </button>
          <button
            onClick={() => setMode("record")}
            disabled={!speechSupported}
            className={cn(
              "flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-sm font-medium transition",
              mode === "record" ? "bg-white text-slate-900 shadow-sm" : "text-slate-500 hover:text-slate-700",
              !speechSupported && "cursor-not-allowed opacity-40"
            )}
            title={!speechSupported ? "Web Speech API not available in this browser" : undefined}
          >
            <Mic size={15} /> Live record
          </button>
        </div>
      </div>

      {mode === "upload" ? (
        <div className="space-y-4">
          <div
            onDragOver={(e) => {
              e.preventDefault();
              setDragging(true);
            }}
            onDragLeave={() => setDragging(false)}
            onDrop={(e) => {
              e.preventDefault();
              setDragging(false);
              onSelectFile(e.dataTransfer.files?.[0] ?? null);
            }}
            onClick={() => inputRef.current?.click()}
            className={cn(
              "flex cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed px-6 py-8 text-center transition",
              dragging
                ? "border-indigo-400 bg-indigo-50"
                : file
                ? "border-emerald-300 bg-emerald-50/50"
                : "border-slate-300 bg-slate-50/50 hover:border-indigo-300 hover:bg-white"
            )}
          >
            <input
              ref={inputRef}
              type="file"
              accept="audio/*,video/*"
              className="hidden"
              onClick={(e) => { e.currentTarget.value = "" }}
              onChange={(e) => onSelectFile(e.target.files?.[0] ?? null)}
            />
            {file ? (
              <>
                <CheckCircle2 size={28} className="text-emerald-500" />
                <p className="mt-2 text-sm font-semibold text-slate-800">{file.name}</p>
                <p className="text-xs text-slate-500">{(file.size / 1024 / 1024).toFixed(2)} MB · click to replace</p>
              </>
            ) : (
              <>
                <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-indigo-100 text-indigo-600">
                  <FileAudio size={24} />
                </div>
                <p className="mt-3 text-sm font-semibold text-slate-700">
                  Drag and drop an audio file, or click to browse
                </p>
                <p className="text-xs text-slate-400">MP3, WAV, M4A, WEBM · max depends on backend</p>
              </>
            )}
          </div>

          {fileUrl && <audio controls src={fileUrl} className="w-full" />}

          <TranscribeSettings config={config} setProvider={setProvider} update={update} defaultOpen={!isReady} />

          <div className="flex flex-wrap items-center gap-3">
            <button
              onClick={transcribeFile}
              disabled={!file || (status === "processing" && fileMode) || !isReady}
              className="inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {status === "processing" && fileMode ? <Loader2 size={15} className="animate-spin" /> : <Radio size={15} />}
              {status === "done" ? "Re-transcribe" : "Transcribe with Whisper"}
            </button>
            
            {status === "done" && (
              <button
                onClick={() => {
                  setFile(null);
                  if (fileUrl) URL.revokeObjectURL(fileUrl);
                  setFileUrl(null);
                  globalStore.reset();
                }}
                className="inline-flex items-center gap-2 rounded-lg border border-slate-200 px-4 py-2 text-sm font-medium text-slate-600 transition hover:bg-slate-50"
              >
                <RotateCcw size={15} /> Reset
              </button>
            )}
          </div>
          {!isReady && (
            <p className="text-xs text-amber-600">⚠ Add your API key in the settings above to enable transcription.</p>
          )}

          {status === "error" && (
            <div className="flex items-start gap-2 rounded-xl border border-rose-200 bg-rose-50 p-3 text-xs text-rose-700">
              <AlertCircle size={15} className="mt-0.5 shrink-0" />
              <span>{error}</span>
            </div>
          )}
        </div>
      ) : (
        <div className="space-y-4">
          {!speechSupported ? (
            <div className="flex items-start gap-2 rounded-xl border border-amber-200 bg-amber-50 p-3 text-xs text-amber-700">
              <AlertCircle size={15} className="mt-0.5 shrink-0" />
              <span>
                Live recording uses the Web Speech API, which is not available in this browser. Try Chrome or Edge.
              </span>
            </div>
          ) : (
            <>
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div>
                  <label className="mb-1 block text-xs font-semibold text-slate-600">Recognition language</label>
                  <select
                    value={lang}
                    onChange={(e) => setLang(e.target.value)}
                    disabled={listening}
                    className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-700 outline-none focus:border-indigo-300 focus:ring-2 focus:ring-indigo-100 disabled:opacity-50"
                  >
                    {LANGS.map((l) => (
                      <option key={l.code} value={l.code}>
                        {l.label}
                      </option>
                    ))}
                  </select>
                </div>
                {!listening ? (
                  <button
                    onClick={startRecording}
                    className="inline-flex items-center gap-2 rounded-xl bg-rose-600 px-5 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-rose-700"
                  >
                    <Mic size={16} /> Start recording
                  </button>
                ) : (
                  <button
                    onClick={stopRecording}
                    className="inline-flex items-center gap-2 rounded-xl bg-slate-900 px-5 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-slate-800"
                  >
                    <Square size={15} className="fill-current" /> Stop and analyze
                  </button>
                )}
              </div>

              <div className="min-h-[140px] rounded-xl border border-slate-200 bg-slate-50/50 p-4">
                <div className="mb-2 flex items-center gap-2">
                  {listening ? (
                    <>
                      <span className="relative flex h-2.5 w-2.5">
                        <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-rose-400 opacity-75" />
                        <span className="relative inline-flex h-2.5 w-2.5 rounded-full bg-rose-500" />
                      </span>
                      <span className="text-xs font-semibold text-rose-600">Listening, speak now</span>
                    </>
                  ) : (
                    <span className="text-xs font-medium text-slate-400">
                      {liveText ? "Captured transcript preview" : "Press start and speak, text appears here live."}
                    </span>
                  )}
                </div>
                <p className="text-sm leading-relaxed text-slate-700">
                  {liveText || <span className="text-slate-300">No speech yet...</span>}
                </p>
              </div>

              {status === "error" && (
                <div className="flex items-start gap-2 rounded-xl border border-rose-200 bg-rose-50 p-3 text-xs text-rose-700">
                  <AlertCircle size={15} className="mt-0.5 shrink-0" />
                  <span>{error}</span>
                </div>
              )}
              <p className="text-xs text-slate-400">
                Tip: live recording transcribes in-browser via the Web Speech API. For long files or 99-language
                accuracy, upload and use your Whisper backend.
              </p>
            </>
          )}
        </div>
      )}
    </Card>
  );
}
