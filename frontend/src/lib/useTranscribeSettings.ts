import { useEffect, useState } from "react";
import { PROVIDER_PRESETS, type Provider, type TranscribeConfig } from "./transcribe";

const STORAGE_KEY = "speechiq.transcribe.config.v2";

export function defaultConfig(): TranscribeConfig {
  return {
    provider: "local",
    apiKey: "",
    endpoint: PROVIDER_PRESETS.local.defaultEndpoint,
    model: PROVIDER_PRESETS.local.defaultModel,
    translate: true, // large-v3 translates any language → English
    vadFilter: true, // drop silence, prevent hallucinations
    language: "",
  };
}

function load(): TranscribeConfig {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return defaultConfig();
    const parsed = JSON.parse(raw);
    return { ...defaultConfig(), ...parsed };
  } catch {
    return defaultConfig();
  }
}

export function useTranscribeSettings() {
  const [config, setConfig] = useState<TranscribeConfig>(() => {
    if (typeof window === "undefined") return defaultConfig();
    return load();
  });

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(config));
    } catch {
      /* ignore quota errors */
    }
  }, [config]);

  const setProvider = (provider: Provider) => {
    setConfig((c) => {
      // Only auto-apply the preset endpoint/model when the user is still on a
      // preset value (so we never overwrite a custom URL they typed).
      const preset = PROVIDER_PRESETS[provider];
      const wasPresetEndpoint = Object.values(PROVIDER_PRESETS).some(
        (p) => p.defaultEndpoint === c.endpoint
      );
      const wasPresetModel = Object.values(PROVIDER_PRESETS).some(
        (p) => p.defaultModel === c.model
      );
      return {
        ...c,
        provider,
        endpoint: wasPresetEndpoint || c.provider === "custom" ? preset.defaultEndpoint : c.endpoint,
        model: wasPresetModel ? preset.defaultModel : c.model,
      };
    });
  };

  const update = (patch: Partial<TranscribeConfig>) => setConfig((c) => ({ ...c, ...patch }));

  // Local faster-whisper needs only an endpoint (no API key). Cloud needs both.
  const isReady =
    config.provider === "local" || config.provider === "custom"
      ? !!config.endpoint
      : !!config.apiKey && !!config.endpoint;

  return { config, setProvider, update, isReady };
}
