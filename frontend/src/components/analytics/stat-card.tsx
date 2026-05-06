import { cn } from "@/lib/utils";
import type { StatCardData } from "@/lib/types";

export function StatCard({ label, value, delta, positive }: StatCardData) {
  return (
    <div className="flex-1 rounded-lg border border-neutral-200 bg-white px-5 py-4">
      <p className="mb-2 font-mono text-xs tracking-widest text-neutral-400 uppercase">
        {label}
      </p>
      <p className="text-2xl font-bold tracking-tight">{value}</p>
      <p
        className={cn(
          "mt-1 font-mono text-xs",
          positive ? "text-emerald-600" : "text-neutral-400",
        )}
      >
        {positive && "▲ "}
        {delta}
      </p>
    </div>
  );
}
