import type { Idea, WeeklyPost, StatCardData } from "./types";

export const IDEAS: Idea[] = [
  {
    id: "86070576762d40e68ddd80beb2397854",
    format: "photo_post",
    engagement: "HIGH",
    hook: "built an AI feature last week that worked perfectly in testing...",
    content: `photo_brief: a photo of me at my desk with multiple screens, mid-build
---
built an AI feature last week that worked perfectly in testing.

deployed it. real users found 3 edge cases in the first hour that none of my prompts accounted for.

the gap between demo and production is where most AI products quietly die. the models are good enough — the orchestration around them is what's hard.

what's the messiest production edge case you've hit with an LLM?`,
    rationale:
      "Directly addresses the trending Reddit conversation about AI failing at scale, but grounds it in Jamie's own building experience — exactly the 'build in public' micro-case-study format that the performance insights recommend.",
    source: "personal · last sprint",
    chars: 412,
    status: "generated",
  },
  {
    id: "92d449e952f44aec9f9a4a15ed971dec",
    format: "contrarian",
    engagement: "HIGH",
    hook: "Sam Altman funded a $60M UBI study, found it didn't improve health...",
    content: `Sam Altman funded a $60M UBI study. result: $1k/month didn't improve physical health, mental health, or employment outcomes vs. control. the people building AI think they know what humans need after AI takes the jobs. they don't.`,
    rationale:
      "The Sam Altman UBI pivot is trending heavily on Reddit — this contrarian take captures the absurdity without lecturing, which aligns with brand voice and should drive quote tweets and replies.",
    source: "OpenResearch · Jul 2024",
    chars: 234,
    status: "generated",
  },
  {
    id: "417edca31cb44664943f261d202aeeb5",
    format: "photo_post",
    engagement: "MEDIUM",
    hook: "95% of enterprise AI pilots deliver zero measurable financial impact...",
    content: `photo_brief: a photo of me at a coffee shop with a notebook or laptop open
---
95% of enterprise AI pilots deliver zero measurable financial impact.

that MIT stat keeps coming up and honestly it matches what I see. most teams start with "let's add AI" instead of "what decision is too slow or too expensive right now."

the projects I've seen work all started from a specific, boring, painful workflow. not from the model.

what's the most boring AI use case you've seen actually work in production?`,
    rationale:
      "Turns a viral Reddit discussion into an original insight post grounded in Jamie's experience, invites practical responses, and positions Jamie as someone who builds rather than just comments.",
    source: "MIT NANDA · 2025",
    chars: 389,
    status: "generated",
  },
  {
    id: "1076f7b551cb4fe5a1ff3f0b70af3f53",
    format: "short_form",
    engagement: "HIGH",
    hook: "the most valuable engineers in 2026 aren't the ones who can prompt...",
    content: `Bun is being ported from Zig to Rust.

right after being acquired by Anthropic.

the Zig project has an anti-AI contribution policy. Bun's team wanted to upstream AI-generated code. Zig said no.

so now it's a full rewrite instead.

the second-order effects of AI policies on open source dependencies are going to get very weird very fast`,
    rationale:
      "Connects two trending HN stories into a single sharp observation about where open source is heading — original analysis that builders will want to discuss and share.",
    source: "HN · today",
    chars: 298,
    status: "generated",
  },
  {
    id: "4008c8c12fe745fbb9bae60c586d6d09",
    format: "contrarian",
    engagement: "MEDIUM",
    hook: 'everyone says "learn AI or get left behind." wrong frame...',
    content: `photo_brief: a photo of me walking through a Tokyo street or train station
---
building in Tokyo taught me something I didn't expect.

the default here is to ship something small that works perfectly before adding features. in London and SF the default is to ship something ambitious that mostly works.

both approaches break in different ways. but I've started noticing which AI products feel like they were built with which philosophy.

do you default to scope or to polish?`,
    rationale:
      "Leverages Jamie's rare London/Tokyo vantage point, ties a personal observation to a product-building lesson, and invites discussion.",
    source: "personal",
    chars: 341,
    status: "generated",
  },
  {
    id: "430f0cfd019a4ccca48cc0c76e7a7fe2",
    format: "how_to",
    engagement: "MEDIUM",
    hook: "how I cut Claude API costs 73% on a production agent...",
    content: `If you're building with AI and want your posts to actually get shared, not just liked:

Show the tradeoff you made, not just the result.
Include one number or data point from real usage.
End with the question you still don't know the answer to.

People share posts that make them look thoughtful by association. Vulnerability + specificity is what gets bookmarked.`,
    rationale:
      "Directly addresses Jamie's own growth challenge (near-zero retweets) as a lesson for other builders — meta but practical.",
    source: "GrowthOp internal",
    chars: 312,
    status: "generated",
  },
  {
    id: "b750b213dc2f41dfaa58fb8e9a415b6d",
    format: "photo_post",
    engagement: "MEDIUM",
    hook: "OpenAI published how they handle low-latency voice AI at scale...",
    content: `photo_brief: a selfie or casual photo of me with headphones on, maybe testing something on a laptop
---
OpenAI just published how they handle low-latency voice AI at scale.

the most interesting part isn't the engineering. it's that their own users are frustrated because the system responds too fast — it interrupts you when you pause to think.

optimizing for speed when the actual problem is turn-taking. classic case of solving the metric instead of the experience.

what's a feature you've seen where the technical achievement actively hurts the UX?`,
    rationale:
      "Turns the OpenAI voice latency story from HN into a product design observation that founders and operators can relate to.",
    source: "HN · today",
    chars: 445,
    status: "generated",
  },
  {
    id: "80d863a8c7ec4b98852471a535e06a8a",
    format: "how_to",
    engagement: "MEDIUM",
    hook: "3 questions before you let an agent run unattended...",
    content: `started a rule for myself: every AI feature I ship has to have a manual fallback path.

not because the AI is bad. because when it fails at 2am on a Saturday for one specific edge case, someone needs to keep working.

the boring reliability layer is the thing that actually makes AI features feel trustworthy to users.

do you build fallbacks from day one or add them after something breaks?`,
    rationale:
      "A specific, practical building-in-public lesson that demonstrates Jamie's engineering judgment.",
    source: "GrowthOp internal",
    chars: 329,
    status: "generated",
  },
  {
    id: "25d1f0f5d82640f09fa68906dfde86d1",
    format: "short_form",
    engagement: "HIGH",
    hook: "context windows are not memory...",
    content: `Figure AI producing 1 robot per hour.

Anthropic banning a 110-person company overnight without warning.

the infrastructure is scaling exponentially. the trust and governance layer is still held together with support tickets.

we keep talking about whether AI is capable enough. the harder question is whether the companies building it are dependable enough to build on.`,
    rationale:
      "Connects two trending stories into a single original observation about platform risk — a core concern for the founder/operator audience.",
    source: "personal",
    chars: 287,
    status: "generated",
  },
  {
    id: "34c0d24cfe2f4080953548e84b514c1c",
    format: "photo_post",
    engagement: "MEDIUM",
    hook: "malware was just found inside PyTorch Lightning — a library used by...",
    content: `photo_brief: a photo of me looking at my phone, maybe on a couch or at a desk
---
malware was just found inside PyTorch Lightning — a library used by thousands of AI teams.

the attack was in a dependency most people never even look at. Dune-themed naming and everything.

one thing I've started doing: before adding any new AI library, I check how many maintainers it actually has and when the last audit was. two minutes of checking saves a lot of pain.

how do you vet your AI dependencies?`,
    rationale:
      "The PyTorch Lightning malware story is trending on HN — this turns a security news item into a practical builder lesson.",
    source: "HN · today",
    chars: 398,
    status: "generated",
  },
];

export const WEEKLY_POSTS: WeeklyPost[] = [
  {
    day: "Mon",
    format: "photo_post",
    hook: "built an AI feature last week that worked perfectly in testing...",
    impressions: 4200,
    eng: 142,
    replies: 12,
    rate: 3.4,
  },
  {
    day: "Tue",
    format: "contrarian",
    hook: "Sam Altman funded a $60M UBI study, found it didn't improve health...",
    impressions: 12800,
    eng: 890,
    replies: 67,
    rate: 7.0,
  },
  {
    day: "Wed",
    format: "photo_post",
    hook: "95% of enterprise AI pilots deliver zero measurable financial impact...",
    impressions: 6100,
    eng: 233,
    replies: 18,
    rate: 3.8,
  },
  {
    day: "Thu",
    format: "how_to",
    hook: "how I cut Claude API costs 73% on a production agent...",
    impressions: 3300,
    eng: 78,
    replies: 4,
    rate: 2.4,
  },
  {
    day: "Thu",
    format: "short_form",
    hook: "the most valuable engineers in 2026 aren't the ones who can prompt...",
    impressions: 8900,
    eng: 412,
    replies: 33,
    rate: 4.6,
  },
  {
    day: "Fri",
    format: "photo_post",
    hook: "context windows are not memory...",
    impressions: 5400,
    eng: 198,
    replies: 15,
    rate: 3.7,
  },
  {
    day: "Sat",
    format: "contrarian",
    hook: "everyone says learn AI or get left behind. wrong frame...",
    impressions: 9200,
    eng: 521,
    replies: 44,
    rate: 5.7,
  },
  {
    day: "Sun",
    format: "how_to",
    hook: "3 questions before you let an agent run unattended...",
    impressions: 2800,
    eng: 67,
    replies: 3,
    rate: 2.4,
  },
];

export const STAT_CARDS: StatCardData[] = [
  { label: "impressions", value: "94.2k", delta: "+18%", positive: true },
  { label: "followers", value: "3,590", delta: "+470", positive: true },
  { label: "avg eng. rate", value: "3.4%", delta: "+0.7", positive: true },
  { label: "posts", value: "12 / wk", delta: "· 0", positive: false },
];

export const FOLLOWER_SERIES = [400, 520, 680, 890, 1200, 1580, 2100, 3590];
export const ENGAGEMENT_SERIES = [1.8, 2.1, 2.4, 2.9, 3.1, 2.8, 3.4, 3.4];

export const WEEKLY_INSIGHT = {
  summary:
    "contrarian_take posts outperformed photo_post by 2.1× on engagement this week. Hooks containing a specific dollar amount drove the top 3 posts. Two photo_posts that referenced internal anecdotes underperformed by 60%.",
  suggestions: [
    "shift format mix: 40% contrarian (was 30%)",
    'voice_brief: emphasize "specific numbers in hook"',
    "de-emphasize internal anecdotes w/o stakes",
  ],
};

export const DO_RULES = [
  "open with a specific number, claim, or contrarian frame",
  "name sources by ground truth (paper, repo, screenshot)",
  "end with a stance, not a question",
  "use lowercase to start sentences (visual signature)",
];

export const DONT_RULES = [
  '"in today\'s fast-paced world..."',
  'questions in the hook ("ever wondered why...?")',
  "emoji except 1 2 3 in lists",
  "internal anecdotes without verifiable stakes",
];

export const GOOD_EXAMPLES = [
  {
    format: "contrarian" as const,
    quote:
      '"95% of enterprise AI pilots deliver zero measurable financial impact. MIT NANDA report, 300 deployments studied..."',
  },
  {
    format: "how_to" as const,
    quote:
      '"Set spend alerts before you ship. Not after. Log every prompt-response pair from day one."',
  },
];

export const STRATEGY_BRIEF = `Post original analysis, operating lessons, and practical frameworks over summaries of what happened. At least half ideas should use photo_post format. Prioritize content that demonstrates AI engineering judgment — not just commentary on AI news.

Target audience: founders and operators building with AI who want to learn from someone who has shipped things in production. Not thought leaders. Not hype. Real decisions with real tradeoffs.

Weekly goal: 2+ photo_posts, 1 contrarian take grounded in data, 1 how_to from direct experience.`;

export const COMPILED_PROMPT = `You are Jamie Ogundiran, an AI engineer building products between London and Tokyo.

VOICE: Direct, technical, slightly contrarian. No hedging. No corporate softening. Writes like a senior eng who has shipped things, not a thought leader.

STRATEGY: Post original analysis and operating lessons. At least half ideas should use photo_post format. Target founders and operators building with AI.

DO:
- Open with a specific number, claim, or contrarian frame
- Name sources by ground truth (paper, repo, screenshot)
- End with a stance, not a question
- Use lowercase to start sentences

DON'T:
- "in today's fast-paced world..."
- Questions in the hook
- Emoji except in numbered lists
- Internal anecdotes without verifiable stakes`;

export const FORMATS = [
  {
    name: "photo_post",
    description: "Personal photo + observation or open question",
    limit: "280 chars post + photo_brief",
  },
  {
    name: "contrarian",
    description: "Takes a position against the consensus view",
    limit: "280 chars",
  },
  {
    name: "short_form",
    description: "Punchy multi-line take on a news story",
    limit: "280 chars",
  },
  {
    name: "how_to",
    description: "Numbered practical steps from direct experience",
    limit: "560 chars",
  },
];
