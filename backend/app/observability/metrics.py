"""Asynchronous in-memory metrics for AI-pipeline execution."""

import asyncio
from collections import defaultdict
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PipelineMetricsSnapshot:
    """Immutable snapshot suitable for a future metrics exporter."""

    pipeline_successes: int
    pipeline_failures: int
    human_escalations: int
    agent_successes: dict[str, int]
    agent_failures: dict[str, int]
    agent_duration_ms: dict[str, float]


class PipelineMetrics:
    """Collect pipeline metrics safely across concurrent async requests."""

    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._pipeline_successes = 0
        self._pipeline_failures = 0
        self._human_escalations = 0
        self._agent_successes: defaultdict[str, int] = defaultdict(int)
        self._agent_failures: defaultdict[str, int] = defaultdict(int)
        self._agent_duration_ms: defaultdict[str, float] = defaultdict(float)

    async def record_agent_execution(
        self,
        agent: str,
        *,
        duration_ms: float,
        succeeded: bool,
    ) -> None:
        """Record one agent invocation and its elapsed duration."""
        async with self._lock:
            self._agent_duration_ms[agent] += duration_ms
            if succeeded:
                self._agent_successes[agent] += 1
            else:
                self._agent_failures[agent] += 1

    async def record_pipeline_completion(
        self,
        *,
        succeeded: bool,
        requires_human: bool,
    ) -> None:
        """Record the final pipeline outcome and any human escalation."""
        async with self._lock:
            if succeeded:
                self._pipeline_successes += 1
            else:
                self._pipeline_failures += 1
            if requires_human:
                self._human_escalations += 1

    async def snapshot(self) -> PipelineMetricsSnapshot:
        """Return a copy of the current metrics without exposing mutable state."""
        async with self._lock:
            return PipelineMetricsSnapshot(
                pipeline_successes=self._pipeline_successes,
                pipeline_failures=self._pipeline_failures,
                human_escalations=self._human_escalations,
                agent_successes=dict(self._agent_successes),
                agent_failures=dict(self._agent_failures),
                agent_duration_ms=dict(self._agent_duration_ms),
            )


pipeline_metrics = PipelineMetrics()
