"""
State models and data structures for the Agent Execution Engine.
Encapsulates Task Nodes, DAG status, Execution Traces, and Human-in-the-Loop payloads.
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
import time
import uuid

class TaskStatus(str, Enum):
    PENDING = "PENDING"
    PLANNING = "PLANNING"
    RUNNING = "RUNNING"
    AWAITING_APPROVAL = "AWAITING_APPROVAL"
    RECOVERING = "RECOVERING"
    VERIFYING = "VERIFYING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"

class RiskLevel(str, Enum):
    LOW = "LOW"          # Read-only operations, internal scratchpad computations
    MEDIUM = "MEDIUM"    # Modifying internal state/staging data, non-destructive API updates
    HIGH = "HIGH"        # Financial transactions, external emails, production deletions, IAM admin grants
    CRITICAL = "CRITICAL"# Direct database schema drops, fund transfers > policy threshold

class ApprovalStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    MODIFIED = "MODIFIED"

class ApprovalRequest(BaseModel):
    id: str = Field(default_factory=lambda: f"hitl-{uuid.uuid4().hex[:8]}")
    task_id: str
    task_description: str
    risk_level: RiskLevel
    reason: str
    proposed_action: str
    tool_name: str
    tool_params: Dict[str, Any]
    blast_radius: str
    status: ApprovalStatus = ApprovalStatus.PENDING
    human_feedback: Optional[str] = None
    modified_params: Optional[Dict[str, Any]] = None
    timestamp: float = Field(default_factory=time.time)

class VerificationContract(BaseModel):
    """Contract defining invariant checks that must pass for a task to be marked successful."""
    target_system: str
    expected_state: Dict[str, Any]
    verification_query: str
    proof_type: str = "INVARIANT_CHECK"  # INVARIANT_CHECK, CHECKSUM, HTTP_200, DB_RECORD_EXISTS

class TaskNode(BaseModel):
    """A discrete node in the Hierarchical Task DAG."""
    id: str = Field(default_factory=lambda: f"task-{uuid.uuid4().hex[:8]}")
    title: str
    description: str
    tool_name: str
    params: Dict[str, Any] = Field(default_factory=dict)
    dependencies: List[str] = Field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    risk_level: RiskLevel = RiskLevel.LOW
    requires_approval: bool = False
    approval_request: Optional[ApprovalRequest] = None
    verification_contract: Optional[VerificationContract] = None
    retry_count: int = 0
    max_retries: int = 3
    result: Optional[Any] = None
    error: Optional[str] = None
    recovery_notes: Optional[str] = None
    evidence_artifacts: List[str] = Field(default_factory=list)
    start_time: Optional[float] = None
    end_time: Optional[float] = None

class TraceLog(BaseModel):
    timestamp: float = Field(default_factory=time.time)
    stage: str  # UNDERSTAND, PLAN, GUARDRAIL, EXECUTE, OBSERVE, RECOVER, VERIFY, COMPLETE
    task_id: Optional[str] = None
    level: str = "INFO"  # INFO, WARNING, ERROR, SUCCESS, HITL
    message: str
    payload: Optional[Dict[str, Any]] = None

class ExecutionState(BaseModel):
    """Global runtime execution state for an autonomous enterprise goal."""
    session_id: str = Field(default_factory=lambda: f"sess-{uuid.uuid4().hex[:8]}")
    user_goal: str
    disambiguated_intent: Optional[str] = None
    matched_sop_id: Optional[str] = None
    tasks: List[TaskNode] = Field(default_factory=list)
    active_task_id: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    pending_approvals: List[ApprovalRequest] = Field(default_factory=list)
    working_memory: Dict[str, Any] = Field(default_factory=dict)
    trace_logs: List[TraceLog] = Field(default_factory=list)
    evidence_summary: Optional[Dict[str, Any]] = None
    created_at: float = Field(default_factory=time.time)
    updated_at: float = Field(default_factory=time.time)

    def log(self, stage: str, message: str, level: str = "INFO", task_id: Optional[str] = None, payload: Optional[Dict[str, Any]] = None):
        entry = TraceLog(
            stage=stage,
            level=level,
            message=message,
            task_id=task_id,
            payload=payload or {}
        )
        self.trace_logs.append(entry)
        self.updated_at = time.time()
        return entry

    def get_task(self, task_id: str) -> Optional[TaskNode]:
        for t in self.tasks:
            if t.id == task_id:
                return t
        return None
