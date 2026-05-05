"""Claude-powered intelligence layer — generates post ideas and analytics review."""
import json

import anthropic
from pydantic import BaseModel

from growth_op_agent.brand import BrandContext
from growth_op_agent.data_sources.aggregator import Context


class PostIdea(BaseModel):
    content: str
    rationale: str
    format: str
    estimated_engagement: str


IDEA_MAX_TOKENS = 4096
REVIEW_MAX_TOKENS = 1024


class IntelligenceLayer:
    def __init__(self, brand: BrandContext, model: str = "claude-opus-4-7") -> None:
        self._client = anthropic.Anthropic()
        self._brand = brand
        self._model = model
        # System prompt is stable — eligible for prompt caching
        self._system = [
            {
                "type": "text",
                "text": brand.to_system_prompt(),
                "cache_control": {"type": "ephemeral"},
            }
        ]

    def generate_post_ideas(self, context: Context, n: int = 10) -> list[PostIdea]:
        prompt = _build_ideas_prompt(
            context,
            n,
            self._brand.post_max_chars,
            [content_format.name for content_format in self._brand.formats],
        )
        message = self._client.messages.create(
            model=self._model,
            max_tokens=IDEA_MAX_TOKENS,
            system=self._system,
            messages=[{"role": "user", "content": prompt}],
        )
        return _parse_ideas(message.content[0].text)

    def review_performance(self, analytics_summary: dict) -> dict:
        """Return strategic insights from recent performance data."""
        prompt = (
            f"Here is our recent post performance:\n\n{json.dumps(analytics_summary, indent=2)}\n\n"
            "Give 3 concise strategic takeaways and 2 suggested content adjustments. "
            "Return only valid JSON with no markdown fences or explanatory text."
        )
        message = self._client.messages.create(
            model=self._model,
            max_tokens=REVIEW_MAX_TOKENS,
            system=self._system,
            messages=[{"role": "user", "content": prompt}],
        )
        return _parse_json_object(message.content[0].text)


def _build_ideas_prompt(
    context: Context,
    n: int,
    max_chars: int,
    format_names: list[str],
) -> str:
    reddit_summary = [
        {"title": p.title, "subreddit": p.subreddit, "votes": p.votes,
         "type": p.post_type, "body": p.body}
        for p in context.reddit_posts[:10]
    ]
    return f"""Generate {n} post ideas.

Decision hierarchy:
1. Follow the stable brand voice and content strategy from the system prompt.
2. Use weekly performance insights as tactical guidance for what to do more/less of.
3. Treat HN and Reddit as a raw opportunity pool. Do not chase a topic unless it supports the strategy or reveals a durable lesson.
4. Prefer original analysis, operating lessons, and practical frameworks over summaries of what happened.
5. At least half of the ideas should use the "photo_post" format — paired with a personal photo of Jamie, a real-life scene, or a moment from daily life. Never suggest a diagram, chart, or graphic for this format.

## Weekly performance insights and tactical adjustments
{json.dumps(context.performance_insights, indent=2)}

## Raw opportunity pool: Top Hacker News stories
{json.dumps([
    {"title": s.title, "score": s.score, "comment": s.top_comment}
    for s in context.hn_stories[:8]
], indent=2)}

## Raw opportunity pool: Hot posts in AI/tech subreddits
{json.dumps(reddit_summary, indent=2)}

Use only these format names — do not invent others:
{json.dumps(format_names, indent=2)}

Prefer "photo_post" as the default. Use the template from the system prompt to determine the exact structure of the "content" field for each format.

Return a JSON array of {n} objects. Each object must have exactly these keys:
- "content": the post text following the format template (max {max_chars} chars, or the format's own limit if stricter)
- "rationale": one sentence on why this will resonate with the audience
- "format": one of the configured format names above
- "estimated_engagement": low, medium, or high

Return only the JSON array — no markdown fences, no commentary."""


def _parse_ideas(raw: str) -> list[PostIdea]:
    text = _strip_json_fence(raw)
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as e:
        preview = text[:500]
        raise ValueError(f"Claude returned malformed idea JSON: {preview!r}") from e

    if not isinstance(parsed, list):
        raise ValueError("Claude idea output must be a JSON array.")
    return [PostIdea.model_validate(item) for item in parsed]


def _parse_json_object(raw: str) -> dict:
    text = _strip_json_fence(raw)
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as e:
        preview = text[:500]
        raise ValueError(f"Claude returned non-JSON performance insights: {preview!r}") from e

    if not isinstance(parsed, dict):
        raise ValueError("Claude performance insights must be a JSON object.")
    return parsed


def _strip_json_fence(raw: str) -> str:
    text = raw.strip()
    if text.startswith("```json"):
        text = text.removeprefix("```json")
    elif text.startswith("```"):
        text = text.removeprefix("```")
    if text.endswith("```"):
        text = text.removesuffix("```")
    return text.strip()
