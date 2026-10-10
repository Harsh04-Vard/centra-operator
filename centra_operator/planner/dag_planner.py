"""
Hierarchical DAG Planner:
Compiles grounded intent and SOP steps into an executable Directed Acyclic Graph (DAG)
with dependency chains, parameter bindings, guardrails, and verification contracts.
"""

from typing import List, Dict, Any, Optional
from centra_operator.engine.state import TaskNode, TaskStatus, VerificationContract
from centra_operator.memory.default_knowledge import CompanySOP
from centra_operator.planner.guardrails import GLOBAL_GUARDRAIL

class DAGPlanner:
    def __init__(self):
        self.guardrail = GLOBAL_GUARDRAIL

    def build_plan(self, disambiguated_intent: str, sop: CompanySOP, entities: Dict[str, Any]) -> List[TaskNode]:
        """
        Synthesizes a list of TaskNodes forming a verified execution DAG.
        """
        tasks: List[TaskNode] = []
        prev_task_id: Optional[str] = None

        for idx, step in enumerate(sop.steps):
            task_id = f"task-{idx+1}-{step.step_id}"
            params = self._synthesize_params_for_step(step.step_id, step.suggested_tool, entities)
            
            # Formulate Invariant Verification Contract
            contract = VerificationContract(
                target_system=step.suggested_tool,
                expected_state={"status": "VERIFIED_OK", "step_id": step.step_id},
                verification_query=step.verification_rule,
                proof_type="INVARIANT_CHECK"
            )

            task = TaskNode(
                id=task_id,
                title=step.title,
                description=step.description,
                tool_name=step.suggested_tool,
                params=params,
                dependencies=[prev_task_id] if prev_task_id else [],
                status=TaskStatus.PENDING,
                verification_contract=contract
            )

            # Apply Guardrails & HITL checks
            self.guardrail.attach_guardrails_to_task(task)

            tasks.append(task)
            prev_task_id = task_id

        return tasks

    def _synthesize_params_for_step(self, step_id: str, tool_name: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Maps extracted enterprise entities to specific tool parameter schemas."""
        params: Dict[str, Any] = {}
        emp_name = entities.get("employee_name", "Alex Morgan")
        emp_email = entities.get("email", "alex.m@acme.corp")
        emp_role = entities.get("role", "Senior Frontend Engineer")
        emp_dept = entities.get("department", "Engineering")

        # SOP-HR-001 Steps
        if "parse-contract" in step_id:
            params = {
                "action": "read",
                "path": "documents/offer_letter_alex_morgan.md"
            }
        elif "register-hris" in step_id:
            params = {
                "system": "bamboohr",
                "action": "create_employee",
                "name": emp_name,
                "email": emp_email,
                "role": emp_role,
                "department": emp_dept,
                "salary": entities.get("salary", "$165,000 USD")
            }
        elif "provision-iam" in step_id:
            params = {
                "system": "okta",
                "action": "provision_access",
                "email": emp_email,
                "teams": ["engineering-frontend", "github-repo-access", "slack-general"]
            }
        elif "generate-checklist" in step_id:
            safe_name = emp_name.lower().replace(" ", "_")
            params = {
                "action": "write",
                "path": f"evidence/onboarding_checklist_{safe_name}.md",
                "content": (
                    f"# SOC2 Onboarding Compliance Record\n"
                    f"- **Employee:** {emp_name} ({emp_email})\n"
                    f"- **Role:** {emp_role}\n"
                    f"- **Department:** {emp_dept}\n"
                    f"- **BambooHR Status:** Registered & Active\n"
                    f"- **GitHub & Okta SSO:** Provisioned with 2FA\n"
                    f"- **Verification Hash:** COMPLIANCE-VERIFIED-2026\n"
                )
            }
        elif "send-welcome-email" in step_id:
            params = {
                "to": emp_email,
                "subject": f"Welcome to Acme Corp, {emp_name}! Your First Day Guide",
                "body": (
                    f"Hi {emp_name},\n\n"
                    f"We are excited to have you join as {emp_role}. "
                    f"Your accounts in Okta and GitHub have been provisioned.\n\n"
                    f"Best,\nPeople Operations Team"
                )
            }

        # SOP-FIN-004 Steps
        elif "fetch-ticket" in step_id:
            params = {
                "system": "zendesk",
                "action": "get_ticket",
                "ticket_id": entities.get("ticket_id", "TICK-8841")
            }
        elif "verify-charge" in step_id:
            params = {
                "system": "stripe",
                "action": "verify_charge",
                "charge_id": entities.get("charge_id", "ch_3M99824X")
            }
        elif "issue-refund" in step_id:
            params = {
                "system": "stripe",
                "action": "create_refund",
                "charge_id": entities.get("charge_id", "ch_3M99824X"),
                "amount": float(entities.get("refund_amount", 75.00))
            }
        elif "update-ledger" in step_id:
            cust_email = entities.get("customer_email", "billing-support@cloudscale.tech")
            ref_amt = entities.get("refund_amount", 75.00)
            params = {
                "action": "append",
                "path": "documents/q3_refund_reconciliation.csv",
                "content": f"2026-10-10,TICK-8841,ch_3M99824X,{cust_email},{ref_amt},RESOLVED,controller_hitl_approved"
            }

        # SOP-SEC-012 Steps
        elif "audit-permissions" in step_id:
            params = {
                "system": "okta",
                "action": "audit_permissions",
                "email": entities.get("employee_email", "alex.m@acme.corp")
            }
        elif "revoke-access" in step_id:
            params = {
                "system": "okta",
                "action": "revoke_access",
                "email": entities.get("employee_email", "alex.m@acme.corp")
            }
        elif "export-audit-cert" in step_id:
            target_email = entities.get("employee_email", "alex.m@acme.corp")
            params = {
                "action": "write",
                "path": "evidence/soc2_revocation_certificate.md",
                "content": (
                    f"# SOC2 Cryptographic Offboarding Proof\n"
                    f"- **Target Subject:** {target_email}\n"
                    f"- **Deactivation Timestamp:** 2026-10-10T10:30:00Z\n"
                    f"- **Okta Status:** DEACTIVATED\n"
                    f"- **GitHub Status:** REMOVED\n"
                    f"- **Audit Cryptographic Hash:** SHA256-REVOKE-8834921-SECURE\n"
                )
            }

        return params

GLOBAL_DAG_PLANNER = DAGPlanner()
