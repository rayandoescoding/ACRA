export type TicketPriority = "low" | "medium" | "high" | "critical";
export type TicketStatus = "open" | "in_progress" | "resolved" | "closed";

export type Ticket = {
  id: string;
  customer_id: string;
  order_id: string | null;
  subject: string;
  description: string | null;
  category: string | null;
  priority: TicketPriority;
  status: TicketStatus;
  sentiment: string | null;
  intent: string | null;
  ai_summary: string | null;
  created_at: string;
  updated_at: string;
};
