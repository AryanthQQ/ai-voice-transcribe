import { pipeline, env } from "@huggingface/transformers";

// Disable local model loading, force remote from HF Hub (optional but good for web)
env.allowLocalModels = false;

let transcriber: any = null;

self.addEventListener("message", async (e) => {
  const { type, data } = e.data;

  if (type === "LOAD_MODEL") {
    try {
      // 1. Detect if WebGPU (Hardware Acceleration) is supported for massive speedup
      let targetDevice: any = "wasm"; // Fallback to CPU
      try {
        if (navigator.gpu) {
          const adapter = await navigator.gpu.requestAdapter();
          if (adapter) {
            targetDevice = "webgpu";
          }
        }
      } catch (e) {
        console.warn("WebGPU not available, falling back to WASM/CPU", e);
      }

      // 2. Load the lighter, much faster Tiny model
      transcriber = await pipeline(
        "automatic-speech-recognition",
        "onnx-community/whisper-tiny",
        {
          dtype: {
            encoder_model: targetDevice === "webgpu" ? "fp32" : "fp32", // fp16 better for webgpu but stick to fp32 for safety
            decoder_model_merged: "q4",
          },
          device: targetDevice,
          progress_callback: (progress: any) => {
            self.postMessage({ type: "PROGRESS", data: progress });
          },
        }
      );
      self.postMessage({ type: "LOADED", data: true, device: targetDevice });
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err);
      self.postMessage({ type: "ERROR", data: `Model load fail: ${msg}` });
    }
  }

  if (type === "TRANSCRIBE") {
    if (!transcriber) {
      self.postMessage({ type: "ERROR", data: "Model not loaded" });
      return;
    }

    try {
      const res = await transcriber(data.audio, {
        chunk_length_s: 30,
        stride_length_s: 5,
        language: data.language,
        task: data.task,
        return_timestamps: true,
        // Anti-hallucination parameters:
        no_repeat_ngram_size: 3, 
        repetition_penalty: 1.2
      });
      self.postMessage({ type: "RESULT", data: res });
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err);
      self.postMessage({ type: "ERROR", data: `Transcription fail: ${msg}` });
    }
  }
});
