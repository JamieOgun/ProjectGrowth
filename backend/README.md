# GrowthOpAgent

AI-powered social media content agent. Uses Claude as the intelligence layer to generate post ideas from live data sources (Hacker News and Reddit) informed by your brand context and historical post performance.

Publishing is intentional and manual — the agent generates idea records as JSON. You decide what to post.

---

## Architecture

```
Data sources (async)
  ├── Hacker News       → public API, no credentials
  └── Reddit            → public JSON API via ZenRows
          │
          ▼
    DataAggregator  →  Context (pydantic)
          │
          ▼
  IntelligenceLayer (Claude)
          │
          ▼
    list[PostIdea]  →  IdeaStore  →  data/ideas/<date>.json
                                    (review manually)

Analytics (separate cadence)
  PerformanceAnalytics  →  weekly_snapshot.json  (pure Python, deterministic)
  WeeklyReview          →  weekly_insights.json  (Claude, once per ISO week)
          │
          └──► fed back into Context.performance_insights on next cycle
```

### Key design decisions

**Deterministic performance context.** The snapshot and LLM review are computed once per ISO week and persisted to disk. Every content cycle within that week reads the same stable files — the feedback signal doesn't change between runs, making content strategy consistent and auditable.

**No live publishing.** X API write access is expensive. Ideas are saved to `data/ideas/<date>.json` for manual review and copy-paste. X read-only API is kept for fetching your own post engagement metrics.

**Minimal review state.** Idea records currently support only `generated` and `rejected`.

**Pydantic at every boundary.** All data entering the system from external sources is validated through pydantic models. `.model_dump()` is only called at file-write boundaries, not between modules.

**ZenRows for Reddit scraping.** Reddit blocks unauthenticated requests, so the Reddit source uses ZenRows for proxy rotation.

---

## Project structure

```
growth_op_agent/
├── brand/
│   └── brand_context.py      BrandContext model, loaded from config/brand_voice.yaml
├── data_sources/
│   ├── aggregator.py         DataAggregator — returns typed Context model
│   ├── hackernews.py         HackerNewsStory — HN Firebase API (no auth)
│   ├── reddit.py             RedditPost — public JSON API via ZenRows
│   ├── performance.py        OwnPerformanceSource — reads weekly snapshot files
│   └── zenrows.py            Shared ZenRows HTTP helper
├── intelligence/
│   └── intelligence.py       IntelligenceLayer — Claude API with prompt caching
├── content/
│   ├── idea_generator.py     IdeaGenerator — orchestrates fetch → generate → persist
│   └── idea_store.py         IdeaRecord, IdeaStatus, IdeaStore JSON persistence
├── analytics/
│   ├── performance.py        PerformanceAnalytics — metrics + weekly snapshot
│   └── weekly_review.py      WeeklyReview — LLM review, ISO-week staleness gate
├── publishing/
│   └── scheduler.py          PublishScheduler — APScheduler wrapper
├── orchestrator/
│   └── orchestrator.py       Orchestrator — wires all components together
├── cli/
│   └── test_commands.py      Click test subcommands
└── main.py                   CLI entry point
```

---

## Setup

**Requirements:** Python 3.11+, [uv](https://docs.astral.sh/uv/)

```bash
git clone <repo>
cd GrowthOpAgent
cd backend
uv sync
cp .env.example .env
```

### Environment variables

```bash
# .env

# Required to generate ideas
ANTHROPIC_API_KEY=

# Required for Reddit scraping
ZENROWS_API_KEY=

# Optional — required only to refresh your own post engagement metrics
TWITTER_BEARER_TOKEN=
```

### Brand configuration

Edit `config/brand_voice.yaml`:

```yaml
brand:
  name: "Your Name"
  handle: "@yourhandle"

voice:
  tone: "authoritative yet approachable"
  style: "concise, insight-driven"
  avoid:
    - "corporate jargon"
    - "excessive hashtags"
    - "clickbait"

guidelines:
  post_max_chars: 280
  preferred_formats:
    - "insight + supporting evidence"
    - "contrarian take + reasoning"
  target_audience: "founders, operators, growth practitioners"

strategic_pillars:
  - "product-led growth"
  - "data-driven decision making"

competitors:
  - handle: "@competitor1"
```

### Agent configuration

Edit `config/settings.yaml`:

```yaml
intelligence:
  model: claude-opus-4-7   # Claude model to use

publishing:
  posts_per_day: 10
  schedule_times:
    - "09:00"
    - "13:00"
    - "18:00"
  timezone: "UTC"           # Scheduler timezone

analytics:
  performance_review_interval_hours: 24
```

---

## CLI

Run all backend commands from `/Users/Jamie/personal-project/GrowthOpAgent/backend`.

```bash
# Recommended — no activation needed
uv run growth-op --help

# Or activate the venv once and use growth-op directly
source .venv/bin/activate
growth-op --help
```

### Run

```bash
# Generate ideas once and save to data/ideas/<today>.json
growth-op run --once

# Start the scheduler (generates ideas daily at 06:00, analytics weekly)
growth-op run
```

### Test

Verify each module independently before running the full cycle.

```bash
growth-op test --help       # list all modules with key requirements

growth-op test brand        # parse brand_voice.yaml, print system prompt
growth-op test hn           # fetch top HN stories
growth-op test snapshot     # compute weekly performance snapshot
growth-op test reddit       # fetch hot posts from target subreddits
growth-op test aggregator   # run all data sources, print counts
growth-op test intelligence  # call Claude with a minimal context
```

**Keys required per module:**

| Module | Keys |
|---|---|
| `brand`, `hn`, `snapshot` | none |
| `reddit`, `aggregator` | `ZENROWS_API_KEY` |
| `intelligence` | `ANTHROPIC_API_KEY` |

### Recommended first-run order

```bash
growth-op test brand          # confirm config is valid
growth-op test hn             # confirm network access
growth-op test reddit         # confirm ZenRows key
growth-op test intelligence   # confirm Claude key + brand voice
growth-op run --once          # full cycle
```

---

## Data flow

### Content cycle (`growth-op run --once`)

1. `DataAggregator.fetch_all()` — fetches HN and Reddit, and reads performance files
2. `IntelligenceLayer.generate_post_ideas(context)` — sends context to Claude, returns `list[PostIdea]`
3. `IdeaGenerator._persist()` — saves ideas as `IdeaRecord` objects to `data/ideas/<date>.json`

### Idea review state

Generated ideas are persisted through `IdeaStore`.

Supported statuses:

| Status | Meaning |
|---|---|
| `generated` | The idea was created by the content cycle and has not been rejected. |
| `rejected` | The idea was manually rejected and should not be used. |

The only supported transition is `generated` → `rejected`.

### Analytics cycle (weekly, via scheduler)

1. `PerformanceAnalytics.refresh_metrics()` — pulls engagement numbers from X API for your posts
2. `PerformanceAnalytics.compute_weekly_snapshot()` — pure Python metrics, writes `data/performance/weekly_snapshot.json`
3. `WeeklyReview.run_if_stale()` — if no insights exist for this ISO week, calls Claude → writes `data/performance/weekly_insights.json`

On the next content cycle, `OwnPerformanceSource.fetch_context()` reads both files and injects them into the `Context` passed to Claude, closing the feedback loop.

---

## Pydantic models

| Model | Module | Description |
|---|---|---|
| `BrandContext` | `brand/brand_context.py` | Brand voice and guidelines |
| `HackerNewsStory` | `data_sources/hackernews.py` | HN story with score |
| `RedditPost` | `data_sources/reddit.py` | Subreddit post with votes |
| `Context` | `data_sources/aggregator.py` | Unified input to intelligence layer |
| `PostIdea` | `intelligence/intelligence.py` | Generated post with rationale |
| `IdeaRecord` | `content/idea_store.py` | Persisted generated idea with review status |
| `IdeaStatus` | `content/idea_store.py` | `generated` or `rejected` |
| `PerformanceSnapshot` | `analytics/performance.py` | Weekly computed metrics |
| `WeekOf` | `analytics/performance.py` | ISO year + week identifier |
| `TopPost` | `analytics/performance.py` | Top performing post summary |
| `WeeklyInsights` | `analytics/weekly_review.py` | LLM strategic review (extra fields allowed) |

---

## Target subreddits

Configured in `growth_op_agent/data_sources/reddit.py`:

```python
SUBREDDITS = [
    "AgentsOfAI",
    "LocalLLaMA",
    "singularity",
    "ClaudeAI",
    "ChatGPT",
]
```

---

## Running tests

```bash
uv run pytest
```
