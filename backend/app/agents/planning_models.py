"""Typed vocabulary used by the Phase 6 planning layer."""

from enum import Enum


class PlanningAction(str, Enum):
    """Actions that a planner may recommend without executing them."""

    REFUND = "refund"
    ESCALATE = "escalate"
    TROUBLESHOOT = "troubleshoot"
    ASK_FOR_INFORMATION = "ask_for_information"
    CANCEL_ORDER = "cancel_order"
    UPDATE_ACCOUNT = "update_account"


class NextAgent(str, Enum):
    """Future handling targets selected by the planner."""

    HUMAN_REVIEW = "human_review"
    RESOLUTION_GENERATION = "resolution_generation"
    INFORMATION_COLLECTION = "information_collection"
    ACCOUNT_OPERATIONS = "account_operations"
    ORDER_OPERATIONS = "order_operations"


class RequiredContext(str, Enum):
    """Context subsets a later stage needs to safely evaluate a plan."""

    TICKET = "ticket"
    CUSTOMER_PROFILE = "customer_profile"
    CUSTOMER_ACCOUNT = "customer_account"
    CUSTOMER_ORDERS = "customer_orders"
    PREVIOUS_TICKETS = "previous_tickets"
    PREVIOUS_RESOLUTIONS = "previous_resolutions"
