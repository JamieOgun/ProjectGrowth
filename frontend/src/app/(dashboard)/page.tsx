import { PageHeader } from "@/components/layout/page-header";
import { IdeaList } from "@/components/ideas/idea-list";
import { Button } from "@/components/ui/button";
import { GenerateMoreButton } from "@/components/ideas/generate-more-button";
import { getIdeas } from "@/lib/api";

export default async function HomePage() {
  const ideas = await getIdeas("generated");

  const latestDate = ideas[0]?.source ?? new Date().toISOString().slice(0, 10);
  const dateLabel = new Date(latestDate + "T12:00:00Z").toLocaleDateString(
    "en-GB",
    { weekday: "long", month: "long", day: "numeric" },
  );

  return (
    <>
      <PageHeader
        breadcrumb={`ideas · ${dateLabel.toLowerCase()}`}
        title={`${ideas.length} generated`}
        subtitle="sorted by priority ▼ · half must be photo_post"
        actions={
          <>
            <Button
              variant="outline"
              size="sm"
              className="border-neutral-300 font-mono text-xs"
            >
              growth-op ideas list
            </Button>
            <GenerateMoreButton />
          </>
        }
      />
      <IdeaList ideas={ideas} />
    </>
  );
}
