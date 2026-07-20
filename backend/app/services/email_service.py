import smtplib
from email.message import EmailMessage
from app.core.config import settings
from app.core.logger import logger

def send_violation_alert_email(alert_data: dict) -> dict:
    """
    Sends an email alert to the safety team when a violation is detected.
    """
    smtp_host = settings.SMTP_HOST
    smtp_user = settings.SMTP_USER
    smtp_pass = settings.SMTP_PASS
    alert_email = settings.ALERT_EMAIL

    if not smtp_host or not smtp_user or not smtp_pass or not alert_email:
        logger.warning("SMTP not configured. Alert email will be logged but not sent.")
        logger.info(f"Would send violation alert to: {alert_email or '(not set)'}")
        logger.info(f"Violations: {', '.join(alert_data.get('violations', []))}")
        logger.info(f"User: {alert_data.get('user_id')} | Advisor: {alert_data.get('adviser_id')}")
        return {
            "success": False, 
            "error": "SMTP credentials missing",
            "logged_only": True
        }

    try:
        msg = EmailMessage()
        msg['Subject'] = f"🚨 URGENT: Policy Violation Detected (Advisor: {alert_data.get('adviser_id')})"
        msg['From'] = smtp_user
        msg['To'] = alert_email

        violations_str = ", ".join(alert_data.get('violations', []))
        
        body = f"""
POLICY VIOLATION ALERT
======================
Date: {alert_data.get('time', 'Now')}
Violations Detected: {violations_str}

PARTICIPANTS
------------
Advisor ID: {alert_data.get('adviser_id')}
User ID: {alert_data.get('user_id')}

AUDIO RECORDING
---------------
URL: {alert_data.get('audio_url')}

INCIDENT DETAILS
----------------
"""
        incidents = alert_data.get('incidents', [])
        for inc in incidents:
            body += f"\n[{inc.get('time')}] {inc.get('speaker')}: \"{inc.get('text')}\""
            body += f"\n   -> Triggered by: {', '.join(inc.get('violations', []))}\n"

        body += f"\n\nFULL TRANSCRIPT\n---------------\n{alert_data.get('transcript', 'No transcript provided.')}"
        
        msg.set_content(body)

        logger.info("Connecting to SMTP server...")
        server = smtplib.SMTP(smtp_host, settings.SMTP_PORT)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)
        server.quit()
        
        logger.info(f"Violation alert email sent to {alert_email}")
        return {"success": True}
    except Exception as e:
        logger.error(f"Failed to send alert email: {str(e)}")
        return {"success": False, "error": str(e)}
