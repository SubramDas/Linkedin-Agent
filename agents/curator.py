import sys
from pathlib import Path
from typing import List
from pydantic import BaseModel, Field

# Add project root to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from agents.scout import Article, ScoutAgent
from services.llm import llm_service


class CuratedTopic(BaseModel):
    """Structured representation of the top chosen article selected for LinkedIn."""
    selected_title: str = Field(description="The exact title of the chosen article.")
    selected_link: str = Field(description="URL link of the chosen article.")
    selected_source: str = Field(description="The source publisher (e.g. Hacker News, TechCrunch).")
    virality_score: int = Field(description="Engagement score from 1 to 100 based on interest to tech pros.")
    why_it_matters: str = Field(description="1-2 sentences explaining why developers and tech leads should care.")
    hook_angle: str = Field(description="The intriguing angle or perspective to pitch in the post.")


class CuratorAgent:
    """Agent responsible for filtering raw news and picking the highest-impact story."""

    SYSTEM_INSTRUCTION = """
    You are an elite Tech Content Strategist and LinkedIn Growth Specialist.
    Your goal is to review a list of trending tech and AI articles and pick the SINGLE MOST compelling story.
    
    Evaluation criteria:
    1. Relevance: High impact for software engineers, AI practitioners, and tech leaders.
    2. Discussion Potential: Topics that spark debate, offer learning value, or reveal major shifts.
    3. Timeliness: Immediate interest over niche theoretical trivia.
    
    You must output your choice strictly matching the required schema.
    """

    def __init__(self, llm=llm_service):
        self.llm = llm

    def curate(
        self,
        articles: List[Article],
        exclude_topics: Optional[List[Dict[str, str]]] = None,
    ) -> CuratedTopic:
        """Selects the best topic from a list of scouted articles, excluding recent coverage."""
        if not articles:
            raise ValueError("No articles provided to curate.")

        exclude_links = {t.get("link", "").strip() for t in (exclude_topics or []) if t.get("link")}
        exclude_titles = [t.get("title", "").strip().lower() for t in (exclude_topics or []) if t.get("title")]

        # Filter out articles that directly match previously covered links or titles
        eligible_articles = []
        for a in articles:
            if a.link and a.link.strip() in exclude_links:
                continue
            if a.title and any(past_t in a.title.lower() for past_t in exclude_titles):
                continue
            eligible_articles.append(a)

        # Fallback to all articles if everything was somehow excluded
        candidates = eligible_articles if eligible_articles else articles

        # Format articles into readable text for the prompt
        formatted_list = []
        for idx, art in enumerate(candidates, 1):
            formatted_list.append(
                f"[{idx}] Source: {art.source}\n"
                f"Title: {art.title}\n"
                f"Summary: {art.summary}\n"
                f"Link: {art.link}\n"
            )
        articles_text = "\n".join(formatted_list)

        exclusion_note = ""
        if exclude_titles:
            past_titles_str = "\n".join(f"- {t}" for t in exclude_titles[:5])
            exclusion_note = f"\nDO NOT select any story that is substantively the same as these recently covered topics:\n{past_titles_str}\n"

        prompt = f"""
        Here are today's trending tech stories:
        
        {articles_text}
        {exclusion_note}
        Carefully evaluate each one. Select the #1 story that will get the highest engagement and discussion on LinkedIn.
        """

        return self.llm.generate_structured(
            prompt=prompt,
            response_schema=CuratedTopic,
            system_instruction=self.SYSTEM_INSTRUCTION,
        )


if __name__ == "__main__":
    print("--- Testing Scout + Curator Pipeline ---")
    scout = ScoutAgent()
    print("1. Fetching live articles...")
    articles = scout.fetch_articles(limit_per_feed=2)
    print(f"Scouted {len(articles)} articles.")

    curator = CuratorAgent()
    print("\n2. Curating best topic with Gemini...")
    top_pick = curator.curate(articles)

    print("\n🏆 Winning Selection:")
    print(f"Title:    {top_pick.selected_title}")
    print(f"Source:   {top_pick.selected_source}")
    print(f"Score:    {top_pick.virality_score}/100")
    print(f"Why:      {top_pick.why_it_matters}")
    print(f"Angle:    {top_pick.hook_angle}")
    print(f"Link:     {top_pick.selected_link}")
