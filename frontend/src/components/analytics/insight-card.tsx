import { Button } from "@/components/ui/button";

interface InsightCardProps {
  insight: { summary: string; suggestions: string[] };
}

export function InsightCard({ insight }: InsightCardProps) {
  return (
    <div className="flex flex-col gap-4 rounded-lg border border-amber-200 bg-amber-50 px-5 py-4">
      <div className="flex items-start justify-between gap-4">
        <p className="text-sm font-bold">weekly insight</p>
        <span className="flex-shrink-0 rounded border border-neutral-200 bg-white px-2 py-0.5 font-mono text-xs text-neutral-500">
          auto · mon 09:00
        </span>
      </div>

      <p className="text-sm leading-relaxed text-neutral-700">
        {insight.summary}
      </p>

      <div>
        <p className="mb-2 font-mono text-[10px] tracking-widest text-neutral-400 uppercase">
          Suggested Updates
        </p>
        <ul className="flex flex-col gap-1">
          {insight.suggestions.map((s, i) => (
            <li key={i} className="flex gap-2 text-sm text-neutral-700">
              <span className="flex-shrink-0 text-neutral-400">•</span>
              {s}
            </li>
          ))}
        </ul>
      </div>

      <div className="border-t border-amber-200" />

      <div className="flex items-center gap-2">
        <Button
          size="sm"
          className="bg-black text-xs text-white hover:bg-neutral-800"
        >
          apply to brand voice →
        </Button>
        <Button
          size="sm"
          variant="outline"
          className="border-neutral-300 text-xs"
        >
          review diff
        </Button>
        <Button
          size="sm"
          variant="outline"
          className="border-neutral-300 text-xs text-neutral-500"
        >
          dismiss
        </Button>
      </div>
    </div>
  );
}
