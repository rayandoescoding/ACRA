import { LogoutButton } from "@/components/auth/LogoutButton";

type Metric = {
  label: string;
  value: string;
};

const defaultMetrics: Metric[] = [
  { label: "THROUGHPUT", value: "42/hr" },
  { label: "P95 LATENCY", value: "1.8s" },
  { label: "ESCALATION", value: "12.4%" },
  { label: "AUTO-RESOLVED", value: "76.8%" },
];

export function TopBar({ metrics = defaultMetrics }: { metrics?: Metric[] }) {
  return (
    <header className="fixed inset-x-0 top-0 z-20 border-b border-hairline bg-bg">
      <div className="mx-auto flex h-16 max-w-[1600px] items-center gap-6 px-5">
        <div className="flex items-center gap-3">
          <span className="grid h-8 w-8 place-items-center border border-teal bg-teal-dim font-mono text-xs font-bold text-teal">
            A
          </span>
          <div>
            <p className="font-mono text-sm font-semibold tracking-[0.2em] text-text">ACRA</p>
            <p className="font-mono text-[9px] tracking-[0.12em] text-text-faint">AGENT CONTROL ROOM</p>
          </div>
        </div>

        <span className="inline-flex items-center gap-2 rounded-full border border-teal bg-teal-dim px-2.5 py-1 font-mono text-[10px] font-medium tracking-[0.12em] text-teal">
          <span className="h-1.5 w-1.5 rounded-full bg-teal" /> LIVE
        </span>

        <dl className="ml-auto hidden items-center divide-x divide-hairline md:flex">
          {metrics.map((metric) => (
            <div key={metric.label} className="px-4 first:pl-0 last:pr-0">
              <dt className="font-mono text-[9px] tracking-[0.1em] text-text-faint">{metric.label}</dt>
              <dd className="mt-0.5 font-mono text-xs text-text">{metric.value}</dd>
            </div>
          ))}
        </dl>
        <LogoutButton />
      </div>
    </header>
  );
}
