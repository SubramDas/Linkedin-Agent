import sys
from pathlib import Path
from datetime import datetime
import base64
import urllib.parse
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Add project root to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from config import (
    SMTP_HOST,
    SMTP_PORT,
    SENDER_EMAIL,
    SENDER_APP_PASSWORD,
    RECEIVER_EMAIL,
    WEB_REVIEW_URL,
)
from agents.copywriter import LinkedInDraft
from agents.curator import CuratedTopic


class EmailService:
    """Service responsible for sending generated LinkedIn drafts via SMTP."""

    def __init__(
        self,
        host: str = SMTP_HOST,
        port: int = SMTP_PORT,
        sender: str = SENDER_EMAIL,
        password: str = SENDER_APP_PASSWORD,
        receiver: str = RECEIVER_EMAIL,
    ):
        self.host = host
        self.port = port
        self.sender = sender
        self.password = password
        self.receiver = receiver

    def is_configured(self) -> bool:
        """Check if all email credentials have been configured."""
        return bool(self.sender and self.password and self.receiver)

    def send_draft(self, draft: LinkedInDraft, topic: CuratedTopic) -> bool:
        """Sends the generated LinkedIn draft to your configured email address."""
        if not self.is_configured():
            print("[EmailService] Warning: Email credentials are not fully configured in .env.")
            print("[EmailService] Please set SENDER_EMAIL, SENDER_APP_PASSWORD, and RECEIVER_EMAIL.")
            return False

        time_str = datetime.now().strftime("%H:%M")
        subject = f"🚀 [LinkedIn Draft - {time_str}] {topic.selected_title[:50]}..."

        # Create multi-part message (plain text + HTML fallback)
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = self.sender
        msg["To"] = self.receiver

        # Encode full_post into Base64 for the Web Copier
        encoded_post = base64.b64encode(draft.full_post.encode("utf-8")).decode("utf-8")
        safe_hash = urllib.parse.quote(encoded_post)
        web_copier_url = f"{WEB_REVIEW_URL.rstrip('/')}/#{safe_hash}" if WEB_REVIEW_URL else ""

        # Plain text version
        plain_text = f"""Good morning! Here is today's curated LinkedIn post draft.

TOPIC: {topic.selected_title}
SOURCE: {topic.selected_source} ({topic.virality_score}/100)
LINK: {topic.selected_link}
"""
        if web_copier_url:
            plain_text += f"\n1-TAP COPY ON MOBILE: {web_copier_url}\n"

        plain_text += f"""
----------------------------------------
READY-TO-POST DRAFT:
----------------------------------------

{draft.full_post}

----------------------------------------
Review, copy, and paste into LinkedIn!
"""

        # HTML formatted version (optimized for mobile 1-tap copy)
        web_copier_button = ""
        if web_copier_url:
            web_copier_button = f"""
            <div style="margin-bottom: 16px; text-align: center;">
                <a href="{web_copier_url}" 
                   style="display: block; width: 90%; margin: 0 auto; background-color: #16a34a; color: #ffffff; text-decoration: none; padding: 14px 0; border-radius: 10px; font-weight: 700; font-size: 16px; box-shadow: 0 2px 6px rgba(22,163,74,0.3);" 
                   target="_blank">
                    📋 1-Tap Copy on Mobile (Opens Copier)
                </a>
            </div>
            """

        html_content = f"""
        <html>
        <head>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="margin: 0; padding: 12px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f1f5f9; color: #0f172a;">
            <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.1); border: 1px solid #e2e8f0;">
                
                <!-- Header -->
                <div style="background-color: #0a66c2; color: #ffffff; padding: 16px 20px;">
                    <h2 style="margin: 0; font-size: 18px; font-weight: 600;">🚀 Today's LinkedIn Draft</h2>
                    <p style="margin: 4px 0 0 0; font-size: 13px; opacity: 0.9;">Virality Score: {topic.virality_score}/100 • {topic.selected_source}</p>
                </div>
                
                <div style="padding: 16px 20px;">
                    <!-- Context snippet -->
                    <p style="margin: 0 0 16px 0; font-size: 13px; color: #64748b;">
                        <strong>Topic:</strong> <a href="{topic.selected_link}" style="color: #0a66c2; text-decoration: none;" target="_blank">{topic.selected_title}</a>
                    </p>

                    <!-- Green 1-Tap Mobile Copier Button -->
                    {web_copier_button}

                    <!-- Post Box -->
                    <div style="
                        background-color: #f8fafc;
                        border: 1px solid #cbd5e1;
                        border-radius: 8px;
                        padding: 16px;
                        font-size: 15px;
                        line-height: 1.6;
                        color: #1e293b;
                        white-space: pre-wrap;
                    ">{draft.full_post}</div>

                    <!-- Open LinkedIn Button -->
                    <div style="margin-top: 20px; text-align: center;">
                        <a href="https://www.linkedin.com/feed/?shareActive=true" 
                           style="display: block; width: 90%; margin: 0 auto; background-color: #0a66c2; color: #ffffff; text-decoration: none; padding: 12px 0; border-radius: 10px; font-weight: 600; font-size: 15px;" 
                           target="_blank">
                            ↗️ Open LinkedIn to Post
                        </a>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """

        msg.attach(MIMEText(plain_text, "plain"))
        msg.attach(MIMEText(html_content, "html"))

        try:
            print(f"[EmailService] Connecting to {self.host}:{self.port}...")
            with smtplib.SMTP_SSL(self.host, self.port) as server:
                server.login(self.sender, self.password)
                server.send_message(msg)
            print(f"[EmailService] Draft successfully sent to {self.receiver}!")
            return True
        except Exception as e:
            print(f"[EmailService] Failed to send email: {e}")
            return False


# Global shared instance
email_service = EmailService()


if __name__ == "__main__":
    print("--- Testing EmailService Configuration ---")
    if not email_service.is_configured():
        print("Status: NOT CONFIGURED")
        print("To enable email notifications, update the following in your .env file:")
        print("  - SENDER_EMAIL=your_email@gmail.com")
        print("  - SENDER_APP_PASSWORD=your_16_char_app_password")
        print("  - RECEIVER_EMAIL=your_email@gmail.com")
    else:
        print("Status: CONFIGURED")
        print(f"Sender:   {email_service.sender}")
        print(f"Receiver: {email_service.receiver}")
        print("You can run main.py to trigger a full test send.")
