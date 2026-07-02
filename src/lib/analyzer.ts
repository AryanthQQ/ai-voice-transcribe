// ============================================================================
//  AI Speech Analytics — Detection Engine (analyzer.ts)
//  Scans transcripts for: Profanity (multilingual), Threats, Self-Harm,
//  Scam/Fraud, and PII (phone, email, card, Aadhaar, SSN).
//  Fully functional — runs client-side on any pasted/produced transcript.
// ============================================================================

export type Category = "profanity" | "threat" | "self-harm" | "scam" | "pii";
export type Severity = "critical" | "high" | "medium" | "low";

export interface Finding {
  id: string;
  category: Category;
  severity: Severity;
  label: string;
  match: string; // exact matched substring
  start: number;
  end: number;
  language: string;
}

export interface PIIMatch {
  id: string;
  type: "phone" | "email" | "credit-card" | "aadhaar" | "ssn" | "iban" | "sensitive-number";
  value: string;
  masked: string;
  start: number;
  end: number;
}

export interface CategoryStat {
  category: Category;
  count: number;
}

export interface AnalysisResult {
  findings: Finding[];
  pii: PIIMatch[];
  stats: Record<Category, number>;
  riskScore: number; // 0-100
  riskLevel: "Safe" | "Moderate" | "High" | "Critical";
  wordCount: number;
  languages: string[];
}

// ---------------------------------------------------------------------------
//  Severity weights drive the risk score.
// ---------------------------------------------------------------------------
const SEVERITY_WEIGHT: Record<Severity, number> = {
  critical: 22,
  high: 12,
  medium: 6,
  low: 3,
};

// ---------------------------------------------------------------------------
//  Pattern dictionaries. Matching is case-insensitive and tolerant of
//  common obfuscations (asterisks, dots, spaces inside words).
// ---------------------------------------------------------------------------

// Profanity — English + romanized Hindi & global slurs
const PROFANITY: { word: string; lang: string }[] = [
  { word: "damn", lang: "Detected" },
  { word: "hell", lang: "Detected" },
  { word: "stupid", lang: "Detected" },
  { word: "idiot", lang: "Detected" },
  { word: "fool", lang: "Detected" },
  { word: "dumb", lang: "Detected" },
  { word: "bastard", lang: "Detected" },
  { word: "moron", lang: "Detected" },
  { word: "crap", lang: "Detected" },
  { word: "shut up", lang: "Detected" },
  { word: "loser", lang: "Detected" },
  { word: "jerk", lang: "Detected" },
  { word: "nonsense", lang: "Detected" },
  { word: "rubbish", lang: "Detected" },
  { word: "useless", lang: "Detected" },
  { word: "pathetic", lang: "Detected" },
  { word: "bloody", lang: "Detected" },
  { word: "scam", lang: "Detected" },
  { word: "fraud", lang: "Detected" },
  { word: "cheat", lang: "Detected" },
  { word: "abuse", lang: "Detected" },
  { word: "harass", lang: "Detected" },
  { word: "threaten", lang: "Detected" },
  { word: "kill", lang: "Detected" },
  { word: "hate", lang: "Detected" },
  { word: "racist", lang: "Detected" },
  { word: "sexist", lang: "Detected" },
  { word: "slur", lang: "Detected" },
  { word: "profanity", lang: "Detected" },
  { word: "vulgar", lang: "Detected" },
  { word: "obscene", lang: "Detected" },
  { word: "disgusting", lang: "Detected" },
  { word: "terrible", lang: "Detected" },
  { word: "horrible", lang: "Detected" },
  { word: "worst", lang: "Detected" },
  { word: "incompetent", lang: "Detected" },
  { word: "bewakoof", lang: "Detected" },
  { word: "gadha", lang: "Detected" },
  { word: "kamina", lang: "Detected" },
  { word: "haramkhor", lang: "Detected" },
  { word: "badtameez", lang: "Detected" },
  { word: "pagal", lang: "Detected" },
  { word: "ullu", lang: "Detected" },
  { word: "kameena", lang: "Detected" },
  { word: "saala", lang: "Detected" },
  { word: "bevakoof", lang: "Detected" },
  { word: "chutiya", lang: "Detected" },
  { word: "chutiye", lang: "Detected" },
  { word: "behenchod", lang: "Detected" },
  { word: "bhenchod", lang: "Detected" },
  { word: "madarchod", lang: "Detected" },
  { word: "madarchood", lang: "Detected" },
  { word: "अबे", lang: "Detected" },
  { word: "साला", lang: "Detected" },
  { word: "साले", lang: "Detected" },
  { word: "हरामखोर", lang: "Detected" },
  { word: "कमीना", lang: "Detected" },
  { word: "कमीने", lang: "Detected" },
  { word: "कुत्ते", lang: "Detected" },
  { word: "बेवकूफ", lang: "Detected" },
  { word: "गधा", lang: "Detected" },
  { word: "चूतिया", lang: "Detected" },
  { word: "चूतिये", lang: "Detected" },
  { word: "मादरचोद", lang: "Detected" },
  { word: "बहनचोद", lang: "Detected" },
  { word: "भोसड़ी", lang: "Detected" },
  { word: "भोसड़ीके", lang: "Detected" },
  { word: "पागल", lang: "Detected" },
  { word: "उल्लू", lang: "Detected" },
  { word: "bc", lang: "Detected" },
  { word: "mc", lang: "Detected" },
  { word: "bsdk", lang: "Detected" },
  { word: "bkl", lang: "Detected" },
  { word: "cmn", lang: "Detected" },
  { word: "mdrc", lang: "Detected" },
  { word: "gmd", lang: "Detected" },
  { word: "bhosdike", lang: "Detected" },
  { word: "bhosadike", lang: "Detected" },
  { word: "bhosidi", lang: "Detected" },
  { word: "bhosdika", lang: "Detected" },
  { word: "bhenchods", lang: "Detected" },
  { word: "behenchods", lang: "Detected" },
  { word: "madarchot", lang: "Detected" },
  { word: "machod", lang: "Detected" },
  { word: "maderchod", lang: "Detected" },
  { word: "chutya", lang: "Detected" },
  { word: "chootiya", lang: "Detected" },
  { word: "chutiapa", lang: "Detected" },
  { word: "chutyapa", lang: "Detected" },
  { word: "c*tiya", lang: "Detected" },
  { word: "chooth", lang: "Detected" },
  { word: "chootiye", lang: "Detected" },
  { word: "randi", lang: "Detected" },
  { word: "raand", lang: "Detected" },
  { word: "randwa", lang: "Detected" },
  { word: "randi-rona", lang: "Detected" },
  { word: "rndi", lang: "Detected" },
  { word: "lodu", lang: "Detected" },
  { word: "lawde", lang: "Detected" },
  { word: "lawda", lang: "Detected" },
  { word: "lavde", lang: "Detected" },
  { word: "lavda", lang: "Detected" },
  { word: "lode", lang: "Detected" },
  { word: "loda", lang: "Detected" },
  { word: "loude", lang: "Detected" },
  { word: "lund", lang: "Detected" },
  { word: "land", lang: "Detected" },
  { word: "laand", lang: "Detected" },
  { word: "bhadwa", lang: "Detected" },
  { word: "bhadwe", lang: "Detected" },
  { word: "bharwa", lang: "Detected" },
  { word: "bhadwi", lang: "Detected" },
  { word: "bhadkhau", lang: "Detected" },
  { word: "jhantu", lang: "Detected" },
  { word: "jhatu", lang: "Detected" },
  { word: "jhaantu", lang: "Detected" },
  { word: "gandu", lang: "Detected" },
  { word: "gaandu", lang: "Detected" },
  { word: "gandmare", lang: "Detected" },
  { word: "chinal", lang: "Detected" },
  { word: "chhinal", lang: "Detected" },
  { word: "tatte", lang: "Detected" },
  { word: "tatta", lang: "Detected" },
  { word: "mutthal", lang: "Detected" },
  { word: "muthal", lang: "Detected" },
  { word: "harami", lang: "Detected" },
  { word: "haraami", lang: "Detected" },
  { word: "haramjade", lang: "Detected" },
  { word: "haramzade", lang: "Detected" },
  { word: "haramzadi", lang: "Detected" },
  { word: "kutta", lang: "Detected" },
  { word: "kutiya", lang: "Detected" },
  { word: "kutte", lang: "Detected" },
  { word: "suar", lang: "Detected" },
  { word: "suwar", lang: "Detected" },
  { word: "panchod", lang: "Detected" },
  { word: "fuddu", lang: "Detected" },
  { word: "kanjar", lang: "Detected" },
  { word: "bund", lang: "Detected" },
  { word: "gashti", lang: "Detected" },
  { word: "gashtiye", lang: "Detected" },
  { word: "saleya", lang: "Detected" },
  { word: "ullu da patha", lang: "Detected" },
  { word: "zavadya", lang: "Detected" },
  { word: "zhavadya", lang: "Detected" },
  { word: "gandya", lang: "Detected" },
  { word: "lavdya", lang: "Detected" },
  { word: "bhadtya", lang: "Detected" },
  { word: "aai zawadya", lang: "Detected" },
  { word: "yedzavya", lang: "Detected" },
  { word: "bokachoda", lang: "Detected" },
  { word: "bokachuda", lang: "Detected" },
  { word: "khanir chele", lang: "Detected" },
  { word: "baal", lang: "Detected" },
  { word: "suorer baccha", lang: "Detected" },
  { word: "banchod", lang: "Detected" },
  { word: "khanki", lang: "Detected" },
  { word: "khanki magi", lang: "Detected" },
  { word: "shala", lang: "Detected" },
  { word: "thevidiya", lang: "Detected" },
  { word: "thevdiya", lang: "Detected" },
  { word: "thevidya", lang: "Detected" },
  { word: "punda", lang: "Detected" },
  { word: "pundai", lang: "Detected" },
  { word: "baadu", lang: "Detected" },
  { word: "poolu", lang: "Detected" },
  { word: "koothi", lang: "Detected" },
  { word: "ommala", lang: "Detected" },
  { word: "lanjakoduka", lang: "Detected" },
  { word: "dengu", lang: "Detected" },
  { word: "dengay", lang: "Detected" },
  { word: "niyamma", lang: "Detected" },
  { word: "bolimaga", lang: "Detected" },
  { word: "sulemaga", lang: "Detected" },
  { word: "lofer", lang: "Detected" },
  { word: "koyyale", lang: "Detected" },
  { word: "myre", lang: "Detected" },
  { word: "myran", lang: "Detected" },
  { word: "poori", lang: "Detected" },
  { word: "nayinte mone", lang: "Detected" },
  { word: "thalle", lang: "Detected" },
  { word: "burbak", lang: "Detected" },
  { word: "bokhandi", lang: "Detected" },
  { word: "chhotabhai", lang: "Detected" },
  { word: "stfu", lang: "Detected" },
  { word: "wtf", lang: "Detected" },
  { word: "gtfo", lang: "Detected" },
  { word: "stpd", lang: "Detected" },
  { word: "fck", lang: "Detected" },
  { word: "fuk", lang: "Detected" },
  { word: "fuq", lang: "Detected" },
  { word: "fucker", lang: "Detected" },
  { word: "fucking", lang: "Detected" },
  { word: "bitch", lang: "Detected" },
  { word: "asshole", lang: "Detected" },
  { word: "dick", lang: "Detected" },
  { word: "pussy", lang: "Detected" },
  { word: "slut", lang: "Detected" },
  { word: "whore", lang: "Detected" },
  { word: "भोसड़ीके", lang: "Detected" },
  { word: "लौड़े", lang: "Detected" },
  { word: "गांडू", lang: "Detected" },
  { word: "लंड", lang: "Detected" },
  { word: "रांड", lang: "Detected" },
  { word: "भड़वा", lang: "Detected" },
  { word: "हरामी", lang: "Detected" },
  { word: "हरामजादे", lang: "Detected" },
  { word: "मुठ्ठल", lang: "Detected" },
  { word: "sex", lang: "Detected" },
  { word: "boobs", lang: "Detected" },
  { word: "porn", lang: "Detected" },
  { word: "penis", lang: "Detected" },
  { word: "vagina", lang: "Detected" },
  { word: "tits", lang: "Detected" },
  { word: "dickhead", lang: "Detected" },
  { word: "cum", lang: "Detected" },
  { word: "blowjob", lang: "Detected" },
];

// Threat patterns — direct violence intent
const THREATS: { pattern: string; lang: string }[] = [
  { pattern: "i'?ll kill you", lang: "English" },
  { pattern: "i will kill you", lang: "English" },
  { pattern: "kill yourself", lang: "English" },
  { pattern: "i'?m going to hurt you", lang: "English" },
  { pattern: "going to beat you", lang: "English" },
  { pattern: "i'?ll beat you", lang: "English" },
  { pattern: "i will destroy you", lang: "English" },
  { pattern: "i'?ll destroy you", lang: "English" },
  { pattern: "i will end you", lang: "English" },
  { pattern: "watch your back", lang: "English" },
  { pattern: "you'?re dead", lang: "English" },
  { pattern: "i'?ll find you", lang: "English" },
  { pattern: "maar dunga", lang: "Hindi" },
  { pattern: "jaan se maar", lang: "Hindi" },
  { pattern: "jan se maar", lang: "Hindi" },
  { pattern: "thok dunga", lang: "Hindi" },
  { pattern: "tod dunga", lang: "Hindi" },
  { pattern: "maar d?al?unga", lang: "Hindi" },
  { pattern: "khatam kar d?ung[ae]", lang: "Hindi" },
  { pattern: "zinda gaad d?unga", lang: "Hindi" },
];

// Self-harm / suicide prevention
const SELF_HARM: { pattern: string; lang: string }[] = [
  { pattern: "kill myself", lang: "English" },
  { pattern: "want to die", lang: "English" },
  { pattern: "wanna die", lang: "English" },
  { pattern: "end my life", lang: "English" },
  { pattern: "ending my life", lang: "English" },
  { pattern: "suicide", lang: "English" },
  { pattern: "suicidal", lang: "English" },
  { pattern: "cut myself", lang: "English" },
  { pattern: "hurt myself", lang: "English" },
  { pattern: "no reason to live", lang: "English" },
  { pattern: "better off dead", lang: "English" },
  { pattern: "don'?t want to live", lang: "English" },
  { pattern: "mar jana chahta", lang: "Hindi" },
  { pattern: "mar jaunga", lang: "Hindi" },
  { pattern: "marne ka mann", lang: "Hindi" },
  { pattern: "khud ko maar", lang: "Hindi" },
  { pattern: "suicide kar", lang: "Hindi" },
];

// Scam / financial fraud / phishing
const SCAMS: { pattern: string; lang: string; label?: string }[] = [
  { pattern: "\\botp\\b", lang: "Hindi/English", label: "OTP request" },
  { pattern: "one time password", lang: "English", label: "OTP request" },
  { pattern: "cvv", lang: "English", label: "CVV request" },
  { pattern: "share your pin", lang: "English", label: "PIN harvest" },
  { pattern: "upi pin", lang: "English", label: "UPI PIN harvest" },
  { pattern: "atm pin", lang: "English", label: "ATM PIN harvest" },
  { pattern: "credit card number", lang: "English", label: "Card harvest" },
  { pattern: "card number", lang: "English", label: "Card harvest" },
  { pattern: "bank details", lang: "English", label: "Bank info harvest" },
  { pattern: "account number", lang: "English", label: "Account harvest" },
  { pattern: "you (have )?won", lang: "English", label: "Lottery scam" },
  { pattern: "lucky (winner|draw)", lang: "English", label: "Lottery scam" },
  { pattern: "lottery", lang: "English", label: "Lottery scam" },
  { pattern: "prize money", lang: "English", label: "Prize scam" },
  { pattern: "transfer (the )?money", lang: "English", label: "Money transfer" },
  { pattern: "wire transfer", lang: "English", label: "Money transfer" },
  { pattern: "gift card", lang: "English", label: "Gift card scam" },
  { pattern: "bitcoin", lang: "English", label: "Crypto scam" },
  { pattern: "investment (opportunity|plan|scheme)", lang: "English", label: "Investment scam" },
  { pattern: "double your money", lang: "English", label: "Ponzi scheme" },
  { pattern: "guaranteed returns", lang: "English", label: "Ponzi scheme" },
  { pattern: "kyc (expire|update|verif)", lang: "Hindi/English", label: "Fake KYC" },
  { pattern: "tax refund", lang: "English", label: "Tax refund scam" },
  { pattern: "verify your account", lang: "English", label: "Phishing" },
  { pattern: "suspended", lang: "English", label: "Urgency pressure" },
  { pattern: "otp batao", lang: "Hindi", label: "OTP request" },
  { pattern: "cvv batao", lang: "Hindi", label: "CVV request" },
];

// PII regular expressions. Higher `priority` wins when matches overlap
// (e.g. a 16-digit card run is also matched by the generic number rule).
const PII_PATTERNS: {
  type: PIIMatch["type"];
  re: RegExp;
  priority: number;
  mask: (v: string) => string;
}[] = [
  {
    type: "email",
    re: /[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}/gi,
    priority: 6,
    mask: (v) => v.replace(/^(.{2}).*(@.*)$/, "$1••••••$2"),
  },
  {
    type: "ssn",
    re: /\b\d{3}-\d{2}-\d{4}\b/g,
    priority: 5,
    mask: (v) => "XXX-XX-" + v.slice(-4),
  },
  {
    type: "credit-card",
    re: /\b(?:\d[ -]*?){13,16}\b/g,
    priority: 4,
    mask: (v) => "•••• •••• •••• " + v.replace(/\D/g, "").slice(-4),
  },
  {
    type: "aadhaar",
    re: /\b\d{4}[\s-]?\d{4}[\s-]?\d{4}\b/g,
    priority: 4,
    mask: (v) => "XXXX-XXXX-" + v.replace(/\D/g, "").slice(8),
  },
  {
    type: "phone",
    re: /(?:(?:\+91|91)?[ -]?)?\b\d[ \-\d]{8,13}\d\b/g,
    priority: 3,
    mask: (v) => {
      const d = v.replace(/\D/g, "");
      return "+XX-XXXXX-X" + d.slice(-3);
    },
  },
  // Any other run of 4+ digits (OTP, account no, partial card, etc.).
  // Catches "3 se zyada numbers" spoken individually or grouped.
  {
    type: "sensitive-number",
    re: /\b\d(?:[\s-]?\d){3,}\b/g,
    priority: 1,
    mask: (v) => {
      const d = v.replace(/\D/g, "");
      if (d.length <= 2) return "•".repeat(d.length);
      return "•".repeat(d.length - 2) + d.slice(-2);
    },
  },
];

// ---------------------------------------------------------------------------
//  Helpers
// ---------------------------------------------------------------------------
function escapeRegex(s: string): string {
  return s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

// Normalize a token so partial obfuscations (f*ck, ch**iya, be-henchod) match
function toFlexibleRegex(token: string): RegExp {
  const flexible = escapeRegex(token).replace(/\\\*/g, "[^a-z\\s]?").replace(/\s+/g, "[\\s-]*");
  return new RegExp(`(^|[^a-z])(${flexible})([^a-z]|$)`, "gi");
}

let counter = 0;
const uid = () => `f_${Date.now().toString(36)}_${(counter++).toString(36)}`;

// ---------------------------------------------------------------------------
//  Main analysis function
// ---------------------------------------------------------------------------
export function analyze(text: string): AnalysisResult {
  const lower = " " + text.toLowerCase() + " ";
  const findings: Finding[] = [];
  const languages = new Set<string>();

  const addFinding = (
    category: Category,
    severity: Severity,
    label: string,
    matchStr: string,
    start: number,
    end: number,
    lang: string
  ) => {
    findings.push({
      id: uid(),
      category,
      severity,
      label,
      match: matchStr.trim(),
      start: Math.max(0, start - 1),
      end: Math.max(0, end - 1),
      language: lang,
    });
    if (lang && lang !== "Hindi/English") languages.add(lang);
  };

  // --- Profanity ---
  for (const { word, lang } of PROFANITY) {
    const re = toFlexibleRegex(word);
    let m: RegExpExecArray | null;
    while ((m = re.exec(lower)) !== null) {
      // m[1] = boundary char, m[2] = the actual word. Map to original-text offsets.
      const wordStart = m.index + m[1].length;
      const wordEnd = wordStart + m[2].length;
      addFinding("profanity", "medium", "Profanity", m[2], wordStart, wordEnd, lang);
    }
  }

  // --- Threats ---
  for (const { pattern, lang } of THREATS) {
    const re = new RegExp(pattern, "gi");
    let m: RegExpExecArray | null;
    while ((m = re.exec(lower)) !== null) {
      addFinding("threat", "critical", "Violent threat", m[0], m.index, m.index + m[0].length, lang);
    }
  }

  // --- Self-harm ---
  for (const { pattern, lang } of SELF_HARM) {
    const re = new RegExp(pattern, "gi");
    let m: RegExpExecArray | null;
    while ((m = re.exec(lower)) !== null) {
      addFinding("self-harm", "critical", "Self-harm / suicidal", m[0], m.index, m.index + m[0].length, lang);
    }
  }

  // --- Scams ---
  for (const { pattern, lang, label } of SCAMS) {
    const re = new RegExp(pattern, "gi");
    let m: RegExpExecArray | null;
    while ((m = re.exec(lower)) !== null) {
      addFinding("scam", "high", label ?? "Scam / fraud", m[0], m.index, m.index + m[0].length, lang);
    }
  }

  // --- PII (against original text to preserve digits) ---
  type RawPii = PIIMatch & { priority: number };
  const rawPii: RawPii[] = [];
  for (const { type, re, mask, priority } of PII_PATTERNS) {
    let m: RegExpExecArray | null;
    const globalRe = new RegExp(re.source, re.flags.includes("g") ? re.flags : re.flags + "g");
    while ((m = globalRe.exec(text)) !== null) {
      const val = m[0].trim();
      // Reject digit-only matches that accidentally grabbed an @ symbol etc.
      if (type !== "email" && /[a-z@]/i.test(val)) continue;
      rawPii.push({
        id: uid(),
        type,
        value: val,
        masked: mask(val),
        start: m.index,
        end: m.index + m[0].length,
        priority,
      });
    }
  }

  // De-duplicate overlaps. Sort left-first; on tie keep the most specific
  // (higher priority) then the longest match. Walk and drop any span that
  // overlaps an already-accepted region.
  rawPii.sort((a, b) => a.start - b.start || b.priority - a.priority || b.end - a.end);
  const dedupPii: PIIMatch[] = [];
  const accepted: { start: number; end: number }[] = [];
  const overlapsAccepted = (p: RawPii) =>
    accepted.some((r) => p.start < r.end && p.end > r.start);
  for (const p of rawPii) {
    if (overlapsAccepted(p)) continue;
    dedupPii.push(p);
    accepted.push({ start: p.start, end: p.end });
  }
  dedupPii.sort((a, b) => a.start - b.start);

  // --- Stats ---
  const stats: Record<Category, number> = {
    profanity: findings.filter((f) => f.category === "profanity").length,
    threat: findings.filter((f) => f.category === "threat").length,
    "self-harm": findings.filter((f) => f.category === "self-harm").length,
    scam: findings.filter((f) => f.category === "scam").length,
    pii: dedupPii.length,
  };

  findings.sort((a, b) => a.start - b.start);

  // --- Risk score ---
  let raw = findings.reduce((sum, f) => sum + SEVERITY_WEIGHT[f.severity], 0);
  raw += dedupPii.filter((p) => p.type === "credit-card" || p.type === "aadhaar").length * 8;
  raw += dedupPii.filter((p) => p.type === "phone" || p.type === "sensitive-number").length * 60;
  const riskScore = Math.min(100, Math.round(raw));
  let riskLevel: AnalysisResult["riskLevel"] = "Safe";
  if (riskScore >= 60) riskLevel = "Critical";
  else if (riskScore >= 35) riskLevel = "High";
  else if (riskScore >= 12) riskLevel = "Moderate";

  return {
    findings,
    pii: dedupPii,
    stats,
    riskScore,
    riskLevel,
    wordCount: text.trim().split(/\s+/).filter(Boolean).length,
    languages: Array.from(languages),
  };
}

// ---------------------------------------------------------------------------
//  Visual helpers shared across the UI
// ---------------------------------------------------------------------------
export const CATEGORY_META: Record<
  Category,
  { label: string; color: string; text: string; bg: string; ring: string; dot: string }
> = {
  profanity: {
    label: "Profanity",
    color: "#f59e0b",
    text: "text-amber-700",
    bg: "bg-amber-50",
    ring: "ring-amber-200",
    dot: "bg-amber-500",
  },
  threat: {
    label: "Threat",
    color: "#ef4444",
    text: "text-red-700",
    bg: "bg-red-50",
    ring: "ring-red-200",
    dot: "bg-red-500",
  },
  "self-harm": {
    label: "Self-Harm",
    color: "#e11d48",
    text: "text-rose-700",
    bg: "bg-rose-50",
    ring: "ring-rose-200",
    dot: "bg-rose-500",
  },
  scam: {
    label: "Scam / Fraud",
    color: "#f97316",
    text: "text-orange-700",
    bg: "bg-orange-50",
    ring: "ring-orange-200",
    dot: "bg-orange-500",
  },
  pii: {
    label: "PII",
    color: "#3b82f6",
    text: "text-blue-700",
    bg: "bg-blue-50",
    ring: "ring-blue-200",
    dot: "bg-blue-500",
  },
};

export const SEVERITY_META: Record<Severity, { label: string; text: string; bg: string }> = {
  critical: { label: "Critical", text: "text-rose-700", bg: "bg-rose-100" },
  high: { label: "High", text: "text-orange-700", bg: "bg-orange-100" },
  medium: { label: "Medium", text: "text-amber-700", bg: "bg-amber-100" },
  low: { label: "Low", text: "text-slate-600", bg: "bg-slate-100" },
};
