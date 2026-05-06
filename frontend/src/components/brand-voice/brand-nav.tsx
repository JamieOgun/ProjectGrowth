import { cn } from "@/lib/utils";
import type { BrandNavSection } from "@/lib/types";

const SECTIONS: { key: BrandNavSection; label: string }[] = [
  { key: "voice_brief", label: "voice_brief" },
  { key: "strategy_brief", label: "strategy_brief" },
  { key: "formats", label: "formats" },
  { key: "revisions", label: "revisions" },
  { key: "compiled_prompt", label: "compiled_prompt" },
];

interface BrandNavProps {
  active: BrandNavSection;
  onChange: (s: BrandNavSection) => void;
}

export function BrandNav({ active, onChange }: BrandNavProps) {
  return (
    <div className="flex w-[220px] flex-shrink-0 flex-col overflow-hidden rounded-lg border border-neutral-200 bg-white">
      <div className="flex-1 py-2">
        {SECTIONS.map(({ key, label }) => (
          <button
            key={key}
            onClick={() => onChange(key)}
            className={cn(
              "flex w-full items-center justify-between px-4 py-2.5 text-left font-mono text-sm transition-colors",
              active === key
                ? "bg-neutral-50 font-medium text-black"
                : "text-neutral-500 hover:bg-neutral-50 hover:text-black",
            )}
          >
            <span>{label}</span>
            <span className="text-xs text-neutral-300">›</span>
          </button>
        ))}
      </div>

      <div className="mx-3 my-2 border-t border-dashed border-neutral-200" />

      <div className="px-4 py-3">
        <p className="mb-2 font-mono text-[10px] tracking-widest text-neutral-400 uppercase">
          Cache
        </p>
        <p className="font-mono text-xs text-neutral-500">
          cache_control: ephemeral
        </p>
        <p className="mt-0.5 font-mono text-xs text-neutral-500">
          dry_run: true
        </p>
      </div>
    </div>
  );
}
