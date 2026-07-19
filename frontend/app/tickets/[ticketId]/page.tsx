import { AuthGuard } from "@/components/auth/AuthGuard";
import { GuardrailStamp } from "@/components/GuardrailStamp";
import { PageLayout } from "@/components/layout/PageLayout";
import { LaneBadge } from "@/components/ui/LaneBadge";
import { SentimentBar } from "@/components/ui/SentimentBar";

export default function TicketDetailPage() {
  return (
    <AuthGuard>
      <PageLayout activeRoute="ticket">
      <div className="mx-auto max-w-5xl">
        <p className="font-mono text-[10px] tracking-[0.14em] text-text-faint">TICKET / DEMO-001 / STATIC FOUNDATION DATA</p>
        <div className="mt-3 flex flex-wrap items-start justify-between gap-4 border-b border-hairline pb-5">
          <div>
            <h1 className="text-2xl font-semibold text-text">Urgent refund request for enterprise subscription</h1>
            <p className="mt-2 text-sm text-text-muted">Bruno Singh · Enterprise account · Order $1,250.00</p>
          </div>
          <LaneBadge lane="critical" />
        </div>

        <div className="mt-6 grid gap-6 lg:grid-cols-[1fr_0.8fr]">
          <section className="border border-hairline bg-panel p-5">
            <h2 className="font-mono text-[10px] tracking-[0.14em] text-text-faint">CUSTOMER SIGNAL</h2>
            <p className="mt-3 text-sm leading-6 text-text-muted">“I am frustrated and need a refund for this charge.”</p>
            <div className="mt-5 flex items-center justify-between border-t border-hairline pt-4">
              <span className="font-mono text-[10px] tracking-[0.12em] text-text-faint">SENTIMENT</span>
              <SentimentBar score={-0.88} />
            </div>
          </section>

          <section className="border border-hairline bg-panel p-5">
            <h2 className="font-mono text-[10px] tracking-[0.14em] text-text-faint">GUARDRAIL LEDGER</h2>
            <p className="mt-3 text-sm leading-6 text-text-muted">Automatic refund action is held for human review because the request exceeds the configured financial threshold.</p>
            <div className="mt-5"><GuardrailStamp passed={false} visible /></div>
          </section>
        </div>
      </div>
      </PageLayout>
    </AuthGuard>
  );
}
