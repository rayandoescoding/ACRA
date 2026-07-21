"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { GuardrailStamp } from "@/components/GuardrailStamp";
import { ProcessTicketButton } from "@/components/tickets/ProcessTicketButton";
import { ApiError } from "@/lib/api-client";
import { formatConfidence, formatProcessingLabel, formatTicketStatus, formatTicketTimestamp } from "@/lib/formatters";
import { priorityToLane, sentimentToScore } from "@/lib/ticket-mappers";
import type { Ticket } from "@/models/ticket";
import type { TicketProcessingResponse } from "@/models/ticket-processing";
import { TicketService } from "@/services/ticket-service";
import { LaneBadge } from "@/components/ui/LaneBadge";
import { SentimentBar } from "@/components/ui/SentimentBar";
import { TicketDetailSkeleton } from "@/components/ui/TicketDetailSkeleton";

type TicketDetailProps = {
  ticketId: string;
};

export function TicketDetail({ ticketId }: TicketDetailProps) {
  const [ticket, setTicket] = useState<Ticket | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isNotFound, setIsNotFound] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [processingResult, setProcessingResult] = useState<TicketProcessingResponse | null>(null);

  useEffect(() => {
    let active = true;
    setProcessingResult(null);

    TicketService.getTicket(ticketId)
      .then((response) => {
        if (active) setTicket(response);
      })
      .catch((caughtError: unknown) => {
        if (!active) return;

        if (caughtError instanceof ApiError && caughtError.status === 404) {
          setIsNotFound(true);
          return;
        }

        setError("Ticket telemetry could not be retrieved. Verify the operator session and backend connection.");
      })
      .finally(() => {
        if (active) setIsLoading(false);
      });

    return () => {
      active = false;
    };
  }, [ticketId]);

  if (isLoading) return <TicketDetailSkeleton />;

  if (isNotFound) {
    return (
      <TicketState
        code="TICKET NOT FOUND"
        title="This ticket is unavailable"
        detail="The requested ticket does not exist or is no longer available to this operator."
      />
    );
  }

  if (error || !ticket) {
    return (
      <TicketState
        code="TICKET CONNECTION ERROR"
        title="Ticket detail unavailable"
        detail={error ?? "The ticket could not be retrieved."}
        tone="error"
      />
    );
  }

  return (
    <div className="mx-auto max-w-5xl">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <p className="font-mono text-[10px] tracking-[0.14em] text-text-faint">TICKET / {ticket.id}</p>
        <Link
          href="/"
          className="border border-hairline px-3 py-2 font-mono text-[10px] tracking-[0.12em] text-text-muted transition-colors hover:border-hairline-bright hover:bg-panel-raised hover:text-text"
        >
          BACK TO DASHBOARD
        </Link>
      </div>

      <div className="mt-3 flex flex-wrap items-start justify-between gap-4 border-b border-hairline pb-5">
        <div>
          <h1 className="text-2xl font-semibold text-text">{ticket.subject}</h1>
          <p className="mt-2 font-mono text-[11px] uppercase tracking-[0.1em] text-text-muted">
            {formatTicketStatus(ticket.status)} / {ticket.category ?? "UNCLASSIFIED"}
          </p>
        </div>
        <LaneBadge lane={priorityToLane(ticket.priority)} />
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-[1fr_0.8fr]">
        <section className="border border-hairline bg-panel p-5" aria-labelledby="ticket-information-heading">
          <h2 id="ticket-information-heading" className="font-mono text-[10px] tracking-[0.14em] text-text-faint">
            TICKET INFORMATION
          </h2>

          {ticket.description && <p className="mt-3 text-sm leading-6 text-text-muted">{ticket.description}</p>}

          <dl className="mt-5 grid gap-4 border-t border-hairline pt-4 sm:grid-cols-2">
            <DetailField label="CATEGORY" value={ticket.category ?? "Unavailable"} />
            <DetailField label="PRIORITY" value={ticket.priority} />
            <DetailField label="STATUS" value={formatTicketStatus(ticket.status)} />
            <div>
              <dt className="font-mono text-[10px] tracking-[0.12em] text-text-faint">SENTIMENT</dt>
              <dd className="mt-2">
                <p className="mb-2 font-mono text-[11px] uppercase text-text-muted">{ticket.sentiment ?? "Unavailable"}</p>
                <SentimentBar score={sentimentToScore(ticket.sentiment)} />
              </dd>
            </div>
            {ticket.intent && <DetailField label="INTENT" value={ticket.intent} />}
            {ticket.ai_summary && <DetailField label="AI SUMMARY" value={ticket.ai_summary} />}
            <DetailField label="CREATED" value={formatTicketTimestamp(ticket.created_at)} />
            <DetailField label="UPDATED" value={formatTicketTimestamp(ticket.updated_at)} />
          </dl>
        </section>

        <section className="border border-hairline bg-panel p-5" aria-labelledby="reasoning-heading">
          <h2 id="reasoning-heading" className="font-mono text-[10px] tracking-[0.14em] text-text-faint">
            REASONING TRACE
          </h2>
          {processingResult ? (
            <ProcessingResult result={processingResult} />
          ) : (
            <>
              <p className="mt-3 text-sm leading-6 text-text-muted">
                Run the existing ticket-processing pipeline to retrieve the current reasoning result.
              </p>
              <ProcessTicketButton ticketId={ticket.id} onProcessed={setProcessingResult} />
            </>
          )}
        </section>
      </div>
    </div>
  );
}

function ProcessingResult({ result }: { result: TicketProcessingResponse }) {
  const { classification, priority, guardrail, resolution } = result;
  const humanReviewRequired = guardrail.requires_human;

  return (
    <div className="mt-5 space-y-5">
      <div className="border-b border-hairline pb-4">
        <p className="font-mono text-[10px] tracking-[0.12em] text-blue-signal">CLASSIFICATION</p>
        <div className="mt-3 flex items-center justify-between gap-3">
          <div>
            <p className="font-mono text-[11px] uppercase text-text-muted">{formatProcessingLabel(classification.sentiment)}</p>
            <p className="mt-1 text-sm text-text-muted">Intent: {formatProcessingLabel(classification.intent)}</p>
          </div>
          <SentimentBar score={classification.sentiment_score} />
        </div>
        <p className="mt-3 text-sm text-text-muted">Sentiment confidence: {formatConfidence(classification.sentiment_confidence)}</p>
      </div>

      <div className="border-b border-hairline pb-4">
        <p className="font-mono text-[10px] tracking-[0.12em] text-blue-signal">PRIORITY & PLAN</p>
        <div className="mt-3 flex items-center gap-3">
          <LaneBadge lane={priorityToLane(priority.ticket_priority)} />
          <p className="font-mono text-[11px] uppercase text-text-muted">{formatProcessingLabel(priority.level)} / SCORE {priority.score}</p>
        </div>
        <p className="mt-3 text-sm text-text-muted">Action: {formatProcessingLabel(result.planning_action)}</p>
        <p className="mt-1 text-sm text-text-muted">Planning confidence: {formatConfidence(result.confidence)}</p>
      </div>

      <div className="border-b border-hairline pb-4">
        <p className="font-mono text-[10px] tracking-[0.12em] text-blue-signal">GUARDRAIL RESULT</p>
        <div className="mt-3">
          <GuardrailStamp passed={!humanReviewRequired} visible />
        </div>
        <p className="mt-3 text-sm text-text-muted">Risk score: {guardrail.risk_score}</p>
        {guardrail.failure_reason && <p className="mt-1 text-sm text-coral">{guardrail.failure_reason}</p>}
        <p className={`mt-3 font-mono text-[11px] tracking-[0.1em] ${humanReviewRequired ? "text-coral" : "text-teal"}`}>
          HUMAN REVIEW: {result.requires_human ? "REQUIRED" : "NOT REQUIRED"}
        </p>
        {humanReviewRequired && <p className="mt-2 text-sm leading-6 text-coral">Human approval is required before this ticket can proceed.</p>}
      </div>

      <div>
        <p className="font-mono text-[10px] tracking-[0.12em] text-blue-signal">RESOLUTION</p>
        <p className="mt-3 font-mono text-[11px] uppercase text-text-muted">{formatProcessingLabel(resolution.outcome)}</p>
        <p className="mt-2 text-sm leading-6 text-text-muted">{resolution.message}</p>
      </div>
    </div>
  );
}


function DetailField({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt className="font-mono text-[10px] tracking-[0.12em] text-text-faint">{label}</dt>
      <dd className="mt-2 text-sm leading-6 text-text-muted">{value}</dd>
    </div>
  );
}

function TicketState({
  code,
  title,
  detail,
  tone = "default",
}: {
  code: string;
  title: string;
  detail: string;
  tone?: "default" | "error";
}) {
  const borderTone = tone === "error" ? "border-coral" : "border-hairline";
  const codeTone = tone === "error" ? "text-coral" : "text-text-faint";

  return (
    <section className={`border ${borderTone} bg-panel p-6 shadow-[0_8px_30px_rgba(0,0,0,0.16)] sm:p-7`} aria-labelledby="ticket-state-heading">
      <p className={`font-mono text-[10px] tracking-[0.14em] ${codeTone}`}>{code}</p>
      <h1 id="ticket-state-heading" className="mt-2 text-lg font-semibold text-text">{title}</h1>
      <p className="mt-2 text-sm leading-6 text-text-muted">{detail}</p>
      <Link
        href="/"
        className="mt-5 inline-flex border border-hairline px-3 py-2 font-mono text-[10px] tracking-[0.12em] text-text-muted transition-colors hover:border-hairline-bright hover:bg-panel-raised hover:text-text"
      >
        BACK TO DASHBOARD
      </Link>
    </section>
  );
}
