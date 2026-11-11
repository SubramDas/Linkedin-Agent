---
name: run-pipeline
description: Scouts live AI and tech news, curates the most viral topic using Antigravity's active model, writes an authentic short LinkedIn post, and emails the draft for 1-tap mobile publishing.
---

# /run-pipeline Skill: Autonomous LinkedIn Content Assistant

When this skill is invoked (via `/run-pipeline` or user request to generate a LinkedIn post), execute the following multi-agent procedure:

## Step 1: Scout Real-Time Tech & AI News
Run the Scout Agent to pull the freshest articles from Hacker News, TechCrunch, and ArXiv:
```bash
./venv/bin/python agents/scout.py
```
Parse the articles from the output.

## Step 2: Curate the Winning Topic (Antigravity Reasoning)
Evaluate all scouted articles using your own model intelligence.
- **Deduplication Check:** Check recent files in `state/*.json` or `drafts/*.md` to make sure you do NOT pick any topic covered in the past 14 days.
- **Criteria:** Pick the #1 story with the highest engagement potential for software engineers, AI practitioners, and tech leaders.
- Identify:
  1. `Title`
  2. `Link`
  3. `Source`
  4. `Virality Score` (1-100)
  5. `Why It Matters` (1 sentence)
  6. `Angle` (1 sentence)

## Step 3: Craft the LinkedIn Post (Antigravity Writing)
Write the post directly using your model's authentic voice following these strict rules:

1. **Word Count:** STRICTLY under 120–130 words total (readable in 20 seconds on mobile).
2. **Forbidden:**
   - DO NOT start with "Imagine..." or "Imagine this".
   - DO NOT use the rigid repetitive formula `Emoji + The [Noun]:` on every line.
   - NO corporate fluff ('game-changer', 'testament', 'delve', 'pivotal').
3. **Structure:**
   - **Hook (1–2 punchy lines):** A bold observation, contrarian angle, or tectonic shift that stops the scroll.
   - **Context (1 crisp sentence):** What happened in plain English.
   - **Key Takeaways (Exactly 3 bullets, STRICTLY 1 SHORT LINE EACH):** High-density observations using visual emojis (⚡, 💡, 📌, 🔍) and occasional Unicode bold text (e.g. 𝗧𝗵𝗲 𝗦𝗵𝗶𝗳𝘁:).
   - **Discussion Question (1 provocative sentence):** Forces senior tech pros to comment.
   - **Link:** Original source URL on its own line.
   - **Hashtags:** 3 relevant hashtags.

## Step 4: Deliver to Email and Checkpoint
Use `services/deliver.py` to archive the post and send the email with the mobile 1-tap copy button:
```bash
./venv/bin/python services/deliver.py \
  --title "<ARTICLE_TITLE>" \
  --link "<ARTICLE_LINK>" \
  --source "<SOURCE_NAME>" \
  --score <SCORE> \
  --why "<WHY_IT_MATTERS>" \
  --angle "<ANGLE>" \
  --post "<FULL_POST_CONTENT>"
```

## Step 5: Present the Output
Display:
1. The winning topic and source.
2. The complete formatted LinkedIn post.
3. Confirmation that the draft has been archived and sent to the user's Gmail.
