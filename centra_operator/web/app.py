"""
FastAPI Enterprise Mission Control Server:
Provides REST API and Server-Sent Events (SSE) for real-time autonomous operator control,
DAG visualization, HITL approval handling, and evidence inspection.
"""

from typing import Dict, Any, Optional
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from centra_operator.engine.runtime import GLOBAL_RUNTIME
from centra_operator.engine.state import ExecutionState, TaskStatus
from centra_operator.memory.store import GLOBAL_MEMORY

app = FastAPI(title="CentrAlign Autonomous Company Operator", version="1.0.0")

# Store active sessions in memory
SESSIONS: Dict[str, ExecutionState] = {}

class GoalRequest(BaseModel):
    goal: str
    auto_approve: bool = False

class DecisionRequest(BaseModel):
    decision: str  # APPROVED, REJECTED, MODIFIED
    feedback: Optional[str] = None
    modified_params: Optional[Dict[str, Any]] = None

@app.post("/api/goals")
async def start_goal(req: GoalRequest):
    """Initializes and kicks off an autonomous goal execution."""
    state = GLOBAL_RUNTIME.initialize_session(req.goal)
    SESSIONS[state.session_id] = state
    
    # Run synchronously until complete or paused for HITL
    GLOBAL_RUNTIME.run_until_complete_or_blocked(state, auto_approve_hitl=req.auto_approve)
    return state.model_dump()

@app.get("/api/session/{session_id}")
async def get_session(session_id: str):
    state = SESSIONS.get(session_id)
    if not state:
        raise HTTPException(status_code=404, detail="Session not found")
    return state.model_dump()

@app.post("/api/session/{session_id}/step")
async def step_session(session_id: str):
    """Manually step the session forward."""
    state = SESSIONS.get(session_id)
    if not state:
        raise HTTPException(status_code=404, detail="Session not found")
    
    GLOBAL_RUNTIME.step(state)
    return state.model_dump()

@app.post("/api/session/{session_id}/approvals/{approval_id}/decision")
async def submit_approval_decision(session_id: str, approval_id: str, req: DecisionRequest):
    """Submits a human decision on a paused high-risk task and resumes execution."""
    state = SESSIONS.get(session_id)
    if not state:
        raise HTTPException(status_code=404, detail="Session not found")
    
    success = GLOBAL_RUNTIME.hitl_manager.submit_decision(
        state=state,
        approval_id=approval_id,
        decision=req.decision,
        feedback=req.feedback,
        modified_params=req.modified_params
    )
    
    if not success:
        raise HTTPException(status_code=400, detail="Failed to resolve approval")
        
    # Resume execution automatically after approval
    if state.status == TaskStatus.RUNNING:
        GLOBAL_RUNTIME.run_until_complete_or_blocked(state)
        
    return state.model_dump()

@app.get("/api/memory")
async def get_memory():
    """Retrieve organizational context, policies, and SOP knowledge base."""
    return {
        "company_name": GLOBAL_MEMORY.org_graph.company_name,
        "employees": [e.model_dump() for e in GLOBAL_MEMORY.org_graph.employees.values()],
        "tool_policies": [p.model_dump() for p in GLOBAL_MEMORY.org_graph.tool_policies.values()],
        "compliance_rules": GLOBAL_MEMORY.org_graph.compliance_rules,
        "sops": [s.model_dump() for s in GLOBAL_MEMORY.sops.values()]
    }

@app.get("/api/evidence/{session_id}")
async def get_evidence(session_id: str):
    state = SESSIONS.get(session_id)
    if not state or not state.evidence_summary:
        raise HTTPException(status_code=404, detail="Evidence not ready or session not found")
    return state.evidence_summary

# Mount static frontend assets
static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_path = static_dir / "index.html"
    return HTMLResponse(content=index_path.read_text(encoding="utf-8"))
