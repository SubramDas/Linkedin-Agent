import argparse
import sys
import json
from pathlib import Path
from datetime import datetime

# Add project root to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from agents.curator import CuratedTopic
from agents.copywriter import LinkedInDraft
from services.mailer import email_service
from services.checkpoint import DailyCheckpoint
from services.logger import logger


def save_draft_archive(post_content: str, topic_title: str) -> Path:
    """Saves a local markdown archive of the generated draft."""
    drafts_dir = Path(__file__).resolve().parent.parent / "drafts"
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


def deliver(title: str, link: str, source: str, score: int, why: str, angle: str, post: str) -> bool:
    """Saves the draft, updates daily state checkpoint, and sends email notification."""
    checkpoint = DailyCheckpoint()

    topic = CuratedTopic(
        selected_title=title,
        selected_link=link,
        selected_source=source,
        virality_score=score,
        why_it_matters=why,
        hook_angle=angle,
    )

    draft = LinkedInDraft(
        hook=post.split("\n\n")[0] if "\n\n" in post else post[:100],
        key_takeaways=[],
        discussion_question="",
        hashtags=[],
        full_post=post,
    )

    # 1. Update checkpoint
    checkpoint.save_topic(topic)
    checkpoint.save_draft(draft)

    # 2. Save local markdown archive
    saved_path = save_draft_archive(draft.full_post, topic.selected_title)
    logger.info(f"✓ Archived copy saved to: {saved_path}")

    # 3. Send email with 1-tap mobile copy button
    logger.info("Delivering draft to your email...")
    email_sent = email_service.send_draft(draft, topic)

    if email_sent:
        checkpoint.mark_email_sent()
        logger.info("✓ Email sent and checkpoint marked complete!")
        return True
    else:
        logger.warning("⚠️ Email could not be sent. Check email settings.")
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Deliver generated LinkedIn draft via email and checkpoint.")
    parser.add_argument("--title", required=True, help="Title of curated story")
    parser.add_argument("--link", required=True, help="Link of curated story")
    parser.add_argument("--source", default="Tech News", help="Source publication")
    parser.add_argument("--score", type=int, default=90, help="Virality score (1-100)")
    parser.add_argument("--why", default="Important industry development", help="Why it matters")
    parser.add_argument("--angle", default="Impact on software and AI", help="Angle")
    parser.add_argument("--post", required=True, help="Full ready-to-post LinkedIn text")

    args = parser.parse_args()
    success = deliver(
        title=args.title,
        link=args.link,
        source=args.source,
        score=args.score,
        why=args.why,
        angle=args.angle,
        post=args.post,
    )
    sys.exit(0 if success else 1)
