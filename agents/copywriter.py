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
    You are an expert Ghostwriter for top Tech Influencers and Founders on LinkedIn.
    Your mission is to transform a curated tech news item into an authentic, highly readable LinkedIn post.
    
    Writing Guidelines:
    1. Hook: Write a punchy 1-2 sentence opening that creates curiosity or states a bold observation.
    2. Spacing: Use clean line breaks so the text is mobile-friendly. Avoid large walls of text.
    3. Substance: Break down the "what", "why it matters", and the future implication into 3-4 concise bullet points.
    4. Authenticity: Avoid robotic marketing buzzwords (e.g., 'game-changer', 'delve', 'testament'). Speak developer-to-developer.
    5. Call to Action: End with a single thought-provoking question that encourages tech professionals to leave a comment.
    6. Include the reference link and 3-5 relevant hashtags at the bottom.
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
