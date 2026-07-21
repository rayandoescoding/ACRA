"use client";

import { useEffect, useState } from "react";

const stages = ["Classification", "Priority", "Planning", "Guardrail", "Resolution"] as const;

export function ProcessingProgress({ active }: { active: boolean }) {
  const [stageIndex, setStageIndex] = useState(0);

  useEffect(() => {
    if (!active) {
      setStageIndex(0);
      return;
    }

    setStageIndex(0);
    const timer = window.setInterval(() => {
      setStageIndex((current) => Math.min(current + 1, stages.length - 1));
    }, 650);

    return () => window.clearInterval(timer);
  }, [active]);

  if (!active) return null;

  const currentStage = stages[stageIndex];

  return (
    <section className="mt-5 border border-hairline bg-bg p-4" aria-label="Ticket processing progress">
      <p className="font-mono text-[10px] tracking-[0.12em] text-blue-signal" role="status" aria-live="polite" aria-atomic="true">
        PROCESSING / {currentStage.toUpperCase()}
      </p>
      <ol aria-hidden="true" className="mt-4 grid grid-cols-5 gap-1.5">
        {stages.map((stage, index) => {
          const complete = index < stageIndex;
          const current = index === stageIndex;
          const tone = complete || current ? "bg-blue-signal" : "bg-hairline";

          return (
            <li key={stage} className="min-w-0">
              <span className={`block h-1 ${tone} ${current ? "animate-pulse" : ""}`} />
              <span className={`mt-2 block truncate font-mono text-[8px] tracking-[0.08em] ${current ? "text-text" : "text-text-faint"}`}>
                {stage}
              </span>
            </li>
          );
        })}
      </ol>
    </section>
  );
}
