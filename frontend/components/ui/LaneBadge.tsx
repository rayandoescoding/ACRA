type Lane = "critical" | "high" | "standard";

const laneStyles: Record<Lane, { label: string; className: string }> = {
  critical: {
    label: "CRITICAL",
    className: "border-coral bg-coral-dim text-coral",
  },
  high: {
    label: "HIGH",
    className: "border-amber bg-amber-dim text-amber",
  },
  standard: {
    label: "STANDARD",
    className: "border-blue-signal bg-panel-raised text-blue-signal",
  },
};

export function LaneBadge({ lane }: { lane: Lane }) {
  const style = laneStyles[lane];

  return (
    <span
      className={`inline-flex rounded border px-2 py-0.5 font-mono text-[10px] font-medium tracking-[0.14em] ${style.className}`}
    >
      {style.label}
    </span>
  );
}
