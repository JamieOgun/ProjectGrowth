"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";

const NAV = [
  { href: "/", label: "Home" },
  { href: "/analytics", label: "Analytics" },
  { href: "/brand-voice", label: "Brand Voice" },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="fixed top-0 left-0 z-40 flex h-screen w-[180px] flex-col border-r border-neutral-200 bg-[#f8f7f4]">
      {/* Logo */}
      <div className="border-b border-neutral-200 px-5 py-5">
        <div className="flex items-center gap-2">
          <div className="flex h-6 w-6 items-center justify-center rounded-full bg-[#e85d4a]">
            <span className="text-xs font-bold text-white">G</span>
          </div>
          <span className="text-sm font-bold tracking-tight">GrowthOp</span>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex flex-1 flex-col gap-0.5 px-3 py-4">
        {NAV.map(({ href, label }) => {
          const active =
            href === "/" ? pathname === "/" : pathname.startsWith(href);
          return (
            <Link
              key={href}
              href={href}
              className={cn(
                "flex items-center gap-2.5 rounded px-2 py-1.5 text-sm transition-colors",
                active
                  ? "border border-neutral-200 bg-white font-medium text-black shadow-sm"
                  : "text-neutral-500 hover:text-black",
              )}
            >
              <span
                className={cn(
                  "h-2 w-2 flex-shrink-0 rounded-full border",
                  active
                    ? "border-[#e85d4a] bg-[#e85d4a]"
                    : "border-neutral-400",
                )}
              />
              {label}
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="border-t border-neutral-200 px-5 py-4">
        <p className="font-mono text-xs text-neutral-400">@JamieOgundiran</p>
        <p className="mt-0.5 font-mono text-xs text-neutral-400">
          dry_run · on
        </p>
      </div>
    </aside>
  );
}
