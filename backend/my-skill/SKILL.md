---
name: my-skill
description: GrowthOpAgent skill — generates branded social media post ideas using the intelligence layer. Use when the user asks to generate posts, run a content cycle, or create ideas for X/Twitter.
---

# GrowthOpAgent Content Generation Skill

## What this skill does
Runs a full content cycle: fetches Hacker News, Reddit, and own performance context, passes them through Claude's intelligence layer with brand context, and produces post ideas ranked by estimated engagement.

## When to use
- User says "generate post ideas" or "run the content cycle"
- User wants to review today's generated ideas
- User wants to test the intelligence layer output

## Inputs needed
- `config/brand_voice.yaml` populated with real brand details
- `config/settings.yaml` with desired model and schedule
- `.env` with `ANTHROPIC_API_KEY` set

## Steps

1. Ensure dependencies are installed:
   ```bash
   uv sync --extra dev
   ```

2. Run a single content cycle:
   ```bash
   growth-op run --once
   ```
   This generates ideas and prints them without posting.

3. Review the ideas output. Each idea shows:
   - Post content (ready to publish)
   - Rationale (why it should resonate)
   - Estimated engagement tier

4. Review and post manually. Idea records currently support only `generated` and `rejected` status.

## Validation
- You should see post ideas printed to the terminal
- No tweets are sent
- Ideas are saved to `data/ideas/<today>.json`

## Common issues
- `ANTHROPIC_API_KEY not set` → add to `.env`
- Empty Reddit posts → configure `ZENROWS_API_KEY`
- Ideas don't match brand voice → update `config/brand_voice.yaml`
