import { PageHeader } from "@/components/layout/page-header";
import { StatCard } from "@/components/analytics/stat-card";
import { Sparkline } from "@/components/analytics/sparkline";
import { InsightCard } from "@/components/analytics/insight-card";
import { PostsTable } from "@/components/analytics/posts-table";
import { getAnalyticsOverview } from "@/lib/api";

export default async function AnalyticsPage() {
  const data = await getAnalyticsOverview(7);

  return (
    <>
      <PageHeader
        breadcrumb="analytics · last 7 days · @jamieogundiran"
        title="things people did"
        actions={
          <div className="flex items-center gap-2">
            <select className="rounded border border-neutral-200 bg-white px-2 py-1 font-mono text-xs text-neutral-600">
              <option>7d</option>
              <option>14d</option>
              <option>30d</option>
            </select>
            <button className="rounded border border-neutral-200 bg-white px-2.5 py-1 font-mono text-xs text-neutral-600 transition-colors hover:border-neutral-400">
              export csv
            </button>
          </div>
        }
      />

      {/* Stat cards */}
      <div className="mb-6 flex gap-4">
        {data.stat_cards.map((card) => (
          <StatCard key={card.label} {...card} />
        ))}
      </div>

      {/* Charts + Insight */}
      <div className="mb-6 grid grid-cols-3 gap-4">
        <Sparkline
          data={data.follower_series}
          title="followers · 8 weeks"
          subtitle={`${data.follower_series.length} points`}
          height={100}
        />
        <Sparkline
          data={data.engagement_series}
          title="avg engagement rate"
          subtitle={`${data.range.days}d`}
          height={100}
        />
        {data.weekly_insight ? (
          <InsightCard insight={data.weekly_insight} />
        ) : (
          <div className="flex items-center justify-center rounded-lg border border-neutral-200 bg-white px-5 py-4 text-sm text-neutral-400">
            no weekly insight yet
          </div>
        )}
      </div>

      {/* Posts table */}
      <PostsTable posts={data.posts} />
    </>
  );
}
