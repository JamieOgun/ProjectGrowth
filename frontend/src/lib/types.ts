export type Engagement = "HIGH" | "MEDIUM" | "LOW";
export type Format = "photo_post" | "contrarian" | "short_form" | "how_to";
export type IdeaStatus = "generated" | "approved" | "rejected";
export type BrandNavSection =
  | "voice_brief"
  | "strategy_brief"
  | "formats"
  | "revisions"
  | "compiled_prompt";

export type Idea = {
  id: string;
  format: Format;
  engagement: Engagement;
  hook: string;
  content: string;
  rationale: string;
  source: string;
  chars: number;
  status: IdeaStatus;
};

export type WeeklyPost = {
  day: string;
  format: string;
  hook: string;
  impressions: number;
  eng: number;
  replies: number;
  rate: number;
};

export type StatCardData = {
  label: string;
  value: string;
  delta: string;
  positive: boolean;
};

export type WeeklyInsight = {
  summary: string;
  suggestions: string[];
};

export type ContentFormat = {
  name: string;
  purpose: string;
  max_chars: number | null;
  template: string;
  example: string | null;
};

export type BrandConfig = {
  id: string;
  name: string;
  handle: string;
  audience: string;
  voice_brief: string;
  strategy_brief: string;
  content_territories: string[];
  post_max_chars: number;
  formats: ContentFormat[];
  updated_at: string;
};

export type AnalyticsOverview = {
  range: {
    days: number;
    start_date: string;
    end_date: string;
  };
  stat_cards: StatCardData[];
  follower_series: number[];
  engagement_series: number[];
  weekly_insight: WeeklyInsight | null;
  posts: WeeklyPost[];
};
