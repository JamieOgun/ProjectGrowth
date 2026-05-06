interface SparklineProps {
  data: number[];
  title: string;
  subtitle?: string;
  height?: number;
}

export function Sparkline({
  data,
  title,
  subtitle,
  height = 80,
}: SparklineProps) {
  if (data.length === 0) {
    return (
      <div className="flex-1 rounded-lg border border-neutral-200 bg-white px-5 py-4">
        <div className="mb-3 flex items-center justify-between">
          <p className="text-sm font-semibold">{title}</p>
          {subtitle && (
            <p className="font-mono text-xs text-neutral-400">{subtitle}</p>
          )}
        </div>
        <div
          className="flex items-center justify-center font-mono text-xs text-neutral-400"
          style={{ height }}
        >
          no data
        </div>
      </div>
    );
  }

  const min = Math.min(...data);
  const max = Math.max(...data);
  const range = max - min || 1;
  const w = 400;
  const h = height;
  const pad = 2;

  const points = data.map((v, i) => {
    const x = pad + (i / (data.length - 1)) * (w - pad * 2);
    const y = h - pad - ((v - min) / range) * (h - pad * 2);
    return [x, y] as [number, number];
  });

  const pathD =
    points.map(([x, y], i) => `${i === 0 ? "M" : "L"}${x},${y}`).join(" ") +
    ` L${points[points.length - 1][0]},${h} L${points[0][0]},${h} Z`;

  return (
    <div className="flex-1 rounded-lg border border-neutral-200 bg-white px-5 py-4">
      <div className="mb-3 flex items-center justify-between">
        <p className="text-sm font-semibold">{title}</p>
        {subtitle && (
          <p className="font-mono text-xs text-neutral-400">{subtitle}</p>
        )}
      </div>
      <svg
        viewBox={`0 0 ${w} ${h}`}
        className="w-full"
        style={{ height }}
        preserveAspectRatio="none"
      >
        <path d={pathD} fill="black" fillOpacity={0.9} />
      </svg>
    </div>
  );
}
