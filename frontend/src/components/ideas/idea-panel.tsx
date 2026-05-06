import { X } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import type { Idea } from "@/lib/types";

interface IdeaPanelProps {
  idea: Idea;
  onClose: () => void;
  onApprove: (id: string) => void;
  onReject: (id: string) => void;
}

export function IdeaPanel({
  idea,
  onClose,
  onApprove,
  onReject,
}: IdeaPanelProps) {
  const isHigh = idea.engagement === "HIGH";

  return (
    <div className="fixed top-0 right-0 z-50 flex h-screen w-[380px] flex-col overflow-hidden border-l border-neutral-200 bg-white shadow-xl">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-neutral-100 px-5 py-4">
        <div className="flex items-center gap-1.5">
          <span className="rounded border border-black/70 px-1.5 py-0.5 font-mono text-xs leading-none">
            {idea.format}
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
        <button
          onClick={onClose}
          className="text-neutral-400 transition-colors hover:text-black"
        >
          <X className="h-4 w-4" />
        </button>
      </div>

      {/* Content */}
      <div className="flex flex-1 flex-col gap-5 overflow-y-auto px-5 py-5">
        {/* Draft */}
        <div>
          <p className="mb-2 font-mono text-[10px] tracking-widest text-neutral-400 uppercase">
            Draft
          </p>
          <p className="text-sm leading-relaxed whitespace-pre-wrap text-neutral-800">
            {idea.content}
          </p>
        </div>

        <div className="border-t border-dashed border-neutral-200" />

        {/* Why this */}
        <div>
          <p className="mb-2 font-mono text-[10px] tracking-widest text-neutral-400 uppercase">
            Why This
          </p>
          <p className="text-sm leading-relaxed text-neutral-500 italic">
            {idea.rationale}
          </p>
        </div>

        <div className="border-t border-dashed border-neutral-200" />

        {/* Stats */}
        <div className="flex items-center gap-4 font-mono text-xs text-neutral-500">
          <span>
            <span className="font-sans text-lg font-bold text-black not-italic">
              {idea.chars}
            </span>{" "}
            chars
          </span>
          <span className="text-neutral-200">|</span>
          <span>
            <span className="font-medium text-black">
              {isHigh ? "HIGH" : "MED"}
            </span>{" "}
            voice fit
          </span>
          <span className="text-neutral-200">|</span>
          <span>
            <span className="font-medium text-black">2.4k</span> est. reach
          </span>
        </div>
      </div>

      {/* Actions */}
      <div className="flex gap-2 border-t border-neutral-100 px-5 py-4">
        <Button
          size="sm"
          className="flex-1 bg-black text-xs text-white hover:bg-neutral-800"
          onClick={() => onApprove(idea.id)}
        >
          approve
        </Button>
        <Button
          size="sm"
          variant="outline"
          className="flex-1 border-neutral-300 text-xs"
          onClick={() => {}}
        >
          edit draft
        </Button>
        <Button
          size="sm"
          variant="outline"
          className="flex-1 border-neutral-300 text-xs text-[#e85d4a] hover:border-[#e85d4a] hover:text-[#e85d4a]"
          onClick={() => onReject(idea.id)}
        >
          reject
        </Button>
      </div>
    </div>
  );
}
