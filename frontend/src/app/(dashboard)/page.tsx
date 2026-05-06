import { PageHeader } from "@/components/layout/page-header";
import { IdeaList } from "@/components/ideas/idea-list";
import { Button } from "@/components/ui/button";
import { IDEAS } from "@/lib/mock-data";

export default function HomePage() {
  return (
    <>
      <PageHeader
        breadcrumb="ideas · tuesday, may 5"
        title={`${IDEAS.length} generated today`}
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
            <Button
              size="sm"
              className="bg-black text-xs text-white hover:bg-neutral-800"
            >
              + generate more
            </Button>
          </>
        }
      />
      <IdeaList ideas={IDEAS} />
    </>
  );
}
