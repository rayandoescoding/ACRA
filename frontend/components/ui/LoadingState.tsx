export function LoadingState({ label = "LOADING" }: { label?: string }) {
  return (
    <div className="border border-hairline bg-panel p-6" role="status" aria-live="polite">
      <div className="flex items-center gap-3">
        <span className="h-3 w-3 animate-pulse rounded-full bg-blue-signal" />
        <p className="font-mono text-xs tracking-[0.14em] text-text-muted">{label}…</p>
      </div>
    </div>
  );
}
