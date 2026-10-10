"""
CLI and System Shell Operator Tool:
Executes local diagnostic scripts, data verification commands, and system sanity checks.
"""

import subprocess
from typing import Any, Dict, Optional
from centra_operator.tools.base import BaseTool, ToolResult
from centra_operator.engine.state import RiskLevel
from centra_operator.config import CONFIG

class ShellTool(BaseTool):
    name = "cli_shell"
    description = "Execute local system commands and automated verification scripts in sandbox."
    risk_level = RiskLevel.MEDIUM

    def execute(self, params: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> ToolResult:
        command = params.get("command", "")
        if not command:
            return ToolResult(success=False, output=None, error="Empty command supplied")

        # Security check: prevent destructive root commands
        disallowed = ["rm -rf /", "format", "mkfs", ":(){ :|:& };:"]
        if any(d in command.lower() for d in disallowed):
            return ToolResult(
                success=False,
                output=None,
                error="Security violation: command contains prohibited destructive primitives."
            )

        try:
            res = subprocess.run(
                command,
                shell=True,
                cwd=str(CONFIG.sandbox_dir),
                capture_output=True,
                text=True,
                timeout=CONFIG.max_tool_execution_timeout_sec
            )
            return ToolResult(
                success=(res.returncode == 0),
                output=res.stdout.strip() if res.returncode == 0 else res.stderr.strip(),
                evidence={
                    "command": command,
                    "exit_code": res.returncode,
                    "stdout": res.stdout.strip(),
                    "stderr": res.stderr.strip()
                },
                error=res.stderr.strip() if res.returncode != 0 else None
            )
        except Exception as e:
            return ToolResult(success=False, output=None, error=str(e))
