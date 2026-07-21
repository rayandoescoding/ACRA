"use client";

import { useState } from "react";
import { toast } from "sonner";

import { ProcessingProgress } from "@/components/tickets/ProcessingProgress";
import { ApiError } from "@/lib/api-client";
import type { TicketProcessingResponse } from "@/models/ticket-processing";
import { TicketService } from "@/services/ticket-service";

type ProcessTicketButtonProps = {
  ticketId: string;
  onProcessed: (result: TicketProcessingResponse) => void;
};

export function ProcessTicketButton({ ticketId, onProcessed }: ProcessTicketButtonProps) {
  const [error, setError] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);

  async function processTicket() {
    setError(null);
    setIsProcessing(true);

    try {
      const result = await TicketService.processTicket(ticketId);
      toast.success("Ticket processing completed.");
      onProcessed(result);
    } catch (caughtError) {
      const message = caughtError instanceof ApiError ? caughtError.message : "Ticket processing could not be completed.";
      setError(message);
      toast.error(message);
    } finally {
      setIsProcessing(false);
    }
  }

  return (
    <div className="mt-5">
      <ProcessingProgress active={isProcessing} />
      <button
        type="button"
        onClick={processTicket}
        disabled={isProcessing}
        className="border border-teal bg-teal-dim px-4 py-3 font-mono text-xs font-semibold tracking-[0.14em] text-teal transition-colors hover:border-teal hover:bg-panel-raised disabled:cursor-not-allowed disabled:border-hairline disabled:text-text-faint"
      >
        {isProcessing ? "PROCESSING TICKET…" : "PROCESS TICKET"}
      </button>
      {error && (
        <p className="mt-3 border border-coral bg-coral-dim px-3 py-2 font-mono text-xs text-coral" role="alert">
          {error}
        </p>
      )}
    </div>
  );
}
