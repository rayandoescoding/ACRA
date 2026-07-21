import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, vi } from "vitest";

vi.mock("@/services/ticket-service", () => ({
  TicketService: { getTicket: vi.fn(), processTicket: vi.fn() },
}));

vi.mock("sonner", () => ({
  toast: { success: vi.fn(), error: vi.fn() },
}));

import { TicketDetail } from "@/components/tickets/TicketDetail";
import { ApiError } from "@/lib/api-client";
import type { TicketProcessingResponse } from "@/models/ticket-processing";
import { TicketService } from "@/services/ticket-service";

const ticket = {
  id: "40000000-0000-0000-0000-000000000001",
  customer_id: "10000000-0000-0000-0000-000000000001",
  order_id: null,
  subject: "Refund request",
  description: "Please issue a refund.",
  category: "refund",
  priority: "high",
  status: "open",
  sentiment: "negative",
  intent: "refund",
  ai_summary: null,
  created_at: "2026-01-01T00:00:00Z",
  updated_at: "2026-01-01T00:00:00Z",
} as const;

const interceptedResult: TicketProcessingResponse = {
  ticket_id: ticket.id,
  correlation_id: "correlation-id",
  classification: { sentiment: "negative", sentiment_score: -0.8, sentiment_confidence: 0.9, intent: "refund", intent_confidence: 0.9, used_fallback: false },
  priority: { level: "critical", score: 90, ticket_priority: "critical" },
  planning_action: "refund",
  planning_requires_human: true,
  confidence: 0.9,
  guardrail: { passed: false, risk_score: 60, failure_reason: "Approval limit exceeded", requires_human: true, evaluated_rules: [] },
  resolution: { outcome: "human_review", message: "A human agent will review this request.", performed_action: "escalate", requires_follow_up: true, follow_up_reason: "Approval required", persisted_resolution_id: "50000000-0000-0000-0000-000000000001" },
  requires_human: true,
};

beforeEach(() => vi.clearAllMocks());

test("renders an accessible skeleton while the ticket is requested", () => {
  vi.mocked(TicketService.getTicket).mockReturnValue(new Promise(() => {}));
  render(<TicketDetail ticketId={ticket.id} />);

  expect(screen.getByRole("status", { name: "Loading ticket detail" })).toBeInTheDocument();
});

test("renders a live ticket", async () => {
  vi.mocked(TicketService.getTicket).mockResolvedValue(ticket);
  render(<TicketDetail ticketId={ticket.id} />);

  expect(await screen.findByText(ticket.subject)).toBeInTheDocument();
  expect(screen.getByText(ticket.description)).toBeInTheDocument();
});

test("renders a not-found state", async () => {
  vi.mocked(TicketService.getTicket).mockRejectedValue(new ApiError("Not found", 404));
  render(<TicketDetail ticketId={ticket.id} />);

  expect(await screen.findByText("This ticket is unavailable")).toBeInTheDocument();
});

test("renders a request error", async () => {
  vi.mocked(TicketService.getTicket).mockRejectedValue(new Error("offline"));
  render(<TicketDetail ticketId={ticket.id} />);

  expect(await screen.findByText("Ticket detail unavailable")).toBeInTheDocument();
});

test("renders processing results and intercepted guardrail state", async () => {
  vi.mocked(TicketService.getTicket).mockResolvedValue(ticket);
  vi.mocked(TicketService.processTicket).mockResolvedValue(interceptedResult);
  render(<TicketDetail ticketId={ticket.id} />);

  await screen.findByText(ticket.subject);
  fireEvent.click(screen.getByRole("button", { name: "PROCESS TICKET" }));

  await waitFor(() => expect(screen.getByText("HUMAN REVIEW: REQUIRED")).toBeInTheDocument());
  expect(screen.getByText(interceptedResult.resolution.message)).toBeInTheDocument();
  expect(screen.getByLabelText("Guardrail intercepted")).toBeInTheDocument();
});
