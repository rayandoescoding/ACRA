"""Correlation-ID propagation and timing for pipeline executions."""

from contextlib import asynccontextmanager
from contextvars import ContextVar, Token
from dataclasses import dataclass
from time import perf_counter
from typing import AsyncIterator
from uuid import uuid4


_correlation_id: ContextVar[str | None] = ContextVar(
    "acra_pipeline_correlation_id",
    default=None,
)


@dataclass(frozen=True, slots=True)
class PipelineTrace:
    """Non-sensitive trace metadata for one pipeline execution."""

    correlation_id: str
    started_at: float

    def elapsed_ms(self) -> float:
        """Return elapsed monotonic time in milliseconds."""
        return (perf_counter() - self.started_at) * 1_000


def get_correlation_id() -> str | None:
    """Return the correlation ID active in the current async context."""
    return _correlation_id.get()


@asynccontextmanager
async def pipeline_trace(
    correlation_id: str | None = None,
) -> AsyncIterator[PipelineTrace]:
    """Establish and clean up a correlation ID for one pipeline execution."""
    trace = PipelineTrace(
        correlation_id=correlation_id or str(uuid4()),
        started_at=perf_counter(),
    )
    token: Token[str | None] = _correlation_id.set(trace.correlation_id)
    try:
        yield trace
    finally:
        _correlation_id.reset(token)
