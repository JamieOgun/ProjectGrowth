"use client";

import { useState } from "react";
import { IdeaRow } from "./idea-row";
import { IdeaPanel } from "./idea-panel";
import type { Idea } from "@/lib/types";

interface IdeaListProps {
  ideas: Idea[];
}

export function IdeaList({ ideas }: IdeaListProps) {
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [statuses, setStatuses] = useState<Record<string, string>>({});

  const selected = ideas.find((i) => i.id === selectedId) ?? null;

  const handleApprove = (id: string) => {
    setStatuses((s) => ({ ...s, [id]: "approved" }));
    setSelectedId(null);
  };

  const handleReject = (id: string) => {
    setStatuses((s) => ({ ...s, [id]: "rejected" }));
    setSelectedId(null);
  };

  return (
    <>
      <div
        className="overflow-hidden rounded-lg border border-neutral-200 bg-white"
        style={{
          marginRight: selected ? 396 : 0,
          transition: "margin 150ms ease",
        }}
      >
        {ideas.map((idea) => {
          const status = statuses[idea.id];
          if (status === "rejected") return null;
          return (
            <IdeaRow
              key={idea.id}
              idea={{
                ...idea,
                status: (status as Idea["status"]) ?? idea.status,
              }}
              selected={selectedId === idea.id}
              onClick={() =>
                setSelectedId(selectedId === idea.id ? null : idea.id)
              }
            />
          );
        })}
      </div>

      {selected && (
        <IdeaPanel
          idea={selected}
          onClose={() => setSelectedId(null)}
          onApprove={handleApprove}
          onReject={handleReject}
        />
      )}
    </>
  );
}
