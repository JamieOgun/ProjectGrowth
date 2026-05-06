"use client";

import { useState } from "react";
import { PageHeader } from "@/components/layout/page-header";
import { BrandNav } from "@/components/brand-voice/brand-nav";
import { ToneSection } from "@/components/brand-voice/tone-section";
import { RulesSection } from "@/components/brand-voice/rules-section";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import {
  DO_RULES,
  DONT_RULES,
  GOOD_EXAMPLES,
  STRATEGY_BRIEF,
  COMPILED_PROMPT,
  FORMATS,
} from "@/lib/mock-data";
import type { BrandNavSection } from "@/lib/types";

const TONE_DEFAULT =
  "Direct, technical, slightly contrarian. No hedging. No corporate softening. Writes like a senior eng who has shipped things, not a thought leader.";

export default function BrandVoicePage() {
  const [activeSection, setActiveSection] =
    useState<BrandNavSection>("voice_brief");
  const [tone, setTone] = useState(TONE_DEFAULT);

  return (
    <>
      <PageHeader
        breadcrumb="brand voice · brand_voice.yaml · last updated 2d ago"
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

      <div className="flex items-start gap-5">
        <BrandNav active={activeSection} onChange={setActiveSection} />

        <div className="min-h-[500px] flex-1 rounded-lg border border-neutral-200 bg-white px-6 py-5">
          {activeSection === "voice_brief" && (
            <div className="flex flex-col gap-6">
              <ToneSection value={tone} onChange={setTone} />
              <div className="border-t border-neutral-100" />
              <RulesSection
                doRules={DO_RULES}
                dontRules={DONT_RULES}
                examples={GOOD_EXAMPLES}
              />
            </div>
          )}

          {activeSection === "strategy_brief" && (
            <div>
              <p className="mb-3 text-sm font-bold">strategy_brief</p>
              <Textarea
                defaultValue={STRATEGY_BRIEF}
                className="min-h-[200px] resize-none border-neutral-200 font-mono text-sm"
                rows={8}
              />
            </div>
          )}

          {activeSection === "formats" && (
            <div>
              <p className="mb-4 text-sm font-bold">formats</p>
              <div className="flex flex-col gap-3">
                {FORMATS.map((f) => (
                  <div
                    key={f.name}
                    className="rounded-lg border border-neutral-100 px-4 py-3"
                  >
                    <div className="mb-1 flex items-center justify-between">
                      <span className="rounded border border-black/70 px-1.5 py-0.5 font-mono text-xs">
                        {f.name}
                      </span>
                      <span className="font-mono text-xs text-neutral-400">
                        {f.limit}
                      </span>
                    </div>
                    <p className="text-sm text-neutral-600">{f.description}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeSection === "revisions" && (
            <div>
              <p className="mb-4 text-sm font-bold">revisions</p>
              <div className="flex flex-col gap-2">
                {[
                  {
                    date: "2026-05-05",
                    change: "voice_brief updated via voice-update CLI",
                  },
                  {
                    date: "2026-05-03",
                    change:
                      "strategy_brief updated — added photo_post frequency rule",
                  },
                  {
                    date: "2026-04-28",
                    change: "formats: added contrarian format",
                  },
                  {
                    date: "2026-04-20",
                    change: "initial brand_voice.yaml created",
                  },
                ].map((rev, i) => (
                  <div
                    key={i}
                    className="flex items-start gap-3 border-b border-neutral-50 py-2.5 last:border-0"
                  >
                    <span className="mt-0.5 flex-shrink-0 font-mono text-xs text-neutral-400">
                      {rev.date}
                    </span>
                    <span className="text-sm text-neutral-600">
                      {rev.change}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeSection === "compiled_prompt" && (
            <div>
              <p className="mb-3 text-sm font-bold">compiled_prompt</p>
              <p className="mb-3 font-mono text-xs text-neutral-400">
                readonly · this is what gets sent to Claude as the system prompt
              </p>
              <Textarea
                value={COMPILED_PROMPT}
                readOnly
                className="min-h-[300px] resize-none border-neutral-200 bg-neutral-50 font-mono text-xs"
                rows={14}
              />
            </div>
          )}
        </div>
      </div>
    </>
  );
}
