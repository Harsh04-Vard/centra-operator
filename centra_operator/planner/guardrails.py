"""
Policy Guardrails and Risk Assessment Engine:
Inspects task nodes, evaluates company policies, detects blast radius,
and automatically triggers Human-in-the-Loop (HITL) approval gates.
"""

from typing import Any, Dict, Optional, Tuple
from centra_operator.engine.state import TaskNode, RiskLevel, ApprovalRequest
from centra_operator.memory.store import GLOBAL_MEMORY
from centra_operator.config import CONFIG

class GuardrailEngine:
    def __init__(self):
        self.memory = GLOBAL_MEMORY

    def evaluate_task_risk(self, task: TaskNode) -> Tuple[RiskLevel, bool, Optional[str]]:
        """
        Evaluates risk level and determines if task requires human signoff.
        Returns: (RiskLevel, requires_approval, reason)
        """
        action = task.params.get("action", "")

        # 1. Read-only actions are always SAFE
        if action in ("read", "get_ticket", "verify_charge", "audit_permissions", "extract_dom", "hash"):
            return (RiskLevel.LOW, False, None)

        # 2. Financial threshold policy check
        amount = task.params.get("amount") or task.params.get("refund_amount")
        if amount is not None and action == "create_refund":
            try:
                amt_val = float(amount)
                if amt_val > CONFIG.financial_approval_threshold_usd:
                    return (
                        RiskLevel.HIGH,
                        True,
                        f"FIN-POL-04: Transaction amount ${amt_val:.2f} exceeds auto-approval threshold (${CONFIG.financial_approval_threshold_usd:.2f})."
                    )
            except ValueError:
                pass

        # 3. Sensitive External Actions
        if task.tool_name == "email_dispatcher":
            recipient = task.params.get("to", "external")
            return (
                RiskLevel.HIGH,
                True,
                f"External communication to '{recipient}'. Requires human content and recipient verification."
            )

        if task.tool_name in ("okta_github_iam", "internal_api_tool") and action == "revoke_access":
            return (
                RiskLevel.HIGH,
                True,
                "SEC-POL-09: Irreversible de-provisioning of employee credentials across all systems."
            )

        # 4. Standard Tool Policy check in Org Graph (for non-read actions)
        policy = self.memory.org_graph.tool_policies.get(task.tool_name)
        if policy and policy.requires_hitl_approval and action not in ("read", "verify_charge", "get_ticket"):
            return (
                RiskLevel(policy.risk_level),
                True,
                f"Org Policy '{policy.tool_name}': {policy.policy_description}"
            )

        return (task.risk_level, False, None)

    def attach_guardrails_to_task(self, task: TaskNode):
        risk_level, requires_approval, reason = self.evaluate_task_risk(task)
        task.risk_level = risk_level
        task.requires_approval = requires_approval
        
        if requires_approval:
            task.approval_request = ApprovalRequest(
                task_id=task.id,
                task_description=task.description,
                risk_level=risk_level,
                reason=reason or "High-risk enterprise action requires confirmation.",
                proposed_action=f"Execute {task.tool_name} with parameters: {task.params}",
                tool_name=task.tool_name,
                tool_params=task.params,
                blast_radius=self._calculate_blast_radius(task)
            )

    def _calculate_blast_radius(self, task: TaskNode) -> str:
        if task.tool_name == "email_dispatcher":
            return f"External email delivered to recipient: {task.params.get('to')}"
        elif "refund" in task.description.lower():
            return f"Financial debit of ${task.params.get('amount', 0.00):.2f} USD via Stripe gateway."
        elif "revoke" in task.description.lower():
            return "Complete suspension of SSO session tokens and GitHub commit access."
        return "Internal system modification."

GLOBAL_GUARDRAIL = GuardrailEngine()
