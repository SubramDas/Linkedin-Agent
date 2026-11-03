import os
from datetime import datetime
from pathlib import Path

from agents.scout import ScoutAgent, Article
from agents.curator import CuratorAgent, CuratedTopic
from agents.copywriter import CopywriterAgent, LinkedInDraft
from services.mailer import email_service
from services.checkpoint import DailyCheckpoint
from services.logger import logger


def save_draft_archive(post_content: str, topic_title: str) -> Path:
    """Saves a local markdown archive of the generated draft."""
    drafts_dir = Path(__file__).resolve().parent / "drafts"
    drafts_dir.mkdir(exist_ok=True)

    today_str = datetime.now().strftime("%Y-%m-%d")
    archive_file = drafts_dir / f"{today_str}.md"

    content = f"""# LinkedIn Draft - {today_str}

## Selected Story
{topic_title}

---

## Ready-to-Post Content
{post_content}
"""
    archive_file.write_text(content, encoding="utf-8")
    return archive_file


def run_pipeline():
    """Runs the full multi-agent LinkedIn content pipeline with checkpointing & logging."""
    checkpoint = DailyCheckpoint()

    logger.info("=" * 60)
    logger.info("🤖 STARTING AI LINKEDIN CONTENT ASSISTANT")
    logger.info(f"⏰ Execution Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"📁 Daily Checkpoint: state/{checkpoint.today}.json")
    logger.info(f"📝 Daily Log File:   logs/pipeline_{checkpoint.today}.log")
    logger.info("=" * 60)

    # 1. Scout Agent: Pull trending news (or resume from checkpoint)
    logger.info("\n[Step 1/4] ScoutAgent: Gathering live tech & AI news...")
    cached_articles = checkpoint.get_articles()
    if cached_articles:
        articles = [Article(**a) for a in cached_articles]
        logger.info(f"↷ Reusing cached: Loaded {len(articles)} scouted articles from checkpoint.")
    else:
        scout = ScoutAgent()
        articles = scout.fetch_articles(limit_per_feed=3)
        checkpoint.save_articles(articles)
        logger.info(f"✓ Scouted {len(articles)} raw articles and saved to checkpoint.")

    # Display all scouted articles with timestamps in terminal & log
    logger.info("\n--- 📰 Scouted Articles Today ---")
    for idx, art in enumerate(articles, 1):
        logger.info(f"{idx}. [{art.source}] {art.title}")
        logger.info(f"   Published: {art.published}")
        logger.info(f"   Link:      {art.link}")
        logger.info(f"   Summary:   {art.summary}\n")

    # 2. Curator Agent: Evaluate and select winning story (or reuse cached topic)
    logger.info("[Step 2/4] CuratorAgent: Analyzing engagement potential with Gemini...")
    cached_topic = checkpoint.get_topic()
    if cached_topic:
        topic = CuratedTopic(**cached_topic)
        logger.info(f"↷ Reusing cached topic from checkpoint: {topic.selected_title}")
    else:
        curator = CuratorAgent()
        topic = curator.curate(articles)
        checkpoint.save_topic(topic)
        logger.info(f"✓ Winning Story: {topic.selected_title}")
        logger.info(f"✓ Virality Score: {topic.virality_score}/100")
        logger.info(f"✓ Angle: {topic.hook_angle}")

    # 3. Copywriter Agent: Always crafts a fresh LinkedIn post on every run
    logger.info("\n[Step 3/4] CopywriterAgent: Generating a fresh tailored LinkedIn draft...")
    copywriter = CopywriterAgent()
    draft = copywriter.draft_post(topic)
    checkpoint.save_draft(draft)
    logger.info("✓ Fresh draft successfully written and updated in checkpoint!")

    # Save / update local markdown archive
    saved_path = save_draft_archive(draft.full_post, topic.selected_title)
    logger.info(f"✓ Archived copy updated in: {saved_path}")

    # 4. Delivery: Send email alert with fresh draft
    logger.info("\n[Step 4/4] EmailService: Delivering fresh draft to your inbox...")
    email_sent = email_service.send_draft(draft, topic)

    if email_sent:
        checkpoint.mark_email_sent()
        logger.info("✓ Email sent and checkpoint marked complete!")

    logger.info("\n" + "=" * 60)
    logger.info("🎉 PIPELINE RUN COMPLETE")
    logger.info("=" * 60)
    logger.info("\n📄 GENERATED POST:\n")
    logger.info(draft.full_post)
    logger.info("\n" + "-" * 60)

    if email_sent:
        logger.info("📬 Check your email inbox to review and post!")
    else:
        logger.info("💡 Note: Email wasn't sent. The checkpoint will allow you to retry without losing progress.")


if __name__ == "__main__":
    run_pipeline()
