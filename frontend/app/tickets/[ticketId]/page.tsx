import { AuthGuard } from "@/components/auth/AuthGuard";
import { PageLayout } from "@/components/layout/PageLayout";
import { TicketDetail } from "@/components/tickets/TicketDetail";

export default async function TicketDetailPage({
  params,
}: {
  params: Promise<{ ticketId: string }>;
}) {
  const { ticketId } = await params;

  return (
    <AuthGuard>
      <PageLayout activeRoute="ticket">
        <TicketDetail ticketId={ticketId} />
      </PageLayout>
    </AuthGuard>
  );
}
