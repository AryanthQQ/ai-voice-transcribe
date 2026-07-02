import { useEffect, useState } from "react";
import type { AnalysisResult } from "./analyzer";
import type { SampleCall } from "../data/samples";
import { analyze } from "./analyzer";
import { transcribeBlob, TranscribeError, TranscribeConfig } from "./transcribe";

type GlobalState = {
  status: "idle" | "processing" | "done" | "error";
  error: string;
  step: number;
  result: AnalysisResult | null;
  analyzedText: string;
  analyzedSample: SampleCall | null;
  sourceLabel: string;
  fileMode: boolean; // true if it's a real file being transcribed, so we can show a spinner in AudioInput
};

let state: GlobalState = {
  status: "idle",
  error: "",
  step: 0,
  result: null,
  analyzedText: "",
  analyzedSample: null,
  sourceLabel: "",
  fileMode: false
};

type Listener = () => void;
let listeners: Listener[] = [];

export const globalStore = {
  getState: () => state,
  setState: (newState: Partial<GlobalState>) => {
    state = { ...state, ...newState };
    listeners.forEach((l) => l());
  },
  subscribe: (listener: Listener) => {
    listeners.push(listener);
    return () => {
      listeners = listeners.filter((l) => l !== listener);
    };
  },
  reset: () => {
    globalStore.setState({
      status: "idle",
      error: "",
      step: 0,
      result: null,
      analyzedText: "",
      analyzedSample: null,
      sourceLabel: "",
      fileMode: false
    });
  },
  // Runs the mock analysis for sample/paste
  runAnalysisSequence: (text: string, sample: SampleCall | null, label: string) => {
    globalStore.setState({
      status: "processing",
      step: 0,
      result: null,
      sourceLabel: label,
      analyzedSample: sample,
      fileMode: false,
      error: ""
    });

    const STEPS_COUNT = 6;
    for (let i = 0; i < STEPS_COUNT; i++) {
      setTimeout(() => {
        globalStore.setState({ step: i });
      }, i * 260);
    }
    
    setTimeout(() => {
      globalStore.setState({
        result: analyze(text),
        analyzedText: text,
        status: "done"
      });
    }, STEPS_COUNT * 260 + 200);
  },
  // Runs the actual transcription network call
  transcribeAudioFile: async (file: Blob, filename: string, config: TranscribeConfig) => {
    globalStore.setState({
      status: "processing",
      error: "",
      sourceLabel: `Uploaded: ${filename}`,
      fileMode: true,
      result: null,
      analyzedText: "",
      analyzedSample: null
    });

    try {
      const out = await transcribeBlob(file, filename, config);
      if (!out.text) throw new TranscribeError("Whisper returned an empty transcript.");
      
      const text = out.text.trim();
      globalStore.setState({
        result: analyze(text),
        analyzedText: text,
        status: "done",
        analyzedSample: out.turns ? {
           id: "uploaded",
           title: filename,
           description: "Uploaded file",
           language: "auto",
           detectedLanguage: out.language || "en",
           durationSec: out.durationSec || 0,
           turns: out.turns as any
        } : null
      });
    } catch (e: any) {
      const errMsg = e instanceof TranscribeError
          ? e.message + (e.hint ? " — " + e.hint : "")
          : e?.message || "Transcription failed.";
          
      globalStore.setState({
        status: "error",
        error: errMsg
      });
    }
  },
  // Handle raw text (like live mic results)
  handleRawText: (text: string, label: string) => {
    const t = text.trim();
    if (!t) return;
    globalStore.setState({
      status: "done",
      result: analyze(t),
      analyzedText: t,
      sourceLabel: label,
      analyzedSample: null,
      fileMode: false,
      error: ""
    });
  }
};

export function useGlobalStore() {
  const [snap, setSnap] = useState(globalStore.getState());
  useEffect(() => {
    return globalStore.subscribe(() => setSnap(globalStore.getState()));
  }, []);
  return snap;
}
