export function formatTicketTimestamp(timestamp: string): string {
  const date = new Date(timestamp);

  if (Number.isNaN(date.getTime())) {
    return "Unavailable";
  }

  return new Intl.DateTimeFormat("en-US", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
}

export function formatTicketStatus(status: string): string {
  return status.replace("_", " ");
}

export function formatProcessingLabel(value: string): string {
  return value.replaceAll("_", " ");
}

export function formatConfidence(value: number): string {
  return `${Math.round(value * 100)}%`;
}
