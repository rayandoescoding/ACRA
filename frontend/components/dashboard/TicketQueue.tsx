"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { priorityToLane, sentimentToScore, type TicketLane } from "@/lib/ticket-mappers";
import type { Ticket } from "@/models/ticket";
import { TicketService } from "@/services/ticket-service";
import { LaneBadge } from "@/components/ui/LaneBadge";
import { LoadingState } from "@/components/ui/LoadingState";
import { SentimentBar } from "@/components/ui/SentimentBar";

const laneOrder: TicketLane[] = ["critical", "high", "standard"];

export function TicketQueue() {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let active = true;

    TicketService.listTickets()
      .then((response) => {
        if (active) setTickets(response);
      })
      .catch(() => {
        if (active) setError("Ticket telemetry could not be retrieved. Verify the operator session and backend connection.");
      })
      .finally(() => {
        if (active) setIsLoading(false);
      });

    return () => {
      active = false;
    };
  }, []);

  if (isLoading) return <LoadingState label="LOADING TICKET QUEUE" />;

  if (error) {
    return (
      <section className="border border-coral bg-panel p-6" aria-labelledby="ticket-error-heading">
        <p className="font-mono text-[10px] tracking-[0.14em] text-coral">QUEUE CONNECTION ERROR</p>
        <h2 id="ticket-error-heading" className="mt-2 text-lg font-semibold text-text">Ticket feed unavailable</h2>
        <p className="mt-2 text-sm leading-6 text-text-muted">{error}</p>
      </section>
    );
  }

  if (tickets.length === 0) {
    return (
      <section className="border border-hairline bg-panel p-6" aria-labelledby="ticket-empty-heading">
        <p className="font-mono text-[10px] tracking-[0.14em] text-text-faint">INBOUND QUEUE</p>
        <h2 id="ticket-empty-heading" className="mt-2 text-lg font-semibold text-text">No tickets available</h2>
        <p className="mt-2 text-sm leading-6 text-text-muted">The authenticated ticket queue has no records at this time.</p>
      </section>
    );
  }

  return (
    <section aria-labelledby="priority-lanes-heading">
      <div className="mb-4 flex items-end justify-between">
        <div>
          <p className="font-mono text-[10px] tracking-[0.14em] text-text-faint">INBOUND QUEUE</p>
          <h1 id="priority-lanes-heading" className="mt-1 text-xl font-semibold text-text">Priority lanes</h1>
        </div>
        <span className="font-mono text-xs text-text-muted">{String(tickets.length).padStart(2, "0")} ACTIVE</span>
      </div>

      <div className="space-y-5">
        {laneOrder.map((lane) => {
          const laneTickets = tickets.filter((ticket) => priorityToLane(ticket.priority) === lane);

          if (laneTickets.length === 0) return null;

          return (
            <section key={lane}>
              <div className="mb-2 flex items-center gap-2">
                <LaneBadge lane={lane} />
                <span className="font-mono text-[10px] text-text-faint">{laneTickets.length} TICKET{laneTickets.length === 1 ? "" : "S"}</span>
              </div>
              <div className="space-y-2">
                {laneTickets.map((ticket) => (
                  <Link
                    key={ticket.id}
                    href={`/tickets/${ticket.id}`}
                    className="block border border-hairline bg-panel p-4 transition-colors hover:border-hairline-bright hover:bg-panel-raised"
                  >
                    <p className="text-sm font-medium text-text">{ticket.subject}</p>
                    <div className="mt-3 flex items-center justify-between gap-3">
                      <span className="font-mono text-[11px] uppercase text-text-muted">{ticket.status.replace("_", " ")}</span>
                      <SentimentBar score={sentimentToScore(ticket.sentiment)} />
                    </div>
                  </Link>
                ))}
              </div>
            </section>
          );
        })}
      </div>
    </section>
  );
}
