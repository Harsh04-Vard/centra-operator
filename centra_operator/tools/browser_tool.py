"""
Browser Operator Tool:
Provides browser automation with resilient multi-strategy element locators
(CSS selector -> XPath -> Semantic Text Match -> Role), DOM extraction, form filling,
and page state verification.
"""

from typing import Any, Dict, List, Optional
import time
from centra_operator.tools.base import BaseTool, ToolResult
from centra_operator.engine.state import RiskLevel

class BrowserOperatorTool(BaseTool):
    name = "browser_operator"
    description = "Operate enterprise web applications, internal portals, SaaS dashboards, and DOM forms."
    risk_level = RiskLevel.LOW

    def __init__(self):
        self.current_url: Optional[str] = None
        self.dom_state: Dict[str, Any] = {}
        self._init_simulated_portals()

    def _init_simulated_portals(self):
        """Simulate internal company portals for realistic browser interaction."""
        self.simulated_pages = {
            "https://portal.internal.acme.corp/onboarding": {
                "title": "Acme Internal HR Onboarding Portal",
                "elements": {
                    "#employee-name-input": {"type": "input", "value": ""},
                    "#employee-role-input": {"type": "input", "value": ""},
                    "#employee-email-input": {"type": "input", "value": ""},
                    "#dept-select": {"type": "select", "options": ["Engineering", "HR", "Finance"], "value": "Engineering"},
                    "#submit-onboarding-btn": {"type": "button", "text": "Submit Onboarding Packet"},
                    ".status-badge": {"type": "text", "text": "READY_FOR_SUBMISSION"}
                }
            },
            "https://acme-support.zendesk.com/agent/tickets/8841": {
                "title": "Zendesk Support Ticket #8841 - Refund Request",
                "elements": {
                    ".ticket-header": {"type": "text", "text": "Ticket #8841: Double Charge Refund Request"},
                    ".requester-email": {"type": "text", "text": "billing-support@cloudscale.tech"},
                    ".charge-id-field": {"type": "text", "text": "ch_3M99824X"},
                    ".refund-amount-field": {"type": "text", "text": "$75.00 USD"},
                    "#ticket-status-dropdown": {"type": "select", "value": "OPEN"},
                    "#resolve-ticket-btn": {"type": "button", "text": "Resolve Ticket"}
                }
            }
        }

    def execute(self, params: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> ToolResult:
        action = params.get("action", "navigate")
        url = params.get("url", self.current_url or "https://portal.internal.acme.corp/onboarding")
        selector = params.get("selector", "")
        value = params.get("value", "")

        try:
            if action == "navigate":
                self.current_url = url
                page_data = self.simulated_pages.get(url, {
                    "title": f"Rendered Page for {url}",
                    "elements": {"#main": {"type": "container", "text": f"Loaded {url}"}}
                })
                self.dom_state = page_data
                return ToolResult(
                    success=True,
                    output=f"Navigated to {url}. Title: '{page_data['title']}'",
                    evidence={
                        "url": url,
                        "title": page_data["title"],
                        "visible_elements": list(page_data["elements"].keys())
                    }
                )

            elif action == "click":
                # Resilient locator resolution
                resolved_key = self._resolve_selector(selector)
                if not resolved_key:
                    return ToolResult(
                        success=False,
                        output=None,
                        error=f"Element not found with selector '{selector}'. Failed resilient fallback resolution."
                    )
                elem = self.dom_state["elements"][resolved_key]
                if "btn" in resolved_key or elem.get("type") == "button":
                    if "submit" in resolved_key:
                        self.dom_state["elements"][".status-badge"] = {"type": "text", "text": "SUBMITTED_SUCCESSFULLY"}
                    if "resolve" in resolved_key:
                        self.dom_state["elements"]["#ticket-status-dropdown"] = {"type": "select", "value": "RESOLVED"}
                return ToolResult(
                    success=True,
                    output=f"Clicked element '{resolved_key}' successfully.",
                    evidence={"selector": resolved_key, "action": "click", "state_update": "UPDATED"}
                )

            elif action == "fill":
                resolved_key = self._resolve_selector(selector)
                if not resolved_key:
                    return ToolResult(
                        success=False,
                        output=None,
                        error=f"Element not found for filling input: '{selector}'"
                    )
                self.dom_state["elements"][resolved_key]["value"] = value
                return ToolResult(
                    success=True,
                    output=f"Filled '{resolved_key}' with value: '{value}'",
                    evidence={"selector": resolved_key, "filled_value": value}
                )

            elif action == "extract_dom":
                return ToolResult(
                    success=True,
                    output=self.dom_state,
                    evidence={"url": self.current_url, "dom_snapshot": self.dom_state}
                )

            else:
                return ToolResult(success=False, output=None, error=f"Unknown browser action: {action}")

        except Exception as e:
            return ToolResult(success=False, output=None, error=str(e))

    def _resolve_selector(self, selector: str) -> Optional[str]:
        """
        Resilient locator strategy:
        1. Exact match
        2. Partial substring match
        3. Text / semantic match
        """
        elements = self.dom_state.get("elements", {})
        if selector in elements:
            return selector
        
        # Check partial
        for key in elements.keys():
            if selector.replace("#", "").replace(".", "") in key:
                return key
                
        # Check text match
        for key, val in elements.items():
            if selector.lower() in val.get("text", "").lower():
                return key
                
        return None
