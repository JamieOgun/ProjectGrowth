import type { AnalyticsOverview } from "@/lib/types";

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
