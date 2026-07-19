import type { TicketPriority } from "@/models/ticket";

export type TicketLane = "critical" | "high" | "standard";

export function priorityToLane(priority: TicketPriority): TicketLane {
  if (priority === "critical") return "critical";
  if (priority === "high") return "high";
  return "standard";
}

export function sentimentToScore(sentiment: string | null): number {
  switch (sentiment?.trim().toLowerCase()) {
    case "negative":
      return -0.75;
    case "positive":
      return 0.75;
    default:
      return 0;
  }
}
