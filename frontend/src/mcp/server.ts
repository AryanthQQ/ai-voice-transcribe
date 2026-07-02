import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { CallToolRequestSchema, ListToolsRequestSchema } from "@modelcontextprotocol/sdk/types.js";
import { detectAbuse, detectPhoneNumbers } from "../lib/analyzer";
import fs from "fs";
import axios from "axios";
import FormData from "form-data";

const server = new Server(
  {
    name: "ai-speech-analytics",
    version: "1.0.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// Define Tools
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: "analyze_text",
        description: "Analyzes a given text for profanity, abuse, threats, scams, and PII (phone numbers) across global languages.",
        inputSchema: {
          type: "object",
          properties: {
            text: {
              type: "string",
              description: "The transcript or text to analyze.",
            },
          },
          required: ["text"],
        },
      },
      {
        name: "transcribe_audio",
        description: "Transcribes an audio file into English text using the Faster-Whisper backend.",
        inputSchema: {
          type: "object",
          properties: {
            filePath: {
              type: "string",
              description: "Absolute path to the audio file on the system.",
            },
            language: {
              type: "string",
              description: "Language code (e.g. 'auto', 'hi', 'en'). Defaults to 'auto'.",
            }
          },
          required: ["filePath"],
        },
      }
    ],
  };
});

// Handle Tool Execution
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  if (name === "analyze_text") {
    const text = args?.text as string;
    if (!text) throw new Error("Missing 'text' argument");

    // Convert string to word objects expected by analyzer
    const wordObjs = text.split(/\s+/).map(w => ({ word: w, start: 0, end: 1 }));
    
    const abuse = detectAbuse(wordObjs);
    const pii = detectPhoneNumbers(text, wordObjs);

    return {
      content: [
        {
          type: "text",
          text: JSON.stringify({ abuse, pii }, null, 2),
        },
      ],
    };
  }

  if (name === "transcribe_audio") {
    const filePath = args?.filePath as string;
    const language = (args?.language as string) || "auto";
    
    if (!filePath || !fs.existsSync(filePath)) {
      throw new Error(`File not found at path: ${filePath}`);
    }

    try {
      const form = new FormData();
      form.append("file", fs.createReadStream(filePath));
      form.append("language", language);

      const response = await axios.post("http://localhost:8000/transcribe", form, {
        headers: form.getHeaders(),
      });

      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(response.data, null, 2),
          },
        ],
      };
    } catch (error: any) {
      return {
        content: [
          {
            type: "text",
            text: `Transcription failed: ${error.message}`,
          },
        ],
      };
    }
  }

  throw new Error(`Unknown tool: ${name}`);
});

// Start Server
async function run() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("AI Speech Analytics MCP Server running on stdio");
}

run().catch(console.error);
