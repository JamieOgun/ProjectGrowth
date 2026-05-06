"use client";

import { useState } from "react";
import { cn } from "@/lib/utils";
import type { WeeklyPost } from "@/lib/types";

interface PostsTableProps {
  posts: WeeklyPost[];
}

const MAX_RATE = 10;

export function PostsTable({ posts }: PostsTableProps) {
  const [filter, setFilter] = useState<string>("all");
  const filtered =
    filter === "all" ? posts : posts.filter((post) => post.format === filter);
  const formatFilters = [
    { label: `all · ${posts.length}`, value: "all" },
    ...Array.from(new Set(posts.map((post) => post.format))).map((format) => ({
      label: `${format} · ${posts.filter((post) => post.format === format).length}`,
      value: format,
    })),
  ];

  return (
    <div className="overflow-hidden rounded-lg border border-neutral-200 bg-white">
      <div className="flex items-center justify-between border-b border-neutral-100 px-5 py-4">
        <p className="text-sm font-semibold">posts · last 7 days</p>
        <div className="flex items-center gap-1.5">
          {formatFilters.map(({ label, value }) => (
            <button
              key={value}
              onClick={() => setFilter(value)}
              className={cn(
                "rounded-full border px-2.5 py-1 font-mono text-xs transition-colors",
                filter === value
                  ? "border-black bg-black text-white"
                  : "border-neutral-200 text-neutral-500 hover:border-neutral-400",
              )}
            >
              {label}
            </button>
          ))}
        </div>
      </div>

      <table className="w-full">
        <thead>
          <tr className="border-b border-neutral-100">
            {[
              "DAY",
              "FORMAT",
              "HOOK",
              "IMPRESSIONS",
              "ENG.",
              "REPLIES",
              "RATE",
            ].map((heading) => (
              <th
                key={heading}
                className="px-4 py-2.5 text-left font-mono text-[10px] tracking-widest text-neutral-400 uppercase"
              >
                {heading}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {filtered.map((post, index) => (
            <tr
              key={`${post.day}-${post.hook}-${index}`}
              className="border-b border-neutral-50 transition-colors last:border-0 hover:bg-neutral-50"
            >
              <td className="px-4 py-3 font-mono text-xs text-neutral-500">
                {post.day}
              </td>
              <td className="px-4 py-3">
                <span className="rounded border border-black/70 px-1.5 py-0.5 font-mono text-xs">
                  {post.format}
                </span>
              </td>
              <td className="max-w-[200px] truncate px-4 py-3 text-sm text-neutral-700">
                {post.hook}
              </td>
              <td className="px-4 py-3 text-right font-mono text-sm">
                {post.impressions.toLocaleString()}
              </td>
              <td className="px-4 py-3 text-right font-mono text-sm">
                {post.eng}
              </td>
              <td className="px-4 py-3 text-right font-mono text-sm">
                {post.replies}
              </td>
              <td className="px-4 py-3">
                <div className="flex items-center gap-1.5">
                  <div className="h-1.5 w-16 overflow-hidden rounded-full bg-neutral-100">
                    <div
                      className="h-full rounded-full bg-[#e85d4a]"
                      style={{
                        width: `${Math.min((post.rate / MAX_RATE) * 100, 100)}%`,
                      }}
                    />
                  </div>
                  <span className="font-mono text-xs font-medium text-[#e85d4a]">
                    {post.rate}%
                  </span>
                </div>
              </td>
            </tr>
          ))}
          {filtered.length === 0 && (
            <tr>
              <td
                colSpan={7}
                className="px-4 py-8 text-center text-sm text-neutral-400"
              >
                no posts in this range
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
