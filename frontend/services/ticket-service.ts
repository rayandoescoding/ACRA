import { apiClient } from "@/lib/api-client";
import type { Ticket } from "@/models/ticket";

export const TicketService = {
  listTickets(offset = 0, limit = 100): Promise<Ticket[]> {
    const query = new URLSearchParams({ offset: String(offset), limit: String(limit) });
    return apiClient<Ticket[]>(`/tickets?${query.toString()}`);
  },
};
