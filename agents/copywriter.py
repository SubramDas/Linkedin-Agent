import sys
from pathlib import Path
from typing import List
from pydantic import BaseModel, Field

# Add project root to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from agents.curator import CuratedTopic, CuratorAgent
from agents.scout import ScoutAgent
from services.llm import llm_service


class LinkedInDraft(BaseModel):
    """Represents a formatted, high-engagement LinkedIn post draft."""
    hook: str = Field(description="Attention-grabbing first 1-2 lines before the '...see more' button.")
    key_takeaways: List[str] = Field(description="3-4 bullet points breaking down the story concisely.")
    discussion_question: str = Field(description="A provocative, conversational question to invite comments.")
    hashtags: List[str] = Field(description="3-5 relevant, non-spammy hashtags.")
    full_post: str = Field(description="The complete, copy-paste ready LinkedIn post.")


class CopywriterAgent:
    """Agent responsible for crafting engaging LinkedIn posts from curated topics."""

    SYSTEM_INSTRUCTION = """
    You are an elite Ghostwriter for top Tech Influencers and AI Founders on LinkedIn.
    Your mission is to transform a curated tech news item into an authentic, visually striking LinkedIn post that stops the scroll.
    
    Formatting & Writing Guidelines:
    1. The Real-Life Scenario Hook (CRITICAL):
       - ALWAYS open with a vivid, relatable 1-2 sentence real-world example: "Imagine [everyday scenario/struggle]... [how this tech changes that moment]."
       - Example: "Imagine walking into a meeting 15 minutes late, glancing at your wrist, and having instant bullet points of what you missed. Apple just started beta testing this."
       - Make it immediately tangible to a regular person or software engineer.
    
    2. Ultra-Short, Punchy Bullets (STRICT LIMIT):
       - Keep bullet points crisp and brief: MAX 1-2 SHORT LINES per bullet. No long run-on sentences!
       - Format: [Emoji] 𝗕𝗼𝗹𝗱 𝗨𝗻𝗶𝗰𝗼𝗱𝗲 𝗟𝗮𝗯𝗲𝗹: [One crisp sentence takeaway].
       - Example:
         ⚡ 𝗧𝗵𝗲 𝗦𝗵𝗶𝗳𝘁: On-device models now process live audio with zero cloud latency.
         📌 𝗧𝗵𝗲 𝗨𝘀𝗲-𝗖𝗮𝘀𝗲: Auto-captures action items without you touching a keyboard.
         🔍 𝗧𝗵𝗲 𝗖𝗮𝘁𝗰𝗵: Always-listening wearables will test workplace privacy boundaries.

    3. LinkedIn Bolding (Unicode): DO NOT use markdown asterisks (**bold**)! Use Unicode bold sans-serif characters (e.g., 𝗧𝗵𝗲 𝗕𝗶𝗴 𝗣𝗶𝗰𝘁𝘂𝗿𝗲:, 𝗪𝗵𝘆 𝗜𝘁 𝗠𝗮𝘁𝘁𝗲𝗿𝘀:) for labels.
    4. Mobile Spacing: Use double line breaks between points so it breathes nicely on mobile screens.
    5. Call to Action: End with a single thought-provoking question preceded by 💬 to spark comments.
    6. Reference & Hashtags: Include the original link and 3-5 relevant hashtags at the bottom.
    """

    def __init__(self, llm=llm_service):
        self.llm = llm

    def draft_post(self, topic: CuratedTopic) -> LinkedInDraft:
        """Converts a CuratedTopic into a finished LinkedIn post draft."""
        prompt = f"""
        Draft a high-impact LinkedIn post based on this curated topic:
        
        Headline: {topic.selected_title}
        Source: {topic.selected_source}
        Link: {topic.selected_link}
        Why it matters: {topic.why_it_matters}
        Recommended Angle: {topic.hook_angle}
        Virality Score: {topic.virality_score}/100
        
        Generate the post strictly adhering to the LinkedInDraft schema.
        Ensure 'full_post' is ready to copy and paste directly into LinkedIn.
        """

        return self.llm.generate_structured(
            prompt=prompt,
            response_schema=LinkedInDraft,
            system_instruction=self.SYSTEM_INSTRUCTION,
        )


if __name__ == "__main__":
    print("--- Testing Full Agent Pipeline (Scout -> Curator -> Copywriter) ---")
    
    print("1. Scout is fetching news...")
    scout = ScoutAgent()
    articles = scout.fetch_articles(limit_per_feed=2)
    
    print("\n2. Curator is picking the top story...")
    curator = CuratorAgent()
    topic = curator.curate(articles)
    print(f"   Selected: {topic.selected_title} ({topic.virality_score}/100)")
    
    print("\n3. Copywriter is drafting the LinkedIn post...")
    copywriter = CopywriterAgent()
    draft = copywriter.draft_post(topic)
    
    print("\n" + "="*50)
    print("📄 READY-TO-POST LINKEDIN DRAFT:")
    print("="*50)
    print(draft.full_post)
    print("="*50)
