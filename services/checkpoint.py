import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any


class DailyCheckpoint:
    """Manages saving and loading the daily pipeline execution state."""

    def __init__(self, base_dir: Optional[Path] = None):
        self.state_dir = (base_dir or Path(__file__).resolve().parent.parent) / "state"
        self.state_dir.mkdir(exist_ok=True)
        self.today = datetime.now().strftime("%Y-%m-%d")
        self.state_file = self.state_dir / f"{self.today}.json"
        self.data: Dict[str, Any] = self._load()

    def _load(self) -> Dict[str, Any]:
        """Loads today's state if it exists, otherwise initializes an empty state."""
        if self.state_file.exists():
            try:
                with open(self.state_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"[Checkpoint] Warning: Corrupted state file, resetting: {e}")
        return {
            "date": self.today,
            "scouted_articles": None,
            "curated_topic": None,
            "draft": None,
            "email_sent": False,
        }

    def _save(self):
        """Persists current state to disk."""
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2)

    def is_completed(self) -> bool:
        """Returns True if today's post has already been drafted and sent."""
        return bool(self.data.get("email_sent", False))

    # --- Step 1: Scouted articles ---
    def get_articles(self) -> Optional[List[Dict[str, Any]]]:
        return self.data.get("scouted_articles")

    def save_articles(self, articles: List[Any]):
        self.data["scouted_articles"] = [
            a.model_dump() if hasattr(a, "model_dump") else a for a in articles
        ]
        self._save()

    # --- Step 2: Curated topic ---
    def get_topic(self) -> Optional[Dict[str, Any]]:
        return self.data.get("curated_topic")

    def save_topic(self, topic: Any):
        self.data["curated_topic"] = (
            topic.model_dump() if hasattr(topic, "model_dump") else topic
        )
        self._save()

    # --- Step 3: Draft ---
    def get_draft(self) -> Optional[Dict[str, Any]]:
        return self.data.get("draft")

    def save_draft(self, draft: Any):
        self.data["draft"] = (
            draft.model_dump() if hasattr(draft, "model_dump") else draft
        )
        self._save()

    # --- Step 4: Email sent ---
    def mark_email_sent(self):
        self.data["email_sent"] = True
        self._save()
