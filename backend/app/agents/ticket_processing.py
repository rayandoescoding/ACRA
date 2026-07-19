"""Compatibility exports for the relocated ticket-processing orchestrator."""

from app.orchestrator.ticket_processing import (
    ProcessingTicketNotFoundError,
    TicketProcessingOrchestrator,
    TicketProcessingResult,
)

# Retain the existing import path and public class name for current callers.
TicketProcessingWorkflow = TicketProcessingOrchestrator

__all__ = [
    "ProcessingTicketNotFoundError",
    "TicketProcessingResult",
    "TicketProcessingWorkflow",
]
