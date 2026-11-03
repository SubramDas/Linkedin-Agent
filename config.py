import os
from pathlib import Path
from dotenv import load_dotenv

# Ensure system SSL certificates are found on Linux
if not os.environ.get("SSL_CERT_FILE") and Path("/etc/ssl/certs/ca-certificates.crt").exists():
    os.environ["SSL_CERT_FILE"] = "/etc/ssl/certs/ca-certificates.crt"

# Load variables from .env file
load_dotenv()

# Gemini configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
raw_models = os.getenv("GEMINI_MODELS", "gemini-3-flash-preview,gemini-3.5-flash,gemini-3.5-flash-lite")
GEMINI_MODELS = [m.strip() for m in raw_models.split(",") if m.strip()]
GEMINI_MODEL = GEMINI_MODELS[0] if GEMINI_MODELS else "gemini-3-flash-preview"
GEMINI_CALL_DELAY_SECONDS = float(os.getenv("GEMINI_CALL_DELAY_SECONDS", "30.0"))

# Email notification configuration (Gmail SMTP)
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "")
SENDER_APP_PASSWORD = os.getenv("SENDER_APP_PASSWORD", "")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL", "")

# Optional GitHub Pages Web Copier URL (e.g. https://yourusername.github.io/LinkedIn_posts/)
WEB_REVIEW_URL = os.getenv("WEB_REVIEW_URL", "")

# Curated tech & AI RSS feed sources
RSS_FEEDS = {
    "Hacker News": "https://news.ycombinator.com/rss",
    "TechCrunch": "https://techcrunch.com/feed/",
    "ArXiv AI": "https://export.arxiv.org/rss/cs.AI",
    "The Verge - Tech": "https://www.theverge.com/rss/technology/index.xml",
}
