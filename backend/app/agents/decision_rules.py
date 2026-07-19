"""Pure deterministic policy evaluation for the guardrail layer."""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Protocol

from app.agents.context_models import ContextPackage, CustomerOrder
from app.agents.execution_plan import ExecutionPlan
from app.agents.guardrail_models import (
    GuardrailRule,
    RuleEvaluation,
)
from app.agents.planning_models import PlanningAction, RequiredContext
from app.models.account import AccountStatus
from app.models.order import OrderStatus


class DecisionRule(Protocol):
    """A side-effect-free deterministic guardrail rule."""

    def evaluate(self, plan: ExecutionPlan, context: ContextPackage) -> RuleEvaluation:
        """Evaluate a plan using the already retrieved business context."""
        ...


class RequiredContextRule:
    """Require plan-specific context before a downstream action is considered."""

    def evaluate(self, plan: ExecutionPlan, context: ContextPackage) -> RuleEvaluation:
        missing: list[str] = []
        for requirement in plan.required_context:
            if requirement is RequiredContext.CUSTOMER_ACCOUNT and context.account is None:
                missing.append(requirement.value)
            elif requirement is RequiredContext.CUSTOMER_ORDERS and not context.orders:
                missing.append(requirement.value)

        if missing:
            return RuleEvaluation(
                rule=GuardrailRule.REQUIRED_CONTEXT,
                passed=False,
                reason=f"Required context is unavailable: {', '.join(missing)}.",
                risk_points=20,
            )
        return RuleEvaluation(
            rule=GuardrailRule.REQUIRED_CONTEXT,
            passed=True,
            reason=None,
            risk_points=0,
        )


class RefundApprovalLimitRule:
    """Block automatic refunds above the configured deterministic limit."""

    automatic_approval_limit = Decimal("500.00")

    def evaluate(self, plan: ExecutionPlan, context: ContextPackage) -> RuleEvaluation:
        if plan.action is not PlanningAction.REFUND:
            return _pass(GuardrailRule.REFUND_APPROVAL_LIMIT)

        order = _ticket_order(context)
        if order is None:
            return _fail(
                GuardrailRule.REFUND_APPROVAL_LIMIT,
                "A refund cannot be automatically evaluated without the ticket order.",
                40,
            )
        if order.currency != "USD":
            return _fail(
                GuardrailRule.REFUND_APPROVAL_LIMIT,
                "A non-USD refund requires human review because no exchange-rate policy is configured.",
                25,
            )
        if order.amount > self.automatic_approval_limit:
            return _fail(
                GuardrailRule.REFUND_APPROVAL_LIMIT,
                "The refund amount exceeds the automatic approval limit.",
                40,
            )
        return _pass(GuardrailRule.REFUND_APPROVAL_LIMIT)


class RefundEligibilityWindowRule:
    """Require refunds to fall within a deterministic eligibility window."""

    eligibility_window_days = 30

    def evaluate(self, plan: ExecutionPlan, context: ContextPackage) -> RuleEvaluation:
        if plan.action is not PlanningAction.REFUND:
            return _pass(GuardrailRule.REFUND_ELIGIBILITY_WINDOW)

        order = _ticket_order(context)
        if order is None:
            return _fail(
                GuardrailRule.REFUND_ELIGIBILITY_WINDOW,
                "Refund eligibility cannot be evaluated without the ticket order.",
                30,
            )
        now = datetime.now(tz=order.order_date.tzinfo)
        if order.order_date < now - timedelta(days=self.eligibility_window_days):
            return _fail(
                GuardrailRule.REFUND_ELIGIBILITY_WINDOW,
                "The order falls outside the automatic refund eligibility window.",
                30,
            )
        return _pass(GuardrailRule.REFUND_ELIGIBILITY_WINDOW)


class AccountFlaggedRule:
    """Require human review when an account is not active."""

    def evaluate(self, plan: ExecutionPlan, context: ContextPackage) -> RuleEvaluation:
        if context.account is None or context.account.status is AccountStatus.ACTIVE:
            return _pass(GuardrailRule.ACCOUNT_FLAGGED)
        return _fail(
            GuardrailRule.ACCOUNT_FLAGGED,
            "The customer account is not active.",
            35,
        )


class ExcessiveRecentRefundsRule:
    """Detect a deterministic threshold of recently refunded orders."""

    lookback_days = 90
    refund_threshold = 3

    def evaluate(self, plan: ExecutionPlan, context: ContextPackage) -> RuleEvaluation:
        if plan.action is not PlanningAction.REFUND:
            return _pass(GuardrailRule.EXCESSIVE_RECENT_REFUNDS)

        recent_refunds = sum(
            _is_recent_refund(order, self.lookback_days)
            for order in context.orders
        )
        if recent_refunds >= self.refund_threshold:
            return _fail(
                GuardrailRule.EXCESSIVE_RECENT_REFUNDS,
                "The customer has an excessive number of recent refunds.",
                30,
            )
        return _pass(GuardrailRule.EXCESSIVE_RECENT_REFUNDS)


class HighRiskCustomerStateRule:
    """Identify account and refund-history combinations requiring review."""

    lookback_days = 90

    def evaluate(self, plan: ExecutionPlan, context: ContextPackage) -> RuleEvaluation:
        recent_refunds = sum(
            _is_recent_refund(order, self.lookback_days)
            for order in context.orders
        )
        account_is_inactive = (
            context.account is not None
            and context.account.status is not AccountStatus.ACTIVE
        )
        if account_is_inactive and recent_refunds > 0:
            return _fail(
                GuardrailRule.HIGH_RISK_CUSTOMER_STATE,
                "The customer has a non-active account and recent refund activity.",
                25,
            )
        return _pass(GuardrailRule.HIGH_RISK_CUSTOMER_STATE)


DEFAULT_RULES: tuple[DecisionRule, ...] = (
    RequiredContextRule(),
    RefundApprovalLimitRule(),
    RefundEligibilityWindowRule(),
    AccountFlaggedRule(),
    ExcessiveRecentRefundsRule(),
    HighRiskCustomerStateRule(),
)


def evaluate_rules(
    plan: ExecutionPlan,
    context: ContextPackage,
    rules: tuple[DecisionRule, ...] = DEFAULT_RULES,
) -> tuple[RuleEvaluation, ...]:
    """Evaluate deterministic rules without I/O or any external dependencies."""
    return tuple(rule.evaluate(plan, context) for rule in rules)


def _ticket_order(context: ContextPackage) -> CustomerOrder | None:
    """Find the order explicitly linked to the ticket, if it is present."""
    if context.ticket.order_id is None:
        return None
    return next((order for order in context.orders if order.id == context.ticket.order_id), None)


def _is_recent_refund(order: CustomerOrder, lookback_days: int) -> bool:
    """Return whether an order is a refund inside a timezone-compatible window."""
    if order.status is not OrderStatus.REFUNDED:
        return False
    now = datetime.now(tz=order.order_date.tzinfo)
    return order.order_date >= now - timedelta(days=lookback_days)


def _pass(rule: GuardrailRule) -> RuleEvaluation:
    return RuleEvaluation(rule=rule, passed=True, reason=None, risk_points=0)


def _fail(rule: GuardrailRule, reason: str, risk_points: int) -> RuleEvaluation:
    return RuleEvaluation(
        rule=rule,
        passed=False,
        reason=reason,
        risk_points=risk_points,
    )
