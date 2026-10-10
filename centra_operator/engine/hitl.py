"""
Human-In-The-Loop (HITL) Manager:
Handles asynchronous pausing, approval queuing, feedback injection,
parameter overriding, and execution resumption.
"""

from typing import Optional, Dict, Any, List
from centra_operator.engine.state import ExecutionState, TaskNode, TaskStatus, ApprovalStatus, ApprovalRequest

class HITLManager:
    def __init__(self):
        pass

    def pause_for_approval(self, state: ExecutionState, task: TaskNode):
        """Pauses runtime state and registers pending approval."""
        if not task.approval_request:
            return

        task.status = TaskStatus.AWAITING_APPROVAL
        state.status = TaskStatus.AWAITING_APPROVAL
        state.active_task_id = task.id
        
        if task.approval_request not in state.pending_approvals:
            state.pending_approvals.append(task.approval_request)

        state.log(
            stage="GUARDRAIL",
            level="HITL",
            message=f"Task '{task.title}' paused for Human Approval. Reason: {task.approval_request.reason}",
            task_id=task.id,
            payload=task.approval_request.model_dump()
        )

    def submit_decision(self, state: ExecutionState, approval_id: str, decision: str, feedback: Optional[str] = None, modified_params: Optional[Dict[str, Any]] = None) -> bool:
        """Applies human decision (APPROVED, REJECTED, MODIFIED) to pending approval."""
        req: Optional[ApprovalRequest] = None
        for r in state.pending_approvals:
            if r.id == approval_id:
                req = r
                break

        if not req:
            return False

        task = state.get_task(req.task_id)
        if not task:
            return False

        if decision.upper() == "APPROVED":
            req.status = ApprovalStatus.APPROVED
            req.human_feedback = feedback
            task.status = TaskStatus.PENDING
            state.log(stage="GUARDRAIL", level="SUCCESS", message=f"Approval granted by Human Operator. Notes: {feedback or 'None'}", task_id=task.id)
            
        elif decision.upper() == "REJECTED":
            req.status = ApprovalStatus.REJECTED
            req.human_feedback = feedback
            task.status = TaskStatus.FAILED
            task.error = f"Rejected by Human Operator: {feedback or 'Action denied'}"
            state.log(stage="GUARDRAIL", level="WARNING", message=f"Approval REJECTED by Human Operator. Reason: {feedback}", task_id=task.id)

        elif decision.upper() == "MODIFIED":
            req.status = ApprovalStatus.MODIFIED
            req.human_feedback = feedback
            req.modified_params = modified_params
            if modified_params:
                task.params.update(modified_params)
            task.status = TaskStatus.PENDING
            state.log(stage="GUARDRAIL", level="INFO", message=f"Parameters modified by Human Operator. Updated: {modified_params}", task_id=task.id)

        # Remove from pending queue
        state.pending_approvals = [r for r in state.pending_approvals if r.id != approval_id]
        
        if not state.pending_approvals:
            state.status = TaskStatus.RUNNING

        return True

GLOBAL_HITL_MANAGER = HITLManager()
