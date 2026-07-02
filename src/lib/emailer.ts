/**
 * ─────────────────────────────────────────────
 *  emailer.ts  –  SMTP Alert System
 * ─────────────────────────────────────────────
 *  Sends HTML-formatted violation alert emails
 *  to the configured manager email address.
 *
 *  Environment Variables Required:
 *    SMTP_HOST     – e.g., smtp.gmail.com
 *    SMTP_PORT     – e.g., 587
 *    SMTP_USER     – sender email address
 *    SMTP_PASS     – sender email password / app password
 *    ALERT_EMAIL   – manager's email to receive alerts
 * ─────────────────────────────────────────────
 */

import nodemailer from "nodemailer";

export interface ViolationAlert {
  userId: string;
  advisorId: string;
  violationTypes: string[];   // e.g., ["Abusive Language", "Phone Number Sharing"]
  abuseWords: string[];
  detectedNumbers: string[];
  violationSnippets: string[];
  transcript: string;
  audioUrl?: string | null;
}

// ── Build HTML Email Body ────────────────────
function buildAlertHtml(alert: ViolationAlert): string {
  const violationBadges = alert.violationTypes
    .map(
      (v) =>
        `<span style="display:inline-block;background:#dc2626;color:#fff;padding:4px 14px;border-radius:20px;font-size:13px;font-weight:600;margin-right:6px;">${v}</span>`
    )
    .join("");

  const abuseSection =
    alert.abuseWords.length > 0
      ? `
    <tr>
      <td style="padding:10px 16px;font-weight:600;color:#374151;border-bottom:1px solid #e5e7eb;width:180px;">Abusive Words Found</td>
      <td style="padding:10px 16px;color:#dc2626;font-weight:600;border-bottom:1px solid #e5e7eb;">${alert.abuseWords.map((w) => `<code style="background:#fef2f2;padding:2px 8px;border-radius:4px;margin-right:4px;">${w}</code>`).join(" ")}</td>
    </tr>`
      : "";

  const numbersSection =
    alert.detectedNumbers.length > 0
      ? `
    <tr>
      <td style="padding:10px 16px;font-weight:600;color:#374151;border-bottom:1px solid #e5e7eb;width:180px;">Phone Numbers Detected</td>
      <td style="padding:10px 16px;color:#dc2626;font-weight:600;border-bottom:1px solid #e5e7eb;">${alert.detectedNumbers.map((n) => `<code style="background:#fef2f2;padding:2px 8px;border-radius:4px;margin-right:4px;">${n}</code>`).join(" ")}</td>
    </tr>`
      : "";

  const snippetsHtml = alert.violationSnippets
    .map(
      (s) =>
        `<div style="background:#fef2f2;border-left:4px solid #dc2626;padding:10px 14px;margin-bottom:8px;border-radius:0 6px 6px 0;font-size:14px;color:#1f2937;font-family:monospace;">${s}</div>`
    )
    .join("");

  const audioLinkSection = alert.audioUrl
    ? `
    <!-- Audio Link -->
    <div style="background:#eff6ff;border:1px solid #bfdbfe;border-radius:8px;padding:16px;margin-bottom:24px;display:flex;align-items:center;">
      <span style="font-size:24px;margin-right:12px;">🎧</span>
      <div>
        <h4 style="margin:0 0 4px;color:#1e3a8a;font-size:14px;">Original Call Recording</h4>
        <a href="${alert.audioUrl}" target="_blank" style="color:#2563eb;text-decoration:none;font-weight:600;font-size:13px;">Click here to listen to the audio</a>
      </div>
    </div>
    `
    : "";

  return `
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="margin:0;padding:0;background:#f3f4f6;font-family:'Segoe UI',Arial,sans-serif;">
  <div style="max-width:640px;margin:30px auto;background:#ffffff;border-radius:12px;overflow:hidden;box-shadow:0 4px 20px rgba(0,0,0,0.08);">
    
    <!-- Header -->
    <div style="background:linear-gradient(135deg,#dc2626,#b91c1c);padding:28px 32px;text-align:center;">
      <h1 style="margin:0;color:#fff;font-size:22px;letter-spacing:0.5px;">🚨 Call Violation Alert</h1>
      <p style="margin:8px 0 0;color:#fecaca;font-size:14px;">AI Speech Analytics QA Agent</p>
    </div>
    
    <!-- Body -->
    <div style="padding:28px 32px;">
      
      <!-- Violation Badges -->
      <div style="margin-bottom:20px;">${violationBadges}</div>
      
      ${audioLinkSection}
      
      <!-- Details Table -->
      <table style="width:100%;border-collapse:collapse;margin-bottom:24px;border:1px solid #e5e7eb;border-radius:8px;">
        <tr>
          <td style="padding:10px 16px;font-weight:600;color:#374151;border-bottom:1px solid #e5e7eb;width:180px;">User ID</td>
          <td style="padding:10px 16px;color:#1f2937;border-bottom:1px solid #e5e7eb;"><strong>${alert.userId}</strong></td>
        </tr>
        <tr>
          <td style="padding:10px 16px;font-weight:600;color:#374151;border-bottom:1px solid #e5e7eb;width:180px;">Advisor ID</td>
          <td style="padding:10px 16px;color:#1f2937;border-bottom:1px solid #e5e7eb;"><strong>${alert.advisorId}</strong></td>
        </tr>
        ${abuseSection}
        ${numbersSection}
      </table>
      
      <!-- Violation Snippets -->
      <h3 style="color:#374151;font-size:16px;margin-bottom:12px;">📌 Violation Timestamps & Snippets</h3>
      ${snippetsHtml}
      
      <!-- Full Transcript -->
      <h3 style="color:#374151;font-size:16px;margin:24px 0 12px;">📝 Full Transcript</h3>
      <div style="background:#f9fafb;border:1px solid #e5e7eb;border-radius:8px;padding:16px;font-size:13px;color:#4b5563;line-height:1.7;max-height:200px;overflow-y:auto;">
        ${alert.transcript}
      </div>
    </div>
    
    <!-- Footer -->
    <div style="background:#f9fafb;padding:16px 32px;text-align:center;border-top:1px solid #e5e7eb;">
      <p style="margin:0;color:#9ca3af;font-size:12px;">This is an automated alert from the AI Speech Analytics QA System.</p>
    </div>
  </div>
</body>
</html>`;
}

// ── Send Alert Email ─────────────────────────
export async function sendViolationAlert(
  alert: ViolationAlert
): Promise<{ success: boolean; error?: string }> {
  const smtpHost = process.env.SMTP_HOST;
  const smtpPort = parseInt(process.env.SMTP_PORT || "587", 10);
  const smtpUser = process.env.SMTP_USER;
  const smtpPass = process.env.SMTP_PASS;
  const alertEmail = process.env.ALERT_EMAIL;

  // If SMTP is not configured, log the alert and return gracefully
  if (!smtpHost || !smtpUser || !smtpPass || !alertEmail) {
    console.warn(
      "⚠️  SMTP not configured. Alert email will be logged but not sent."
    );
    console.log("📧 Would send violation alert to:", alertEmail || "(not set)");
    console.log("   Violations:", alert.violationTypes.join(", "));
    console.log("   User:", alert.userId, "| Advisor:", alert.advisorId);
    return {
      success: false,
      error:
        "SMTP not configured. Set SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, and ALERT_EMAIL environment variables.",
    };
  }

  try {
    // Create SMTP transporter
    const transporter = nodemailer.createTransport({
      host: smtpHost,
      port: smtpPort,
      secure: smtpPort === 465, // true for 465, false for other ports
      auth: {
        user: smtpUser,
        pass: smtpPass,
      },
    });

    // Build the subject line with violation types
    const subject = `🚨 Call Violation Alert – ${alert.violationTypes.join(" & ")} – User: ${alert.userId}`;

    // Send the email
    await transporter.sendMail({
      from: `"QA Alert System" <${smtpUser}>`,
      to: alertEmail,
      subject,
      html: buildAlertHtml(alert),
    });

    console.log(`✅ Violation alert email sent to ${alertEmail}`);
    return { success: true };
  } catch (error) {
    const errorMsg =
      error instanceof Error ? error.message : "Unknown email error";
    console.error("❌ Failed to send alert email:", errorMsg);
    return { success: false, error: errorMsg };
  }
}
