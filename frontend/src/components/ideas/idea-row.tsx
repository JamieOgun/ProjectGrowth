import { ChevronRight } from "lucide-react";
import { cn } from "@/lib/utils";
import type { Idea } from "@/lib/types";

interface IdeaRowProps {
  idea: Idea;
  selected: boolean;
  onClick: () => void;
}

const FORMAT_LABELS: Record<string, string> = {
  photo_post: "photo_post",
  contrarian: "contrarian",
  short_form: "short_form",
  how_to: "how_to",
};

export function IdeaRow({ idea, selected, onClick }: IdeaRowProps) {
  const isHigh = idea.engagement === "HIGH";

  return (
    <button
      onClick={onClick}
      className={cn(
        "group flex w-full items-center gap-3 border-b border-neutral-100 px-4 py-3.5 text-left transition-colors",
        selected ? "bg-[#fdf0ee]" : "hover:bg-white",
      )}
    >
      {/* Accent bar */}
      <div
        className={cn(
          "w-0.5 flex-shrink-0 self-stretch rounded-full",
          isHigh ? "bg-[#e85d4a]" : "bg-neutral-300",
        )}
      />

      {/* Badges */}
      <div className="flex flex-shrink-0 items-center gap-1.5">
        <span className="rounded border border-black/70 px-1.5 py-0.5 font-mono text-xs leading-none">
          {FORMAT_LABELS[idea.format]}
        </span>
        <span
          className={cn(
            "rounded px-1.5 py-0.5 text-xs leading-none font-medium",
            isHigh
              ? "bg-[#e85d4a] text-white"
              : "bg-neutral-200 text-neutral-600",
          )}
        >
          {idea.engagement}
        </span>
      </div>

      {/* Hook */}
      <span className="flex-1 truncate text-sm text-neutral-800">
        {idea.hook}
      </span>

      {/* Source */}
      <span className="hidden flex-shrink-0 text-xs text-neutral-400 sm:block">
        {idea.source}
      </span>

      <ChevronRight className="h-3.5 w-3.5 flex-shrink-0 text-neutral-300 transition-colors group-hover:text-neutral-500" />
    </button>
  );
}
