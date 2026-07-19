import { AuthGuard } from "@/components/auth/AuthGuard";
import { GuardrailStamp } from "@/components/GuardrailStamp";
import { TicketQueue } from "@/components/dashboard/TicketQueue";
import { PageLayout } from "@/components/layout/PageLayout";
import { LaneBadge } from "@/components/ui/LaneBadge";

const trace = [
  ["01", "CLASSIFICATION", "Refund intent detected; frustrated sentiment."],
  ["02", "CONTEXT RETRIEVAL", "Enterprise plan, delivered order, $1,250.00 charge."],
  ["03", "PRIORITY", "Critical lane selected from value and sentiment signals."],
  ["04", "PLANNING", "Propose human review before financial action."],
] as const;

export default function DashboardPage() {
  return (
    <AuthGuard>
      <PageLayout activeRoute="dashboard">
      <div className="grid gap-6 xl:grid-cols-[minmax(0,0.95fr)_minmax(380px,1.05fr)]">
        <TicketQueue />

        <section className="border border-hairline bg-panel p-5" aria-labelledby="trace-heading">
          <div className="flex items-start justify-between gap-4 border-b border-hairline pb-4">
            <div>
              <p className="font-mono text-[10px] tracking-[0.14em] text-text-faint">SELECTED TICKET / DEMO-001</p>
              <h2 id="trace-heading" className="mt-1 text-lg font-semibold text-text">Reasoning trace</h2>
            </div>
            <LaneBadge lane="critical" />
          </div>

          <ol className="mt-5 space-y-5 border-l border-hairline pl-5">
            {trace.map(([step, title, detail]) => (
              <li key={step} className="relative">
                <span className="absolute -left-[1.78rem] top-0 grid h-4 w-4 place-items-center rounded-full border border-blue-signal bg-panel font-mono text-[8px] text-blue-signal" />
                <p className="font-mono text-[10px] tracking-[0.12em] text-blue-signal">{step} / {title}</p>
                <p className="mt-1 text-sm leading-6 text-text-muted">{detail}</p>
              </li>
            ))}
            <li className="relative">
              <span className="absolute -left-[1.78rem] top-0 grid h-4 w-4 place-items-center rounded-full border border-teal bg-panel font-mono text-[8px] text-teal" />
              <p className="font-mono text-[10px] tracking-[0.12em] text-teal">05 / GUARDRAIL</p>
              <div className="mt-3"><GuardrailStamp passed visible /></div>
            </li>
          </ol>

          <div className="mt-6 border-t border-hairline pt-4">
            <p className="font-mono text-[10px] tracking-[0.12em] text-text-faint">INTERCEPTION EXAMPLE</p>
            <div className="mt-3"><GuardrailStamp passed={false} visible /></div>
          </div>
        </section>
      </div>
      </PageLayout>
    </AuthGuard>
  );
}
