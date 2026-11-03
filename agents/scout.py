import sys
from pathlib import Path

# Add project root to sys.path so config can be imported from anywhere
sys.path.append(str(Path(__file__).resolve().parent.parent))

import re
from typing import List
import feedparser
from pydantic import BaseModel
from config import RSS_FEEDS


class Article(BaseModel):
    """Represents a standardized news article fetched from RSS."""
    title: str
    link: str
    summary: str
    source: str
    published: str = ""


class ScoutAgent:
    """Agent responsible for scouting and collecting trending tech/AI news."""

    def __init__(self, feeds: dict = None):
        self.feeds = feeds or RSS_FEEDS

    def _clean_html(self, raw_html: str) -> str:
        """Strip HTML tags and excessive whitespace from RSS summaries."""
        clean_text = re.sub(r"<[^>]+>", "", raw_html)
        return " ".join(clean_text.split())

    def fetch_articles(self, limit_per_feed: int = 3) -> List[Article]:
        """Fetch the latest articles from all configured RSS feeds."""
        articles: List[Article] = []

        for source_name, feed_url in self.feeds.items():
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries[:limit_per_feed]:
                    title = getattr(entry, "title", "No Title")
                    link = getattr(entry, "link", "")
                    raw_summary = getattr(entry, "summary", getattr(entry, "description", ""))
                    summary = self._clean_html(raw_summary)
                    published = getattr(entry, "published", getattr(entry, "updated", ""))
                    if not published:
                        published = "Recent"

                    # Truncate overly long summaries to keep token usage low
                    if len(summary) > 300:
                        summary = summary[:297] + "..."

                    articles.append(
                        Article(
                            title=title,
                            link=link,
                            summary=summary,
                            source=source_name,
                            published=published,
                        )
                    )
            except Exception as e:
                print(f"[ScoutAgent] Warning: Failed to fetch {source_name}: {e}")

        return articles


if __name__ == "__main__":
    print("--- Testing ScoutAgent ---")
    scout = ScoutAgent()
    results = scout.fetch_articles(limit_per_feed=2)
    print(f"Collected {len(results)} articles:\n")
    for idx, art in enumerate(results, 1):
        print(f"{idx}. [{art.source}] {art.title}")
        print(f"   Link: {art.link}")
        print(f"   Summary: {art.summary}\n")
