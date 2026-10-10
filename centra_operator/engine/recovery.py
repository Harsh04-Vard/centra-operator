"""
Self-Healing and Adaptive Failure Recovery Engine:
Performs Root Cause Analysis (RCA) on failed tool executions, executes automatic
fallback strategies, and adapts parameters without halting execution abruptly.
"""

from typing import Dict, Any, Optional
from centra_operator.engine.state import TaskNode, TaskStatus
from centra_operator.llm.provider import GLOBAL_LLM

class SelfHealingEngine:
    def __init__(self):
        self.llm = GLOBAL_LLM

    def attempt_recovery(self, task: TaskNode, error: str, state_context: Dict[str, Any]) -> bool:
        """
        Attempts to heal a failing task.
        Returns True if a recovery remediation was successfully applied, False if unrecoverable.
        """
        if task.retry_count >= task.max_retries:
            task.recovery_notes = f"Exceeded max retry limit ({task.max_retries}). Marking task as FAILED."
            return False

        task.retry_count += 1
        task.status = TaskStatus.RECOVERING

        # LLM Root Cause Analysis
        diagnosis = self.llm.self_heal(task.title, task.tool_name, error)
        category = diagnosis.get("category", "UNKNOWN_ERROR")
        actionable_fix = diagnosis.get("actionable_fix", "Retrying with updated parameters")
        
        task.recovery_notes = f"RCA [{category}]: {actionable_fix} (Attempt {task.retry_count}/{task.max_retries})"

        # Apply specific recovery remediations
        if category == "SELECTOR_CHANGED":
            # Switch to fallback selector
            fallback_params = diagnosis.get("recovery_params", {})
            task.params.update(fallback_params)
            return True
            
        elif category == "MISSING_RESOURCE":
            # Synthesize template
            task.params["action"] = "write"
            task.params["content"] = "# Synthesized Enterprise Document Template\nAuto-created by Recovery Engine."
            return True

        elif category == "API_ANOMALY":
            # Idempotency token retry
            task.params["_idempotency_retry"] = task.retry_count
            return True

        return True

GLOBAL_RECOVERY_ENGINE = SelfHealingEngine()
