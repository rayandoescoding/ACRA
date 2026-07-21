export function TicketDetailSkeleton() {
  return (
    <section aria-label="Loading ticket detail" role="status">
      <span className="sr-only">Loading ticket detail</span>
      <div aria-hidden="true" className="animate-pulse">
        <div className="flex items-center justify-between border-b border-hairline pb-5">
          <div className="space-y-3">
            <div className="h-3 w-56 bg-panel-raised" />
            <div className="h-8 w-72 max-w-full bg-panel-raised" />
          </div>
          <div className="h-8 w-24 bg-panel-raised" />
        </div>
        <div className="mt-6 grid gap-6 lg:grid-cols-[1fr_0.8fr]">
          {[0, 1].map((panel) => (
            <div key={panel} className="border border-hairline bg-panel p-5">
              <div className="h-3 w-32 bg-panel-raised" />
              <div className="mt-5 space-y-4">
                <div className="h-4 w-full bg-panel-raised" />
                <div className="h-4 w-5/6 bg-panel-raised" />
                <div className="h-24 border-t border-hairline pt-4">
                  <div className="h-3 w-24 bg-panel-raised" />
                  <div className="mt-3 h-3 w-40 bg-panel-raised" />
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
