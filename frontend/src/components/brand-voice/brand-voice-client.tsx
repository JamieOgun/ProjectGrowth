"use client";

import { useState } from "react";
import { BrandNav } from "@/components/brand-voice/brand-nav";
import { ToneSection } from "@/components/brand-voice/tone-section";
import { Textarea } from "@/components/ui/textarea";
import type { BrandConfig, BrandNavSection } from "@/lib/types";

interface BrandVoiceClientProps {
  brand: BrandConfig;
}

export function BrandVoiceClient({ brand }: BrandVoiceClientProps) {
  const [activeSection, setActiveSection] =
    useState<BrandNavSection>("voice_brief");
  const [voiceBrief, setVoiceBrief] = useState(brand.voice_brief);
  const [strategyBrief, setStrategyBrief] = useState(brand.strategy_brief);

  const compiledPrompt = `You are ${brand.name} (${brand.handle}).

VOICE:
${brand.voice_brief.trim()}

STRATEGY:
${brand.strategy_brief.trim()}

Target audience: ${brand.audience}`;

  return (
    <div className="flex items-start gap-5">
      <BrandNav active={activeSection} onChange={setActiveSection} />

      <div className="min-h-[500px] flex-1 rounded-lg border border-neutral-200 bg-white px-6 py-5">
        {activeSection === "voice_brief" && (
          <ToneSection value={voiceBrief} onChange={setVoiceBrief} />
        )}

        {activeSection === "strategy_brief" && (
          <div>
            <p className="mb-3 text-sm font-bold">strategy_brief</p>
            <Textarea
              value={strategyBrief}
              onChange={(e) => setStrategyBrief(e.target.value)}
              className="min-h-[200px] resize-none border-neutral-200 font-mono text-sm"
              rows={8}
            />
          </div>
        )}

        {activeSection === "formats" && (
          <div>
            <p className="mb-4 text-sm font-bold">formats</p>
            <div className="flex flex-col gap-3">
              {brand.formats.map((f) => (
                <div
                  key={f.name}
                  className="rounded-lg border border-neutral-100 px-4 py-3"
                >
                  <div className="mb-1 flex items-center justify-between">
                    <span className="rounded border border-black/70 px-1.5 py-0.5 font-mono text-xs">
                      {f.name}
                    </span>
                    {f.max_chars && (
                      <span className="font-mono text-xs text-neutral-400">
                        {f.max_chars} chars
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-neutral-600">{f.purpose}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeSection === "revisions" && (
          <div>
            <p className="mb-4 text-sm font-bold">revisions</p>
            <p className="text-sm text-neutral-400">
              last updated · {new Date(brand.updated_at).toLocaleDateString()}
            </p>
          </div>
        )}

        {activeSection === "compiled_prompt" && (
          <div>
            <p className="mb-3 text-sm font-bold">compiled_prompt</p>
            <p className="mb-3 font-mono text-xs text-neutral-400">
              readonly · this is what gets sent to Claude as the system prompt
            </p>
            <Textarea
              value={compiledPrompt}
              readOnly
              className="min-h-[300px] resize-none border-neutral-200 bg-neutral-50 font-mono text-xs"
              rows={14}
            />
          </div>
        )}
      </div>
    </div>
  );
}
