import { apiClient } from "@/lib/api-client";
import type { Ticket } from "@/models/ticket";
import type { TicketProcessingResponse } from "@/models/ticket-processing";

export const TicketService = {
  listTickets(offset = 0, limit = 100): Promise<Ticket[]> {
    const query = new URLSearchParams({ offset: String(offset), limit: String(limit) });
    return apiClient<Ticket[]>(`/tickets?${query.toString()}`);
  },

  getTicket(ticketId: string): Promise<Ticket> {
    return apiClient<Ticket>(`/tickets/${ticketId}`);
  },

  processTicket(ticketId: string): Promise<TicketProcessingResponse> {
    return apiClient<TicketProcessingResponse>(`/tickets/${ticketId}/process`, {
      method: "POST",
    });
  },
};
