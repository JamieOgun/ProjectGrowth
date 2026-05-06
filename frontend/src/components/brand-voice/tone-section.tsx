import { Textarea } from "@/components/ui/textarea";

interface ToneSectionProps {
  value: string;
  onChange: (v: string) => void;
}

export function ToneSection({ value, onChange }: ToneSectionProps) {
  return (
    <div>
      <p className="mb-3 text-sm font-bold">tone</p>
      <Textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="min-h-[80px] resize-none border-neutral-200 font-mono text-sm focus:ring-0"
        rows={3}
      />
    </div>
  );
}
