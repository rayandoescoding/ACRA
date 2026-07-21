type GuardrailStampProps = {
  passed: boolean;
  visible: boolean;
};

export function GuardrailStamp({ passed, visible }: GuardrailStampProps) {
  const result = passed ? "CLEARED" : "INTERCEPTED";
  const tone = passed
    ? "border-teal bg-teal-dim text-teal"
    : "border-coral bg-coral-dim text-coral";

  return (
    <div
      className={`inline-flex max-w-64 flex-col border-2 px-3 py-2 shadow-[0_8px_20px_rgba(0,0,0,0.18)] ${tone} ${
        visible ? "guardrail-stamp-enter" : "guardrail-stamp-hidden"
      }`}
      aria-label={`Guardrail ${result.toLowerCase()}`}
    >
      <span className="font-mono text-xs font-semibold tracking-[0.12em]">
        GUARDRAIL: {result}
      </span>
      <span className="mt-1 font-sans text-[10px] leading-tight text-text-muted">
        policy validated independent of model confidence.
      </span>
    </div>
  );
}
