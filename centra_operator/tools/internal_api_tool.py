"""
Internal Enterprise API Tools:
Connectors for BambooHR (HRIS), Stripe (Billing/Refunds), Okta/GitHub (IAM), and Zendesk.
"""

from typing import Any, Dict, List, Optional
import time
import uuid
from centra_operator.tools.base import BaseTool, ToolResult
from centra_operator.engine.state import RiskLevel

class InternalApiTool(BaseTool):
    name = "internal_api_tool"
    description = "Interact with internal enterprise systems: BambooHR, Stripe, Okta/GitHub IAM, and Zendesk."
    risk_level = RiskLevel.MEDIUM

    def __init__(self):
        # In-memory realistic enterprise mock state
        self.hris_records: Dict[str, Dict[str, Any]] = {}
        self.iam_memberships: Dict[str, List[str]] = {
            "alex.m@acme.corp": ["slack.general"]
        }
        self.stripe_charges: Dict[str, Dict[str, Any]] = {
            "ch_3M99824X": {
                "id": "ch_3M99824X",
                "customer": "cus_991823",
                "customer_email": "billing-support@cloudscale.tech",
                "amount": 75.00,
                "currency": "usd",
                "status": "succeeded",
                "refunded": False
            }
        }
        self.zendesk_tickets: Dict[str, Dict[str, Any]] = {
            "TICK-8841": {
                "id": "TICK-8841",
                "subject": "Double Charge on Q3 Invoicing",
                "customer_email": "billing-support@cloudscale.tech",
                "charge_id": "ch_3M99824X",
                "requested_refund_usd": 75.00,
                "status": "OPEN",
                "notes": []
            }
        }

    def execute(self, params: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> ToolResult:
        system = params.get("system", "")
        action = params.get("action", "")

        try:
            # 1. BambooHR System
            if system == "bamboohr":
                if action == "create_employee":
                    emp_id = f"EMP-{len(self.hris_records) + 1090}"
                    record = {
                        "id": emp_id,
                        "name": params.get("name", ""),
                        "email": params.get("email", ""),
                        "role": params.get("role", ""),
                        "department": params.get("department", "Engineering"),
                        "salary": params.get("salary", "$165,000"),
                        "status": "ACTIVE",
                        "created_at": time.time()
                    }
                    self.hris_records[record["email"]] = record
                    return ToolResult(
                        success=True,
                        output=record,
                        evidence={"system": "bamboohr", "employee_id": emp_id, "status": "ACTIVE"}
                    )
                elif action == "get_employee":
                    email = params.get("email")
                    record = self.hris_records.get(email)
                    if record:
                        return ToolResult(success=True, output=record, evidence=record)
                    return ToolResult(success=False, output=None, error=f"Employee {email} not found in HRIS")

            # 2. Okta & GitHub IAM System
            elif system in ("okta", "github", "iam"):
                email = params.get("email", "")
                if action == "provision_access":
                    teams = params.get("teams", ["engineering-frontend", "github-repo-access"])
                    current = self.iam_memberships.get(email, [])
                    updated = list(set(current + teams))
                    self.iam_memberships[email] = updated
                    return ToolResult(
                        success=True,
                        output=f"Provisioned IAM roles for {email}: {updated}",
                        evidence={"email": email, "roles": updated, "2fa_enforced": True}
                    )
                elif action == "revoke_access":
                    self.iam_memberships[email] = []
                    return ToolResult(
                        success=True,
                        output=f"Revoked all Okta SSO and GitHub organization memberships for {email}",
                        evidence={"email": email, "active_roles_count": 0, "status": "DEACTIVATED"}
                    )
                elif action == "audit_permissions":
                    roles = self.iam_memberships.get(email, [])
                    return ToolResult(
                        success=True,
                        output={"email": email, "active_permissions": roles},
                        evidence={"email": email, "permissions": roles}
                    )

            # 3. Stripe Billing System
            elif system == "stripe":
                if action == "verify_charge":
                    charge_id = params.get("charge_id", "ch_3M99824X")
                    charge = self.stripe_charges.get(charge_id)
                    if not charge:
                        return ToolResult(success=False, output=None, error=f"Stripe charge {charge_id} not found")
                    return ToolResult(
                        success=True,
                        output=charge,
                        evidence={"charge_id": charge_id, "refundable": not charge["refunded"], "amount": charge["amount"]}
                    )
                elif action == "create_refund":
                    charge_id = params.get("charge_id", "ch_3M99824X")
                    amount = float(params.get("amount", 75.00))
                    charge = self.stripe_charges.get(charge_id)
                    if not charge:
                        return ToolResult(success=False, output=None, error=f"Stripe charge {charge_id} not found")
                    
                    refund_id = f"re_{uuid.uuid4().hex[:12]}"
                    charge["refunded"] = True
                    charge["refund_id"] = refund_id
                    charge["refund_amount"] = amount
                    
                    return ToolResult(
                        success=True,
                        output={
                            "refund_id": refund_id,
                            "charge_id": charge_id,
                            "amount_refunded": amount,
                            "currency": "usd",
                            "status": "succeeded"
                        },
                        evidence={"refund_id": refund_id, "charge_id": charge_id, "status": "succeeded"}
                    )

            # 4. Zendesk System
            elif system == "zendesk":
                if action == "get_ticket":
                    ticket_id = params.get("ticket_id", "TICK-8841")
                    ticket = self.zendesk_tickets.get(ticket_id)
                    if not ticket:
                        return ToolResult(success=False, output=None, error=f"Ticket {ticket_id} not found")
                    return ToolResult(success=True, output=ticket, evidence=ticket)
                elif action == "resolve_ticket":
                    ticket_id = params.get("ticket_id", "TICK-8841")
                    ticket = self.zendesk_tickets.get(ticket_id)
                    if ticket:
                        ticket["status"] = "RESOLVED"
                        ticket["resolution_note"] = params.get("note", "Refund processed successfully")
                        return ToolResult(
                            success=True,
                            output=f"Zendesk Ticket {ticket_id} marked RESOLVED",
                            evidence={"ticket_id": ticket_id, "status": "RESOLVED"}
                        )

            return ToolResult(success=False, output=None, error=f"Unhandled system '{system}' or action '{action}'")

        except Exception as e:
            return ToolResult(success=False, output=None, error=str(e))
