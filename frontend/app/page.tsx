import Link from "next/link";

import { GuardrailStamp } from "@/components/GuardrailStamp";
import { PageLayout } from "@/components/layout/PageLayout";
import { LaneBadge } from "@/components/ui/LaneBadge";
import { SentimentBar } from "@/components/ui/SentimentBar";

const lanes = [
  {
    lane: "critical" as const,
    tickets: [
      { id: "demo-001", subject: "Urgent refund request for enterprise subscription", customer: "Bruno Singh", sentiment: -0.88 },
    ],
  },
  {
    lane: "high" as const,
    tickets: [
      { id: "demo-002", subject: "Delivery is late", customer: "Chloe Martin", sentiment: -0.42 },
    ],
  },
  {
    lane: "standard" as const,
    tickets: [
      { id: "demo-003", subject: "Excellent service feedback", customer: "Elena Brooks", sentiment: 0.76 },
    ],
  },
];

const trace = [
  ["01", "CLASSIFICATION", "Refund intent detected; frustrated sentiment."],
  ["02", "CONTEXT RETRIEVAL", "Enterprise plan, delivered order, $1,250.00 charge."],
  ["03", "PRIORITY", "Critical lane selected from value and sentiment signals."],
  ["04", "PLANNING", "Propose human review before financial action."],
] as const;

export default function DashboardPage() {
  return (
    <PageLayout activeRoute="dashboard">
      <div className="grid gap-6 xl:grid-cols-[minmax(0,0.95fr)_minmax(380px,1.05fr)]">
        <section aria-labelledby="priority-lanes-heading">
          <div className="mb-4 flex items-end justify-between">
            <div>
              <p className="font-mono text-[10px] tracking-[0.14em] text-text-faint">INBOUND QUEUE</p>
              <h1 id="priority-lanes-heading" className="mt-1 text-xl font-semibold text-text">Priority lanes</h1>
            </div>
            <span className="font-mono text-xs text-text-muted">03 ACTIVE</span>
          </div>

          <div className="space-y-5">
            {lanes.map(({ lane, tickets }) => (
              <section key={lane}>
                <div className="mb-2 flex items-center gap-2">
                  <LaneBadge lane={lane} />
                  <span className="font-mono text-[10px] text-text-faint">{tickets.length} TICKET</span>
                </div>
                <div className="space-y-2">
                  {tickets.map((ticket) => (
                    <Link
                      key={ticket.id}
                      href={`/tickets/${ticket.id}`}
                      className="block border border-hairline bg-panel p-4 transition-colors hover:border-hairline-bright hover:bg-panel-raised"
                    >
                      <p className="text-sm font-medium text-text">{ticket.subject}</p>
                      <div className="mt-3 flex items-center justify-between gap-3">
                        <span className="font-mono text-[11px] text-text-muted">{ticket.customer}</span>
                        <SentimentBar score={ticket.sentiment} />
                      </div>
                    </Link>
                  ))}
                </div>
              </section>
            ))}
          </div>
        </section>

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
  );
}
