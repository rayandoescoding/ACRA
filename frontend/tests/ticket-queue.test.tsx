import { render, screen, waitFor } from "@testing-library/react";
import { beforeEach, vi } from "vitest";

vi.mock("@/services/ticket-service", () => ({
  TicketService: { listTickets: vi.fn() },
}));

import { TicketQueue } from "@/components/dashboard/TicketQueue";
import { TicketService } from "@/services/ticket-service";

const ticket = {
  id: "40000000-0000-0000-0000-000000000001",
  customer_id: "10000000-0000-0000-0000-000000000001",
  order_id: null,
  subject: "Refund request",
  description: null,
  category: "refund",
  priority: "high",
  status: "open",
  sentiment: "negative",
  intent: null,
  ai_summary: null,
  created_at: "2026-01-01T00:00:00Z",
  updated_at: "2026-01-01T00:00:00Z",
} as const;

beforeEach(() => vi.clearAllMocks());

test("renders an accessible skeleton while tickets are requested", () => {
  vi.mocked(TicketService.listTickets).mockReturnValue(new Promise(() => {}));
  render(<TicketQueue />);

  expect(screen.getByRole("status", { name: "Loading ticket queue" })).toBeInTheDocument();
});

test("renders live ticket results", async () => {
  vi.mocked(TicketService.listTickets).mockResolvedValue([ticket]);
  render(<TicketQueue />);

  expect(await screen.findByText(ticket.subject)).toBeInTheDocument();
  expect(screen.getByRole("link", { name: new RegExp(ticket.subject) })).toHaveAttribute("href", `/tickets/${ticket.id}`);
});

test("renders the empty state", async () => {
  vi.mocked(TicketService.listTickets).mockResolvedValue([]);
  render(<TicketQueue />);

  expect(await screen.findByText("No tickets available")).toBeInTheDocument();
});

test("renders the error state", async () => {
  vi.mocked(TicketService.listTickets).mockRejectedValue(new Error("offline"));
  render(<TicketQueue />);

  await waitFor(() => expect(screen.getByText("Ticket feed unavailable")).toBeInTheDocument());
});
