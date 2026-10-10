"""
Organizational Memory Graph:
Represents company structure, personnel, roles, permissions matrix, access policies, and tools.
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

class EmployeeRecord(BaseModel):
    id: str
    name: str
    email: str
    role: str
    department: str
    manager_email: Optional[str] = None
    permissions: List[str] = Field(default_factory=list)
    status: str = "ACTIVE"  # ACTIVE, PENDING_ONBOARDING, OFFBOARDED

class ToolAccessPolicy(BaseModel):
    tool_name: str
    required_role: str
    requires_hitl_approval: bool
    risk_level: str
    policy_description: str

class OrgMemoryGraph(BaseModel):
    company_name: str = "Acme Enterprise Technologies"
    departments: List[str] = Field(default_factory=lambda: ["Engineering", "Human Resources", "Finance", "Security and IT", "Customer Success"])
    employees: Dict[str, EmployeeRecord] = Field(default_factory=dict)
    tool_policies: Dict[str, ToolAccessPolicy] = Field(default_factory=dict)
    system_endpoints: Dict[str, str] = Field(default_factory=dict)
    compliance_rules: List[str] = Field(default_factory=list)

    @classmethod
    def create_default(cls) -> "OrgMemoryGraph":
        graph = cls()
        
        # Seed Employees
        graph.employees = {
            "alex.m@acme.corp": EmployeeRecord(
                id="EMP-1092",
                name="Alex Morgan",
                email="alex.m@acme.corp",
                role="Senior Frontend Engineer",
                department="Engineering",
                manager_email="sarah.cto@acme.corp",
                permissions=["github.read", "slack.general"],
                status="PENDING_ONBOARDING"
            ),
            "sarah.cto@acme.corp": EmployeeRecord(
                id="EMP-0004",
                name="Sarah Lin",
                email="sarah.cto@acme.corp",
                role="VP of Engineering",
                department="Engineering",
                permissions=["admin", "github.admin", "aws.admin"],
                status="ACTIVE"
            ),
            "jordan.hr@acme.corp": EmployeeRecord(
                id="EMP-0012",
                name="Jordan Vance",
                email="jordan.hr@acme.corp",
                role="Head of People",
                department="Human Resources",
                permissions=["bamboohr.admin", "payroll.editor"],
                status="ACTIVE"
            ),
            "elena.fin@acme.corp": EmployeeRecord(
                id="EMP-0023",
                name="Elena Rostova",
                email="elena.fin@acme.corp",
                role="Finance Controller",
                department="Finance",
                permissions=["stripe.admin", "ledger.write"],
                status="ACTIVE"
            )
        }
        
        # Seed Tool Policies
        graph.tool_policies = {
            "browser_operator": ToolAccessPolicy(
                tool_name="browser_operator",
                required_role="Any",
                requires_hitl_approval=False,
                risk_level="LOW",
                policy_description="Automate web navigation and internal portal interfaces."
            ),
            "file_operator": ToolAccessPolicy(
                tool_name="file_operator",
                required_role="Any",
                requires_hitl_approval=False,
                risk_level="LOW",
                policy_description="Read and write workspace sandbox files, reports, and audit certificates."
            ),
            "bamboohr_api": ToolAccessPolicy(
                tool_name="bamboohr_api",
                required_role="Human Resources",
                requires_hitl_approval=False,
                risk_level="MEDIUM",
                policy_description="Create employee records and update employment status in HRIS."
            ),
            "stripe_refund_api": ToolAccessPolicy(
                tool_name="stripe_refund_api",
                required_role="Finance",
                requires_hitl_approval=True,
                risk_level="HIGH",
                policy_description="Issue refunds to customers; requires HITL approval if amount > $50.00 USD."
            ),
            "okta_github_iam": ToolAccessPolicy(
                tool_name="okta_github_iam",
                required_role="Engineering / IT",
                requires_hitl_approval=False,
                risk_level="MEDIUM",
                policy_description="Grant repo and SSO application permissions to authorized personnel."
            ),
            "email_dispatcher": ToolAccessPolicy(
                tool_name="email_dispatcher",
                required_role="Any",
                requires_hitl_approval=True,
                risk_level="HIGH",
                policy_description="Send external communications to candidates or clients."
            )
        }
        
        # Seed System Endpoints
        graph.system_endpoints = {
            "bamboohr": "https://acme.bamboohr.com/api/v1",
            "stripe": "https://api.stripe.com/v1",
            "okta": "https://acme.okta.com/api/v1",
            "github": "https://api.github.com/orgs/acme-corp",
            "internal_portal": "https://portal.internal.acme.corp/onboarding",
            "zendesk": "https://acme-support.zendesk.com/api/v2"
        }
        
        # Compliance Rules
        graph.compliance_rules = [
            "SOC2-CC6.1: All new engineer onboarding must require GitHub 2FA and branch protection permissions.",
            "FIN-POL-04: Any customer refund exceeding $50.00 USD requires explicit controller HITL signoff.",
            "HR-POL-02: Offer letters and tax documents must be verified and checksummed before payroll activation.",
            "SEC-POL-09: Offboarded employee credentials across Okta, GitHub, and AWS must be revoked within 15 minutes."
        ]
        
        return graph
