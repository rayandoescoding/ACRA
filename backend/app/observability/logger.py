"""Safe, structured logging for AI-pipeline observability."""

import logging
from typing import Any


class PipelineEventLogger:
    """Emit pipeline events using a strict allowlist of non-sensitive fields."""

    _ALLOWED_FIELDS = frozenset(
        {
            "agent",
            "duration_ms",
            "intent",
            "outcome",
            "planning_action",
            "priority_level",
            "priority_score",
            "requires_human",
            "risk_score",
            "sentiment",
            "succeeded",
            "used_fallback",
        }
    )

    def __init__(self, logger: logging.Logger | None = None) -> None:
        self._logger = logger or logging.getLogger("acra.observability")

    def info(
        self,
        event: str,
        *,
        correlation_id: str,
        **fields: Any,
    ) -> None:
        """Log one event without accepting customer or ticket data."""
        safe_fields = {
            key: value
            for key, value in fields.items()
            if key in self._ALLOWED_FIELDS
        }
        self._logger.info(
            event,
            extra={
                "event": event,
                "correlation_id": correlation_id,
                **safe_fields,
            },
        )


pipeline_logger = PipelineEventLogger()
