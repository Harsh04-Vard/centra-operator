"""
Standard Operating Procedures (SOPs) and Enterprise Knowledge Base.
Contains executable procedures, required steps, permitted tools, and invariant rules.
"""

from typing import List, Dict, Any
from pydantic import BaseModel, Field

class SOPStep(BaseModel):
    step_id: str
    title: str
    description: str
    suggested_tool: str
    risk_level: str
    requires_hitl: bool = False
    verification_rule: str

class CompanySOP(BaseModel):
    id: str
    title: str
    department: str
    trigger_keywords: List[str]
    description: str
    required_inputs: List[str]
    steps: List[SOPStep]
    policy_notes: str

def get_default_sops() -> List[CompanySOP]:
    return [
        CompanySOP(
            id="SOP-HR-001",
            title="Employee Onboarding and Identity Provisioning",
            department="Human Resources",
            trigger_keywords=["onboard", "new hire", "provision", "employee", "alex", "engineer onboarding"],
            description="Complete end-to-end onboarding: parse offer contract, register in BambooHR, provision GitHub and Okta access, generate welcome kit, send welcome email (HITL approval required), and create compliance audit bundle.",
            required_inputs=["employee_name", "role", "department", "email", "start_date"],
            policy_notes="Requires manager notification and explicit HITL approval before dispatching external welcome emails.",
            steps=[
                SOPStep(
                    step_id="step-1-parse-contract",
                    title="Extract and Verify Employment Agreement",
                    description="Read contract from Dropbox/documents repository, extract salary, role, start date, and verify signed status.",
                    suggested_tool="file_operator",
                    risk_level="LOW",
                    requires_hitl=False,
                    verification_rule="Contract signed status == TRUE and SHA256 checksum recorded."
                ),
                SOPStep(
                    step_id="step-2-register-hris",
                    title="Create Employee Profile in BambooHR",
                    description="Submit new hire record with personal details, department, and salary into BambooHR API.",
                    suggested_tool="bamboohr_api",
                    risk_level="MEDIUM",
                    requires_hitl=False,
                    verification_rule="BambooHR employee record exists with status 'ACTIVE' and matching email."
                ),
                SOPStep(
                    step_id="step-3-provision-iam",
                    title="Provision Okta SSO and GitHub Team Access",
                    description="Grant Engineering team repository access, assign Okta SSO tiles for Slack, Jira, and GitHub.",
                    suggested_tool="okta_github_iam",
                    risk_level="MEDIUM",
                    requires_hitl=False,
                    verification_rule="GitHub team membership confirmed for 'engineering-frontend'."
                ),
                SOPStep(
                    step_id="step-4-generate-checklist",
                    title="Generate Compliance Onboarding Checklist",
                    description="Write formatted SOC2 onboarding compliance checklist and equipment requisition report to sandbox.",
                    suggested_tool="file_operator",
                    risk_level="LOW",
                    requires_hitl=False,
                    verification_rule="Onboarding checklist markdown artifact created and validated."
                ),
                SOPStep(
                    step_id="step-5-send-welcome-email",
                    title="Send Welcome Email with Credentials and Schedule",
                    description="Draft and dispatch official welcome email to candidate with first-day schedule, manager intro, and portal link.",
                    suggested_tool="email_dispatcher",
                    risk_level="HIGH",
                    requires_hitl=True,
                    verification_rule="Email sent confirmation and message ID logged in audit ledger."
                )
            ]
        ),
        CompanySOP(
            id="SOP-FIN-004",
            title="Customer Refund and Ledger Reconciliation",
            department="Finance",
            trigger_keywords=["refund", "chargeback", "zendesk ticket", "stripe refund", "reconciliation"],
            description="Process customer refund request from Zendesk, cross-verify transaction logs in Stripe, calculate policy limits, execute refund (HITL if > $50), update ticket status, and append to Finance ledger.",
            required_inputs=["ticket_id", "customer_email", "charge_id", "refund_amount"],
            policy_notes="FIN-POL-04: Refunds > $50.00 USD require explicit Human-in-the-Loop Controller approval.",
            steps=[
                SOPStep(
                    step_id="step-1-fetch-ticket",
                    title="Retrieve Zendesk Support Ticket and Details",
                    description="Fetch customer refund request details, reason, customer email, and original invoice reference.",
                    suggested_tool="internal_api_tool",
                    risk_level="LOW",
                    requires_hitl=False,
                    verification_rule="Ticket details fetched and validated against customer identity."
                ),
                SOPStep(
                    step_id="step-2-verify-charge",
                    title="Verify Stripe Charge Status and Eligibility",
                    description="Query Stripe API for charge ID, ensure payment was captured and not already refunded.",
                    suggested_tool="stripe_refund_api",
                    risk_level="LOW",
                    requires_hitl=False,
                    verification_rule="Stripe charge status == 'succeeded' and refundable_amount >= requested_amount."
                ),
                SOPStep(
                    step_id="step-3-issue-refund",
                    title="Execute Stripe Refund with Guardrail Check",
                    description="Process the refund transaction. If amount > $50.00 USD, pause for HITL Controller approval.",
                    suggested_tool="stripe_refund_api",
                    risk_level="HIGH",
                    requires_hitl=True,
                    verification_rule="Stripe refund object created with status 'succeeded'."
                ),
                SOPStep(
                    step_id="step-4-update-ledger",
                    title="Reconcile Finance Ledger and Close Zendesk Ticket",
                    description="Append refund transaction entry with hash to Q3 Finance ledger and mark Zendesk ticket RESOLVED.",
                    suggested_tool="file_operator",
                    risk_level="MEDIUM",
                    requires_hitl=False,
                    verification_rule="Finance ledger CSV updated and Zendesk ticket status == 'RESOLVED'."
                )
            ]
        ),
        CompanySOP(
            id="SOP-SEC-012",
            title="SOC2 Access Audit and Offboarding Revocation",
            department="Security and IT",
            trigger_keywords=["offboard", "revoke", "soc2", "security audit", "access revocation", "terminate employee"],
            description="Conduct automated security offboarding: audit all active tokens, revoke Okta SSO, terminate GitHub organization access, lock AWS IAM keys, and output SOC2 cryptographic audit compliance report.",
            required_inputs=["employee_email", "employee_id", "departure_reason"],
            policy_notes="SEC-POL-09: Immediate revocation across all identity providers with zero residual permissions.",
            steps=[
                SOPStep(
                    step_id="step-1-audit-permissions",
                    title="Audit Active System Permissions and Session Tokens",
                    description="Scan Okta, GitHub, AWS IAM, and BambooHR for all active tokens and group memberships for the user.",
                    suggested_tool="okta_github_iam",
                    risk_level="LOW",
                    requires_hitl=False,
                    verification_rule="Complete list of active permissions compiled into audit trace."
                ),
                SOPStep(
                    step_id="step-2-revoke-access",
                    title="Revoke All SSO and Repository Access",
                    description="Execute simultaneous revocation in Okta and GitHub. Critical security step requiring HITL signoff.",
                    suggested_tool="okta_github_iam",
                    risk_level="HIGH",
                    requires_hitl=True,
                    verification_rule="Okta user status == 'DEACTIVATED' and GitHub member status == 'REMOVED'."
                ),
                SOPStep(
                    step_id="step-3-export-audit-cert",
                    title="Generate SOC2 Cryptographic Offboarding Proof",
                    description="Generate signed markdown and JSON certificate verifying timestamped revocation across all platforms.",
                    suggested_tool="file_operator",
                    risk_level="LOW",
                    requires_hitl=False,
                    verification_rule="SOC2 audit certificate generated and hash verified."
                )
            ]
        )
    ]
