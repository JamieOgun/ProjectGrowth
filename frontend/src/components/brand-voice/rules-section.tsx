import type { Format } from "@/lib/types";

interface RulesSectionProps {
  doRules: string[];
  dontRules: string[];
  examples: { format: Format; quote: string }[];
}

export function RulesSection({
  doRules,
  dontRules,
  examples,
}: RulesSectionProps) {
  return (
    <div className="flex flex-col gap-6">
      {/* Do */}
      <div>
        <p className="mb-3 text-sm font-bold">do</p>
        <div className="flex flex-col gap-1.5">
          {doRules.map((rule, i) => (
            <div key={i} className="flex items-start gap-2.5">
              <span className="mt-0.5 flex h-5 w-5 flex-shrink-0 items-center justify-center rounded border border-emerald-400 text-xs font-bold text-emerald-500">
                +
              </span>
              <span className="text-sm text-neutral-700">{rule}</span>
            </div>
          ))}
          <button className="mt-1 flex w-fit items-center gap-2 rounded border border-dashed border-neutral-300 px-3 py-1.5 text-xs text-neutral-400 transition-colors hover:border-neutral-400 hover:text-neutral-600">
            + add rule
          </button>
        </div>
      </div>

      <div className="border-t border-neutral-100" />

      {/* Don't */}
      <div>
        <p className="mb-3 text-sm font-bold">don&apos;t</p>
        <div className="flex flex-col gap-1.5">
          {dontRules.map((rule, i) => (
            <div key={i} className="flex items-start gap-2.5">
              <span className="mt-0.5 flex h-5 w-5 flex-shrink-0 items-center justify-center rounded border border-red-300 text-xs font-bold text-red-400">
                −
              </span>
              <span className="text-sm text-neutral-700">{rule}</span>
            </div>
          ))}
          <button className="mt-1 flex w-fit items-center gap-2 rounded border border-dashed border-neutral-300 px-3 py-1.5 text-xs text-neutral-400 transition-colors hover:border-neutral-400 hover:text-neutral-600">
            + add rule
          </button>
        </div>
      </div>

      <div className="border-t border-neutral-100" />

      {/* Examples */}
      <div>
        <p className="mb-3 text-sm font-bold">examples · good</p>
        <div className="flex flex-col gap-3">
          {examples.map((ex, i) => (
            <div key={i} className="flex flex-col gap-1.5">
              <span className="w-fit rounded border border-black/70 px-1.5 py-0.5 font-mono text-xs">
                {ex.format}
              </span>
              <p className="text-sm text-neutral-500 italic">{ex.quote}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
