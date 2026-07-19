"""Common contracts for asynchronous ACRA agents."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, TypeVar


InputT = TypeVar("InputT")
OutputT = TypeVar("OutputT")


@dataclass(frozen=True, slots=True)
class AgentResult(Generic[OutputT]):
    """Result returned by an agent execution.

    ``used_fallback`` records that a deterministic fallback was used instead
    of the primary implementation, allowing callers to retain a complete
    result while preserving operational visibility.
    """

    value: OutputT
    used_fallback: bool = False
    fallback_reason: str | None = None


class BaseAgent(ABC, Generic[InputT, OutputT]):
    """Abstract asynchronous contract implemented by all ACRA agents."""

    @abstractmethod
    async def execute(self, input_data: InputT) -> AgentResult[OutputT]:
        """Execute the agent and return its typed result."""
        raise NotImplementedError
