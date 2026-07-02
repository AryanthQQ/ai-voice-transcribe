// ============================================================================
//  Sample diarized transcripts for the Analyze tool.
//  These represent what faster-whisper (large-v3) + a diarizer would output.
//  The analyzer runs on the joined `rawText`, so detection is live & real.
// ============================================================================

export interface DiarizedTurn {
  speaker: "customer" | "agent";
  time: string;
  text: string;
}

export interface SampleCall {
  id: string;
  title: string;
  description: string;
  language: string;
  detectedLanguage: string;
  durationSec: number;
  turns: DiarizedTurn[];
}

export const SAMPLE_CALLS: SampleCall[] = [
  {
    id: "telecom-dispute",
    title: "Aggressive Customer — Telecom Dispute",
    description: "Customer escalates over a billing error. High profanity & threat density.",
    language: "Hindi + English",
    detectedLanguage: "hi",
    durationSec: 184,
    turns: [
      { speaker: "agent", time: "00:03", text: "Thank you for calling AirNet support, this is Rahul speaking. How may I help you today?" },
      { speaker: "customer", time: "00:09", text: "How may you help me? You people have charged me three times this month, you chutiya!" },
      { speaker: "agent", time: "00:16", text: "Sir, I completely understand the frustration. Let me pull up your account. Can you confirm the registered number?" },
      { speaker: "customer", time: "00:24", text: "It is +91 98765 43210, and my email is arun.sharma@gmail.com. Now fix this or I swear jaan se maar dunga, I'll come to your office." },
      { speaker: "agent", time: "00:36", text: "Sir, please calm down. Threatening language is not necessary. I see the duplicate charge — I can refund it right now, but I'll need the OTP sent to your phone for verification." },
      { speaker: "customer", time: "00:50", text: "OTP? This is bullshit. You madarchod people always find a way to scam. Just refund my money." },
      { speaker: "agent", time: "00:58", text: "The refund is genuine, sir. Once you share the OTP the money goes back to your card ending in 4451." },
    ],
  },
  {
    id: "bank-phishing",
    title: "Bank OTP Phishing — Impersonation",
    description: "Caller impersonates bank officials to harvest OTP, CVV and card details.",
    language: "English + Hindi",
    detectedLanguage: "en",
    durationSec: 142,
    turns: [
      { speaker: "customer", time: "00:02", text: "Hello? Who is this?" },
      { speaker: "agent", time: "00:05", text: "Hello ma'am, this is the fraud department of your bank. Your card has been suspended due to suspicious activity." },
      { speaker: "customer", time: "00:14", text: "Oh no, what do I do? My card number is 4532 7891 2045 6783." },
      { speaker: "agent", time: "00:21", text: "Thank you. To verify, please tell me the CVV on the back and the OTP you just received." },
      { speaker: "customer", time: "00:30", text: "The CVV is 742 and the OTP is 8841. Am I safe now? I also have 1234 5678 9012 as my account reference." },
      { speaker: "agent", time: "00:41", text: "Almost done, ma'am. Just one more thing — you have won our annual lucky draw prize of two lakh rupees, we just need a small processing transfer." },
      { speaker: "customer", time: "00:52", text: "Wait, that sounds like a scam. I'm calling the police." },
    ],
  },
  {
    id: "mental-health",
    title: "Distressed Caller — Wellness Line",
    description: "Caller in crisis expresses self-harm ideation. Requires immediate escalation.",
    language: "English",
    detectedLanguage: "en",
    durationSec: 96,
    turns: [
      { speaker: "agent", time: "00:02", text: "You've reached the wellness support line. I'm here to listen. How are you feeling right now?" },
      { speaker: "customer", time: "00:09", text: "I don't know anymore. I just want to die. There's no reason to live, everything is falling apart." },
      { speaker: "agent", time: "00:18", text: "I hear how much pain you're in, and I'm so glad you called. You're not alone. Can you tell me your name?" },
      { speaker: "customer", time: "00:26", text: "It's Meera. Sometimes I think about ending my life. I hurt myself last night and I'm scared." },
      { speaker: "agent", time: "00:36", text: "Thank you for trusting me, Meera. That took courage. I'm going to stay with you and connect you to a crisis counsellor right now. You matter." },
    ],
  },
  {
    id: "clean-support",
    title: "Order Support — Clean Conversation",
    description: "Routine e-commerce follow-up. No risk signals detected.",
    language: "English",
    detectedLanguage: "en",
    durationSec: 118,
    turns: [
      { speaker: "agent", time: "00:02", text: "Hi, this is Priya from ShopEasy. I'm calling about your recent order number 4471. Is this a good time?" },
      { speaker: "customer", time: "00:10", text: "Yes, perfect timing. I wanted to check when my delivery will arrive." },
      { speaker: "agent", time: "00:15", text: "Your order is out for delivery and should reach you by 6 PM today. You'll get a tracking SMS shortly." },
      { speaker: "customer", time: "00:23", text: "That's wonderful, thank you so much for the quick update." },
      { speaker: "agent", time: "00:27", text: "My pleasure! Is there anything else I can help you with today?" },
      { speaker: "customer", time: "00:31", text: "No, that's all. Have a great day, Priya." },
    ],
  },
];

export function sampleToRawText(call: SampleCall): string {
  return call.turns.map((t) => t.text).join(" ");
}

export function formatDuration(sec: number): string {
  const m = Math.floor(sec / 60);
  const s = sec % 60;
  return `${m}:${s.toString().padStart(2, "0")}`;
}
