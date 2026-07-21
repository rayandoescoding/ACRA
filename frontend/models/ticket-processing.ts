import type { TicketPriority } from "@/models/ticket";

export type SentimentLabel = "positive" | "neutral" | "negative";
export type IntentLabel =
  | "account_access"
  | "billing"
  | "cancellation"
  | "delivery"
  | "product_issue"
  | "refund"
  | "general_support";
export type PriorityLevel = "critical" | "high" | "standard";
export type PlanningAction =
  | "refund"
  | "escalate"
  | "troubleshoot"
  | "ask_for_information"
  | "cancel_order"
  | "update_account";
export type GuardrailRule =
  | "required_context"
  | "refund_approval_limit"
  | "refund_eligibility_window"
  | "account_flagged"
  | "excessive_recent_refunds"
  | "high_risk_customer_state";
export type ResolutionOutcome = "automated_response" | "human_review" | "information_requested";

export type ClassificationResultResponse = {
  sentiment: SentimentLabel;
  sentiment_score: number;
  sentiment_confidence: number;
  intent: IntentLabel;
  intent_confidence: number;
  used_fallback: boolean;
};

export type PriorityResultResponse = {
  level: PriorityLevel;
  score: number;
  ticket_priority: TicketPriority;
};

export type GuardrailRuleResponse = {
  rule: GuardrailRule;
  passed: boolean;
  reason: string | null;
  risk_points: number;
};

export type GuardrailResultResponse = {
  passed: boolean;
  risk_score: number;
  failure_reason: string | null;
  requires_human: boolean;
  evaluated_rules: GuardrailRuleResponse[];
};

export type ResolutionOutcomeResponse = {
  outcome: ResolutionOutcome;
  message: string;
  performed_action: PlanningAction | null;
  requires_follow_up: boolean;
  follow_up_reason: string | null;
  persisted_resolution_id: string;
};

export type TicketProcessingResponse = {
  ticket_id: string;
  correlation_id: string | null;
  classification: ClassificationResultResponse;
  priority: PriorityResultResponse;
  planning_action: PlanningAction;
  planning_requires_human: boolean;
  confidence: number;
  guardrail: GuardrailResultResponse;
  resolution: ResolutionOutcomeResponse;
  requires_human: boolean;
};
