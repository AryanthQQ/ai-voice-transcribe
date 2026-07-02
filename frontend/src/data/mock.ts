// ============================================================================
//  Mock analytics dataset powering the Dashboard, History & Insights views.
//  In production these come from the FastAPI backend / database.
// ============================================================================

import type { Category } from "../lib/analyzer";

export interface DailyTrend {
  day: string;
  calls: number;
  flagged: number;
  scams: number;
}

export const DAILY_TREND: DailyTrend[] = [
  { day: "Mon", calls: 1240, flagged: 312, scams: 48 },
  { day: "Tue", calls: 1380, flagged: 360, scams: 61 },
  { day: "Wed", calls: 1290, flagged: 298, scams: 39 },
  { day: "Thu", calls: 1455, flagged: 401, scams: 72 },
  { day: "Fri", calls: 1620, flagged: 488, scams: 95 },
  { day: "Sat", calls: 980, flagged: 244, scams: 33 },
  { day: "Sun", calls: 845, flagged: 198, scams: 27 },
  { day: "Mon", calls: 1510, flagged: 422, scams: 70 },
  { day: "Tue", calls: 1680, flagged: 511, scams: 88 },
  { day: "Wed", calls: 1595, flagged: 476, scams: 79 },
  { day: "Thu", calls: 1740, flagged: 540, scams: 102 },
  { day: "Fri", calls: 1890, flagged: 612, scams: 118 },
  { day: "Sat", calls: 1120, flagged: 301, scams: 44 },
  { day: "Sun", calls: 960, flagged: 256, scams: 31 },
];

export const CATEGORY_BREAKDOWN: { category: Category; count: number }[] = [
  { category: "profanity", count: 2840 },
  { category: "scam", count: 1142 },
  { category: "threat", count: 689 },
  { category: "pii", count: 4230 },
  { category: "self-harm", count: 96 },
];

export interface AgentStat {
  name: string;
  initials: string;
  aggressiveCalls: number;
  totalCalls: number;
  satisfaction: number;
}

export const TOP_AGENTS: AgentStat[] = [
  { name: "Rahul Mehta", initials: "RM", aggressiveCalls: 88, totalCalls: 412, satisfaction: 91 },
  { name: "Priya Nair", initials: "PN", aggressiveCalls: 64, totalCalls: 388, satisfaction: 94 },
  { name: "Aman Verma", initials: "AV", aggressiveCalls: 57, totalCalls: 301, satisfaction: 88 },
  { name: "Sara Khan", initials: "SK", aggressiveCalls: 49, totalCalls: 356, satisfaction: 95 },
  { name: "Vikram Singh", initials: "VS", aggressiveCalls: 41, totalCalls: 274, satisfaction: 90 },
];

export interface RiskBucket {
  level: "Critical" | "High" | "Moderate" | "Safe";
  value: number;
  color: string;
}

export const RISK_DISTRIBUTION: RiskBucket[] = [
  { level: "Safe", value: 68, color: "#10b981" },
  { level: "Moderate", value: 18, color: "#f59e0b" },
  { level: "High", value: 9, color: "#f97316" },
  { level: "Critical", value: 5, color: "#ef4444" },
];

export interface WordFreq {
  phrase: string;
  count: number;
  category: Category;
}

export const SCAM_PHRASES: WordFreq[] = [
  { phrase: "share your OTP", count: 612, category: "scam" },
  { phrase: "card suspended", count: 488, category: "scam" },
  { phrase: "verify account", count: 421, category: "scam" },
  { phrase: "lucky draw winner", count: 305, category: "scam" },
  { phrase: "share your CVV", count: 274, category: "scam" },
  { phrase: "prize money", count: 233, category: "scam" },
  { phrase: "KYC expired", count: 198, category: "scam" },
  { phrase: "transfer the money", count: 167, category: "scam" },
  { phrase: "guaranteed returns", count: 142, category: "scam" },
  { phrase: "gift card payment", count: 119, category: "scam" },
  { phrase: "double your money", count: 96, category: "scam" },
  { phrase: "bank details please", count: 84, category: "scam" },
];

export const ABUSE_PHRASES: WordFreq[] = [
  { phrase: "madarchod", count: 980, category: "profanity" },
  { phrase: "chutiya", count: 742, category: "profanity" },
  { phrase: "bhenchod", count: 521, category: "profanity" },
  { phrase: "bullshit", count: 388, category: "profanity" },
  { phrase: "saala", count: 410, category: "profanity" },
  { phrase: "randi", count: 244, category: "profanity" },
  { phrase: "harami", count: 198, category: "profanity" },
  { phrase: "bhosdike", count: 156, category: "profanity" },
  { phrase: "kutta", count: 132, category: "profanity" },
  { phrase: "bitch", count: 118, category: "profanity" },
];

export interface CallRecord {
  id: string;
  agent: string;
  agentInitials: string;
  customer: string;
  language: string;
  durationSec: number;
  when: string;
  riskScore: number;
  riskLevel: "Critical" | "High" | "Moderate" | "Safe";
  categories: Category[];
  summary: string;
}

export const CALL_HISTORY: CallRecord[] = [
  {
    id: "CL-4821",
    agent: "Rahul Mehta",
    agentInitials: "RM",
    customer: "Arun Sharma",
    language: "Hindi + English",
    durationSec: 184,
    when: "2 min ago",
    riskScore: 86,
    riskLevel: "Critical",
    categories: ["profanity", "threat", "scam", "pii"],
    summary:
      "Customer disputed a duplicate charge and made violent threats. Agent requested OTP for a genuine refund but context was flagged.",
  },
  {
    id: "CL-4820",
    agent: "Priya Nair",
    agentInitials: "PN",
    customer: "Unknown Caller",
    language: "English",
    durationSec: 142,
    when: "14 min ago",
    riskScore: 92,
    riskLevel: "Critical",
    categories: ["scam", "pii"],
    summary:
      "Likely phishing call. Caller impersonated bank fraud dept and harvested card number, CVV and OTP. Customer disconnected.",
  },
  {
    id: "CL-4819",
    agent: "Sara Khan",
    agentInitials: "SK",
    customer: "Meera Iyer",
    language: "English",
    durationSec: 96,
    when: "38 min ago",
    riskScore: 74,
    riskLevel: "High",
    categories: ["self-harm"],
    summary:
      "Caller expressed suicidal ideation and recent self-harm. Agent followed crisis protocol and escalated to a counsellor.",
  },
  {
    id: "CL-4818",
    agent: "Aman Verma",
    agentInitials: "AV",
    customer: "Joseph D'Souza",
    language: "English",
    durationSec: 118,
    when: "1 hr ago",
    riskScore: 4,
    riskLevel: "Safe",
    categories: [],
    summary: "Routine delivery status enquiry. Resolved positively. No risk signals detected.",
  },
  {
    id: "CL-4817",
    agent: "Vikram Singh",
    agentInitials: "VS",
    customer: "Fatima Begum",
    language: "Hindi",
    durationSec: 221,
    when: "1 hr ago",
    riskScore: 58,
    riskLevel: "High",
    categories: ["profanity", "scam"],
    summary:
      "Customer frustrated with KYC flow; caller attempted to collect bank details under fake KYC urgency.",
  },
  {
    id: "CL-4816",
    agent: "Priya Nair",
    agentInitials: "PN",
    customer: "Rajesh Gupta",
    language: "Hindi + English",
    durationSec: 167,
    when: "2 hr ago",
    riskScore: 47,
    riskLevel: "Moderate",
    categories: ["profanity", "pii"],
    summary:
      "Refund complaint with repeated profanity. Phone number and email extracted for verification.",
  },
  {
    id: "CL-4815",
    agent: "Rahul Mehta",
    agentInitials: "RM",
    customer: "Anjali Rao",
    language: "English",
    durationSec: 134,
    when: "3 hr ago",
    riskScore: 22,
    riskLevel: "Moderate",
    categories: ["pii"],
    summary: "Account update request. Email and address captured; no abusive or fraudulent content.",
  },
  {
    id: "CL-4814",
    agent: "Sara Khan",
    agentInitials: "SK",
    customer: "Mohammed Ali",
    language: "Urdu",
    durationSec: 203,
    when: "3 hr ago",
    riskScore: 69,
    riskLevel: "High",
    categories: ["threat", "profanity"],
    summary:
      "Heated dispute over charges escalated to direct threats against the agent. Supervisor notified.",
  },
];

export const KPIS = {
  totalCalls: 18429,
  callsChange: 12.4,
  flaggedRate: 24.6,
  flaggedChange: -3.1,
  scamBlocked: 1142,
  scamChange: 18.2,
  piiExtracted: 4230,
  piiChange: 7.8,
  avgRisk: 31,
  avgRiskChange: -2.4,
};
