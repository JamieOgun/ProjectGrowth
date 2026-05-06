import type {
  AnalyticsOverview,
  BrandConfig,
  Engagement,
  Format,
  Idea,
} from "@/lib/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function getAnalyticsOverview(
  days = 7,
): Promise<AnalyticsOverview> {
  const response = await fetch(
    `${API_URL}/api/analytics/overview?days=${days}`,
    { cache: "no-store" },
  );

  if (!response.ok) {
    throw new Error("Failed to fetch analytics overview");
  }

  return response.json();
}

type BackendIdea = {
  id: string;
  generation_date: string;
  content: string;
  rationale: string;
  format: string;
  estimated_engagement: string;
  status: string;
  created_at: string;
  updated_at: string;
};

function mapIdea(raw: BackendIdea): Idea {
  const postText = raw.content.includes("---\n")
    ? (raw.content.split("---\n")[1] ?? raw.content)
    : raw.content;
  const hook = postText.split("\n")[0].trim();
  const engagement = raw.estimated_engagement.toUpperCase() as Engagement;

  return {
    id: raw.id,
    format: raw.format as Format,
    engagement: ["HIGH", "MEDIUM", "LOW"].includes(engagement)
      ? engagement
      : "MEDIUM",
    hook,
    content: raw.content,
    rationale: raw.rationale,
    source: raw.generation_date,
    chars: postText.trim().length,
    status: raw.status as Idea["status"],
  };
}

export async function getBrandConfig(): Promise<BrandConfig> {
  const response = await fetch(`${API_URL}/api/brand`, { cache: "no-store" });
  if (!response.ok) throw new Error("Failed to fetch brand config");
  return response.json();
}

export async function getIdeas(
  status?: "generated" | "rejected",
  limit = 50,
): Promise<Idea[]> {
  const params = new URLSearchParams({ limit: String(limit) });
  if (status) params.set("status", status);

  const response = await fetch(`${API_URL}/api/ideas?${params}`, {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error("Failed to fetch ideas");
  }

  const raw: BackendIdea[] = await response.json();
  return raw.map(mapIdea);
}
