import {
  pgTable,
  serial,
  text,
  timestamp,
  boolean,
  jsonb,
} from "drizzle-orm/pg-core";

// ──────────────────────────────────────────────
// Call Analysis Records Table
// Stores every analysed call along with its
// transcript, detected violations, and alert status.
// ──────────────────────────────────────────────
export const callAnalyses = pgTable("call_analyses", {
  id: serial("id").primaryKey(),
  userId: text("user_id").notNull(),
  advisorId: text("advisor_id").notNull(),
  transcript: text("transcript").notNull(),
  hasAbuse: boolean("has_abuse").notNull().default(false),
  hasPhoneNumber: boolean("has_phone_number").notNull().default(false),
  abuseWords: jsonb("abuse_words").$type<string[]>().default([]),
  detectedNumbers: jsonb("detected_numbers").$type<string[]>().default([]),
  violationSnippets: jsonb("violation_snippets").$type<string[]>().default([]),
  alertSent: boolean("alert_sent").notNull().default(false),
  alertError: text("alert_error"),
  createdAt: timestamp("created_at").notNull().defaultNow(),
});

export type CallAnalysis = typeof callAnalyses.$inferSelect;
export type NewCallAnalysis = typeof callAnalyses.$inferInsert;
