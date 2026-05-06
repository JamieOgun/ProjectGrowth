import { PageHeader } from "@/components/layout/page-header";
import { BrandVoiceClient } from "@/components/brand-voice/brand-voice-client";
import { Button } from "@/components/ui/button";
import { getBrandConfig } from "@/lib/api";

export default async function BrandVoicePage() {
  const brand = await getBrandConfig();

  const updatedLabel = new Date(brand.updated_at).toLocaleDateString("en-GB", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });

  return (
    <>
      <PageHeader
        breadcrumb={`brand voice · supabase · updated ${updatedLabel}`}
        title="how Jamie talks"
        actions={
          <>
            <Button
              variant="outline"
              size="sm"
              className="border-neutral-300 font-mono text-xs"
            >
              view raw yaml
            </Button>
            <Button
              size="sm"
              className="bg-black text-xs text-white hover:bg-neutral-800"
            >
              save
            </Button>
          </>
        }
      />
      <BrandVoiceClient brand={brand} />
    </>
  );
}
