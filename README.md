# AI LinkedIn Content Assistant

An automated, 100% free, multi-agent pipeline that scouts trending AI and tech news, filters for high engagement, generates polished LinkedIn post drafts, and emails them to you daily for review before posting.

---

## 🎯 Objectives
- **Zero Cost:** Runs entirely on free APIs, free scheduling, and standard email protocols.
- **Account Safety:** Human-in-the-loop (email review) eliminates bot detection and bans on LinkedIn.
- **High Quality:** Multi-agent separation ensures content is both relevant and well-crafted.

---

## 🏗️ Architecture

```text
[Tech/AI RSS Feeds]
        │
        ▼
[Agent 1: The Scout] ────────► Collects top 10-15 trending stories
        │
        ▼
[Agent 2: The Curator] ──────► Filters and picks top 1-2 viral/high-value topics
        │
        ▼
[Agent 3: The Copywriter] ───► Writes engaging, ready-to-post LinkedIn draft
        │
        ▼
[Delivery: Email Notifier] ──► Delivers draft to your inbox for 1-click review & posting
```

---

## 🤖 The Multi-Agent System

1. **Agent 1: The Scout (Collector)**
   - **Role:** Fetches raw headlines, summaries, and URLs from tech and AI RSS feeds.
   - **Sources:** Hacker News, TechCrunch, ArXiv AI, Verge Tech.

2. **Agent 2: The Curator (Engagement Filter)**
   - **Role:** Evaluates stories based on audience interest, tech relevance, and discussion potential.
   - **Output:** Selects the top story and provides the core hook/angle.

3. **Agent 3: The Copywriter (Post Creator)**
   - **Role:** Converts the selected story into an engaging LinkedIn post with:
     - Clear hook (first 2 lines).
     - Concise, easy-to-read takeaways (bullet points).
     - Discussion prompt to drive comments.
     - Relevant hashtags.

4. **Delivery: Email Notifier**
   - **Role:** Formats the final draft into an email and sends it directly to your inbox via free Gmail SMTP.

---

## 🛠️ Tech Stack (100% Free)
- **Language:** Python 3.10+
- **LLM Engine:** Google Gemini Free API (or Groq Cloud Free Tier)
- **Data Ingestion:** `feedparser` (RSS parser)
- **Email Service:** Standard Python `smtplib` / `email` (using Gmail App Password)
- **Scheduler:** GitHub Actions (cron) or local system cron

---

## 📂 Project Structure

```text
LinkedIn_posts/
├── README.md                 # Project overview and instructions
├── requirements.txt          # Python dependencies
├── .env.example              # Template for API keys and email credentials
├── config.py                 # Configuration and feed URLs
├── agents/
│   ├── __init__.py
│   ├── scout.py              # Agent 1: RSS fetching
│   ├── curator.py            # Agent 2: Story filtering & selection
│   └── copywriter.py         # Agent 3: Post drafting
├── services/
│   ├── __init__.py
│   ├── llm.py                # LLM client wrapper (Gemini / Groq)
│   └── mailer.py             # Email notification service
└── main.py                   # Pipeline orchestrator
```

---

## 📋 Next Steps
1. Create virtual environment and install core dependencies.
2. Set up environment variables (`.env.example`).
3. Build Agent 1 ([scout.py](file:///home/subramd/MyProjects/LinkedIn_posts/agents/scout.py)) to fetch live RSS feeds.
4. Implement LLM connection and Agents 2 & 3.
5. Implement email sender service.
6. Connect all parts in [main.py](file:///home/subramd/MyProjects/LinkedIn_posts/main.py).
# Linkedin-Agent
