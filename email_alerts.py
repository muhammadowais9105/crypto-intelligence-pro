"""
email_alerts.py
Crypto Intelligence Pro — Gmail SMTP Alert Sender
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

try:
    from email_config import SENDER_EMAIL, APP_PASSWORD, RECEIVER_EMAIL
    EMAIL_CONFIGURED = True
except ImportError:
    EMAIL_CONFIGURED = False
    SENDER_EMAIL = ""
    APP_PASSWORD = ""
    RECEIVER_EMAIL = ""


def send_alert(subject: str, body: str, to_email: str = None) -> dict:
    """
    Send an email alert via Gmail SMTP.
    Returns dict with success flag and message.
    """
    if not EMAIL_CONFIGURED:
        return {"success": False, "message": "email_config.py not found or not configured."}

    if not APP_PASSWORD or APP_PASSWORD == "your_app_password_here":
        return {"success": False, "message": "Please update email_config.py with your Gmail App Password."}

    recipient = to_email or RECEIVER_EMAIL

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = SENDER_EMAIL
        msg["To"] = recipient

        # Plain text version
        text_body = f"{body}\n\n---\nSent by Crypto Intelligence Pro\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        # HTML version
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background: #0d1117; color: #e6edf3; padding: 20px;">
            <div style="max-width: 600px; margin: auto; background: #161b22; border-radius: 12px; padding: 30px; border: 1px solid #30363d;">
                <h2 style="color: #f0c040; margin-top: 0;">🚀 Crypto Intelligence Pro</h2>
                <h3 style="color: #58a6ff;">{subject}</h3>
                <div style="background: #0d1117; border-radius: 8px; padding: 16px; margin: 16px 0; white-space: pre-wrap; font-size: 14px;">
                    {body.replace(chr(10), '<br>')}
                </div>
                <hr style="border-color: #30363d; margin: 20px 0;">
                <p style="color: #8b949e; font-size: 12px; margin: 0;">
                    Sent by Crypto Intelligence Pro &bull; {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                </p>
            </div>
        </body>
        </html>
        """

        msg.attach(MIMEText(text_body, "plain"))
        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER_EMAIL, APP_PASSWORD)
            server.sendmail(SENDER_EMAIL, recipient, msg.as_string())

        return {"success": True, "message": f"Alert sent to {recipient}"}

    except smtplib.SMTPAuthenticationError:
        return {"success": False, "message": "Authentication failed. Check your App Password."}
    except Exception as e:
        return {"success": False, "message": f"Failed to send: {str(e)}"}


def build_signal_alert(coin: str, signal_data: dict, risk_data: dict) -> tuple:
    """Build subject + body for a trading signal email."""
    signal = signal_data.get("signal", "HOLD")
    price = signal_data.get("price", 0)
    rsi = signal_data.get("rsi", "N/A")
    reasoning = signal_data.get("reasoning", "")
    stop_loss = risk_data.get("stop_loss", "N/A")
    tp1 = risk_data.get("take_profit_1", "N/A")
    tp2 = risk_data.get("take_profit_2", "N/A")

    emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(signal, "⚪")

    subject = f"{emoji} {signal} Signal — {coin} @ ${price:,}"
    body = (
        f"Signal: {signal}\n"
        f"Coin: {coin}\n"
        f"Current Price: ${price:,}\n"
        f"RSI: {rsi}\n\n"
        f"Analysis:\n{reasoning}\n\n"
        f"Risk Management:\n"
        f"  Stop Loss: ${stop_loss:,}\n"
        f"  Take Profit 1: ${tp1:,}\n"
        f"  Take Profit 2: ${tp2:,}\n"
    )
    return subject, body


def build_political_alert(headline: str, impact: str, source: str) -> tuple:
    """Build subject + body for a political shock alert."""
    emoji = {"BULLISH": "🟢", "BEARISH": "🔴", "NEUTRAL": "⚪"}.get(impact, "⚪")
    subject = f"⚠️ Political Shock Detected — {impact} for Crypto"
    body = (
        f"A market-moving political event has been detected.\n\n"
        f"Impact: {emoji} {impact}\n"
        f"Source: {source}\n\n"
        f"Headline:\n{headline}\n\n"
        f"Action: Review your positions and risk exposure immediately."
    )
    return subject, body
