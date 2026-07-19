"""Asynchronous facade for deterministic plan guardrail evaluation."""

from app.agents.base import AgentResult, BaseAgent
from app.agents.context_models import ContextPackage
from app.agents.decision_rules import DecisionRule, DEFAULT_RULES, evaluate_rules
from app.agents.execution_plan import ExecutionPlan
from app.agents.guardrail_models import GuardrailInput, GuardrailResult


class GuardrailAgent(BaseAgent[GuardrailInput, GuardrailResult]):
    """Evaluates a plan before future execution without executing or persisting it."""

    def __init__(self, rules: tuple[DecisionRule, ...] = DEFAULT_RULES) -> None:
        self._rules = rules

    async def execute(self, input_data: GuardrailInput) -> AgentResult[GuardrailResult]:
        """Evaluate deterministic guardrails for an execution-plan request."""
        result = await self.evaluate(input_data.plan, input_data.context)
        return AgentResult(value=result)

    async def evaluate(
        self,
        plan: ExecutionPlan,
        context: ContextPackage,
    ) -> GuardrailResult:
        """Evaluate pure rules and preserve or increase human involvement only."""
        evaluations = evaluate_rules(plan, context, self._rules)
        failures = tuple(evaluation for evaluation in evaluations if not evaluation.passed)
        risk_score = min(100, sum(evaluation.risk_points for evaluation in failures))
        failure_reason = (
            "; ".join(evaluation.reason for evaluation in failures if evaluation.reason)
            or None
        )
        return GuardrailResult(
            passed=not failures,
            risk_score=risk_score,
            failure_reason=failure_reason,
            requires_human=plan.requires_human or bool(failures),
            evaluated_rules=evaluations,
        )
