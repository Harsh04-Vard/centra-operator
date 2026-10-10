"""
Central Tool Registry:
Dynamic tool discovery, capability lookup, and execution dispatcher.
"""

from typing import Dict, List, Optional
from centra_operator.tools.base import BaseTool
from centra_operator.tools.file_tool import FileOperatorTool
from centra_operator.tools.browser_tool import BrowserOperatorTool
from centra_operator.tools.internal_api_tool import InternalApiTool
from centra_operator.tools.communication_tool import EmailDispatcherTool, SlackNotifierTool
from centra_operator.tools.cli_tool import ShellTool

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
        self._register_default_tools()

    def _register_default_tools(self):
        file_tool = FileOperatorTool()
        browser_tool = BrowserOperatorTool()
        internal_api = InternalApiTool()
        email_tool = EmailDispatcherTool()
        slack_tool = SlackNotifierTool()
        shell_tool = ShellTool()

        self.register(file_tool)
        self.register(browser_tool)
        self.register(internal_api)
        self.register(email_tool)
        self.register(slack_tool)
        self.register(shell_tool)

        # Aliases for SOP compatibility
        self._tools["bamboohr_api"] = internal_api
        self._tools["stripe_refund_api"] = internal_api
        self._tools["okta_github_iam"] = internal_api

    def register(self, tool: BaseTool):
        self._tools[tool.name] = tool

    def get(self, tool_name: str) -> Optional[BaseTool]:
        return self._tools.get(tool_name)

    def list_tools(self) -> List[Dict[str, str]]:
        return [
            {"name": name, "description": tool.description, "risk_level": tool.risk_level.value}
            for name, tool in self._tools.items()
        ]

GLOBAL_TOOL_REGISTRY = ToolRegistry()
