const lanes = ["CRITICAL", "HIGH"] as const;

export function TicketQueueSkeleton() {
  return (
    <section aria-label="Loading ticket queue" role="status">
      <span className="sr-only">Loading ticket queue</span>
      <div aria-hidden="true" className="animate-pulse">
        <div className="mb-5 flex items-end justify-between">
          <div className="space-y-3">
            <div className="h-3 w-28 bg-panel-raised" />
            <div className="h-6 w-40 bg-panel-raised" />
          </div>
          <div className="h-4 w-16 bg-panel-raised" />
        </div>
        <div className="space-y-5">
          {lanes.map((lane) => (
            <div key={lane}>
              <div className="mb-2 h-5 w-24 bg-panel-raised" />
              <div className="space-y-2">
                {[0, 1].map((index) => (
                  <div key={index} className="border border-hairline bg-panel p-4">
                    <div className="h-4 w-3/5 bg-panel-raised" />
                    <div className="mt-4 flex items-center justify-between">
                      <div className="h-3 w-16 bg-panel-raised" />
                      <div className="h-2 w-20 bg-panel-raised" />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
