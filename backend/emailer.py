import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_violation_alert_email(alert_data: dict) -> dict:
    """
    alert_data should contain:
      - user_id
      - adviser_id
      - violations (list of strings)
      - transcript
      - audio_url (optional)
    """
    smtp_host = os.environ.get("SMTP_HOST")
    smtp_port = os.environ.get("SMTP_PORT", "587")
    smtp_user = os.environ.get("SMTP_USER")
    smtp_pass = os.environ.get("SMTP_PASS")
    alert_email = os.environ.get("ALERT_EMAIL")

    if not smtp_host or not smtp_user or not smtp_pass or not alert_email:
        print("⚠️  SMTP not configured. Alert email will be logged but not sent.")
        print(f"📧 Would send violation alert to: {alert_email or '(not set)'}")
        print(f"   Violations: {', '.join(alert_data.get('violations', []))}")
        print(f"   User: {alert_data.get('user_id')} | Advisor: {alert_data.get('adviser_id')}")
        return {
            "success": False,
            "error": "SMTP not configured. Set SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, and ALERT_EMAIL."
        }

    violations = alert_data.get("violations", [])
    subject = f"🚨 Call Violation Alert – {' & '.join(violations)} – User: {alert_data.get('user_id')}"

    # Build HTML body
    violation_badges = "".join([
        f'<span style="display:inline-block;background:#dc2626;color:#fff;padding:4px 14px;border-radius:20px;font-size:13px;font-weight:600;margin-right:6px;">{v}</span>'
        for v in violations
    ])

    audio_url = alert_data.get("audio_url")
    audio_link_section = ""
    if audio_url:
        audio_link_section = f"""
        <div style="background:#eff6ff;border:1px solid #bfdbfe;border-radius:8px;padding:16px;margin-bottom:24px;display:flex;align-items:center;">
          <span style="font-size:24px;margin-right:12px;">🎧</span>
          <div>
            <h4 style="margin:0 0 4px;color:#1e3a8a;font-size:14px;">Original Call Recording</h4>
            <a href="{audio_url}" target="_blank" style="color:#2563eb;text-decoration:none;font-weight:600;font-size:13px;">Click here to listen to the audio</a>
          </div>
        </div>
        """

    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8"></head>
    <body style="margin:0;padding:0;background:#f3f4f6;font-family:'Segoe UI',Arial,sans-serif;">
      <div style="max-width:640px;margin:30px auto;background:#ffffff;border-radius:12px;overflow:hidden;box-shadow:0 4px 20px rgba(0,0,0,0.08);">
        
        <div style="background:linear-gradient(135deg,#dc2626,#b91c1c);padding:28px 32px;text-align:center;">
          <h1 style="margin:0;color:#fff;font-size:22px;letter-spacing:0.5px;">🚨 Call Violation Alert</h1>
          <p style="margin:8px 0 0;color:#fecaca;font-size:14px;">AI Speech Analytics QA Agent</p>
        </div>
        
        <div style="padding:28px 32px;">
          <div style="margin-bottom:20px;">{violation_badges}</div>
          {audio_link_section}
          
          <table style="width:100%;border-collapse:collapse;margin-bottom:24px;border:1px solid #e5e7eb;border-radius:8px;">
            <tr>
              <td style="padding:10px 16px;font-weight:600;color:#374151;border-bottom:1px solid #e5e7eb;width:180px;">User ID</td>
              <td style="padding:10px 16px;color:#1f2937;border-bottom:1px solid #e5e7eb;"><strong>{alert_data.get('user_id')}</strong></td>
            </tr>
            <tr>
              <td style="padding:10px 16px;font-weight:600;color:#374151;border-bottom:1px solid #e5e7eb;width:180px;">Advisor ID</td>
              <td style="padding:10px 16px;color:#1f2937;border-bottom:1px solid #e5e7eb;"><strong>{alert_data.get('adviser_id')}</strong></td>
            </tr>
          </table>
          
          <h3 style="color:#374151;font-size:16px;margin:24px 0 12px;">🚨 Detected Incidents (Timestamps)</h3>
          <div style="background:#fef2f2;border:1px solid #fecaca;border-radius:8px;padding:16px;margin-bottom:24px;">
            {''.join([f'<div style="margin-bottom:12px;padding-bottom:12px;border-bottom:1px solid #fca5a5;"><span style="color:#b91c1c;font-weight:bold;margin-right:8px;">[{inc["time"]}]</span><span style="font-weight:600;color:#991b1b;">{inc["speaker"]}:</span> <span style="color:#7f1d1d;">"{inc["text"]}"</span> <br/><span style="font-size:12px;color:#dc2626;margin-top:4px;display:inline-block;">Violation: {", ".join(inc["violations"])}</span></div>' for inc in alert_data.get('incidents', [])])}
          </div>
          
          <h3 style="color:#374151;font-size:16px;margin:24px 0 12px;">📝 Full Transcript</h3>
          <div style="background:#f9fafb;border:1px solid #e5e7eb;border-radius:8px;padding:16px;font-size:13px;color:#4b5563;line-height:1.7;max-height:200px;overflow-y:auto;">
            {alert_data.get('transcript', '')}
          </div>
        </div>
        
        <div style="background:#f9fafb;padding:16px 32px;text-align:center;border-top:1px solid #e5e7eb;">
          <p style="margin:0;color:#9ca3af;font-size:12px;">This is an automated alert from the AI Speech Analytics QA System.</p>
        </div>
      </div>
    </body>
    </html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"QA Alert System <{smtp_user}>"
    msg["To"] = alert_email

    msg.attach(MIMEText(html_body, "html"))

    try:
        # Connect to SMTP server
        port = int(smtp_port)
        if port == 465:
            server = smtplib.SMTP_SSL(smtp_host, port)
        else:
            server = smtplib.SMTP(smtp_host, port)
            server.starttls()
            
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)
        server.quit()
        
        print(f"✅ Violation alert email sent to {alert_email}")
        return {"success": True}
    except Exception as e:
        print("❌ Failed to send alert email:", str(e))
        return {"success": False, "error": str(e)}
