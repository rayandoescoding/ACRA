type SentimentTone = "coral" | "amber" | "teal";

function getTone(score: number): SentimentTone {
  if (score < -0.25) return "coral";
  if (score > 0.25) return "teal";
  return "amber";
}

const toneStyles: Record<SentimentTone, string> = {
  coral: "bg-coral",
  amber: "bg-amber",
  teal: "bg-teal",
};

export function SentimentBar({ score }: { score: number }) {
  const clampedScore = Math.max(-1, Math.min(1, score));
  const percentage = ((clampedScore + 1) / 2) * 100;
  const tone = getTone(clampedScore);
  const label = `${clampedScore > 0 ? "+" : ""}${clampedScore.toFixed(2)}`;

  return (
    <div className="flex items-center gap-2" aria-label={`Sentiment score ${label}`}>
      <div className="h-1.5 w-16 overflow-hidden rounded-full bg-hairline">
        <div className={`h-full rounded-full ${toneStyles[tone]}`} style={{ width: `${percentage}%` }} />
      </div>
      <span className="font-mono text-[11px] text-text-muted">{label}</span>
    </div>
  );
}
