import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, vi } from "vitest";

vi.mock("@/services/ticket-service", () => ({
  TicketService: { processTicket: vi.fn() },
}));

vi.mock("sonner", () => ({
  toast: { success: vi.fn(), error: vi.fn() },
}));

import { ProcessTicketButton } from "@/components/tickets/ProcessTicketButton";
import { ApiError } from "@/lib/api-client";
import type { TicketProcessingResponse } from "@/models/ticket-processing";
import { TicketService } from "@/services/ticket-service";
import { toast } from "sonner";

const processingResult: TicketProcessingResponse = {
  ticket_id: "40000000-0000-0000-0000-000000000001",
  correlation_id: null,
  classification: { sentiment: "negative", sentiment_score: -0.5, sentiment_confidence: 0.9, intent: "refund", intent_confidence: 0.9, used_fallback: false },
  priority: { level: "high", score: 60, ticket_priority: "high" },
  planning_action: "refund",
  planning_requires_human: false,
  confidence: 0.9,
  guardrail: { passed: true, risk_score: 0, failure_reason: null, requires_human: false, evaluated_rules: [] },
  resolution: { outcome: "automated_response", message: "Resolved", performed_action: "refund", requires_follow_up: false, follow_up_reason: null, persisted_resolution_id: "50000000-0000-0000-0000-000000000001" },
  requires_human: false,
};

beforeEach(() => vi.clearAllMocks());

test("disables while processing, announces progress, and reports success", async () => {
  let resolveRequest: (value: typeof processingResult) => void;
  vi.mocked(TicketService.processTicket).mockReturnValue(new Promise((resolve) => { resolveRequest = resolve; }));
  const onProcessed = vi.fn();
  render(<ProcessTicketButton ticketId={processingResult.ticket_id} onProcessed={onProcessed} />);

  fireEvent.click(screen.getByRole("button", { name: "PROCESS TICKET" }));
  expect(screen.getByRole("button")).toBeDisabled();
  expect(screen.getByRole("status")).toHaveTextContent("PROCESSING / CLASSIFICATION");

  resolveRequest!(processingResult);
  await waitFor(() => expect(onProcessed).toHaveBeenCalledWith(processingResult));
  expect(TicketService.processTicket).toHaveBeenCalledWith(processingResult.ticket_id);
  expect(toast.success).toHaveBeenCalledWith("Ticket processing completed.");
});

test("keeps the accessible API error and shows a failure toast", async () => {
  vi.mocked(TicketService.processTicket).mockRejectedValue(new ApiError("Processing failed", 500));
  render(<ProcessTicketButton ticketId={processingResult.ticket_id} onProcessed={vi.fn()} />);

  fireEvent.click(screen.getByRole("button", { name: "PROCESS TICKET" }));
  expect(await screen.findByRole("alert")).toHaveTextContent("Processing failed");
  expect(toast.error).toHaveBeenCalledWith("Processing failed");
});
