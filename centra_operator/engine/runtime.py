"""
Master Autonomous Company Operator Runtime:
Orchestrates the complete autonomous loop:
Goal -> Understand -> Ground -> Plan (DAG) -> Guardrail -> Execute -> Observe -> Adapt -> Verify -> Complete.
"""

import time
from typing import Optional, Callable, Dict, Any, List
from centra_operator.engine.state import ExecutionState, TaskNode, TaskStatus, TraceLog, ApprovalStatus
from centra_operator.planner.intent_parser import GLOBAL_INTENT_PARSER
from centra_operator.planner.dag_planner import GLOBAL_DAG_PLANNER
from centra_operator.planner.guardrails import GLOBAL_GUARDRAIL
from centra_operator.tools.registry import GLOBAL_TOOL_REGISTRY
from centra_operator.engine.recovery import GLOBAL_RECOVERY_ENGINE
from centra_operator.engine.hitl import GLOBAL_HITL_MANAGER
from centra_operator.verification.verifier import GLOBAL_VERIFIER
from centra_operator.verification.audit_evidence import GLOBAL_AUDIT_COMPILER
from centra_operator.memory.store import GLOBAL_MEMORY

class CentraOperatorRuntime:
    def __init__(self):
        self.intent_parser = GLOBAL_INTENT_PARSER
        self.planner = GLOBAL_DAG_PLANNER
        self.guardrail = GLOBAL_GUARDRAIL
        self.tool_registry = GLOBAL_TOOL_REGISTRY
        self.recovery_engine = GLOBAL_RECOVERY_ENGINE
        self.hitl_manager = GLOBAL_HITL_MANAGER
        self.verifier = GLOBAL_VERIFIER
        self.audit_compiler = GLOBAL_AUDIT_COMPILER
        self.memory = GLOBAL_MEMORY
        self.listeners: List[Callable[[TraceLog], None]] = []

    def add_trace_listener(self, listener: Callable[[TraceLog], None]):
        self.listeners.append(listener)

    def _notify(self, log_entry: TraceLog):
        for l in self.listeners:
            try:
                l(log_entry)
            except Exception:
                pass

    def initialize_session(self, user_goal: str) -> ExecutionState:
        """Stage 1 & 2: Understand, ground in memory, and compile verified Task DAG."""
        state = ExecutionState(user_goal=user_goal)
        state.status = TaskStatus.PLANNING

        # 1. Understand & Ground
        log1 = state.log("UNDERSTAND", f"Received user goal: '{user_goal}'. Searching organizational SOPs...")
        self._notify(log1)

        disambiguated_intent, matched_sop, entities = self.intent_parser.parse_intent(user_goal)
        state.disambiguated_intent = disambiguated_intent
        state.matched_sop_id = matched_sop.id
        state.working_memory["entities"] = entities

        log2 = state.log(
            "UNDERSTAND",
            f"Grounded goal in '{matched_sop.id}: {matched_sop.title}'. Disambiguated intent formulated.",
            payload={"entities": entities, "sop": matched_sop.id}
        )
        self._notify(log2)

        # 2. Plan Hierarchical DAG
        tasks = self.planner.build_plan(disambiguated_intent, matched_sop, entities)
        state.tasks = tasks
        state.status = TaskStatus.RUNNING

        log3 = state.log(
            "PLAN",
            f"Compiled execution DAG with {len(tasks)} verified task nodes and invariant contracts.",
            payload={"tasks_count": len(tasks)}
        )
        self._notify(log3)

        return state

    def step(self, state: ExecutionState, auto_approve_hitl: bool = False) -> ExecutionState:
        """
        Executes the next ready task node in the DAG.
        Handles guardrail checks, tool dispatch, observation, recovery, and verification.
        """
        if state.status in (TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.AWAITING_APPROVAL):
            return state

        # Find next pending task whose dependencies are satisfied
        ready_task: Optional[TaskNode] = None
        for t in state.tasks:
            if t.status == TaskStatus.PENDING:
                deps_satisfied = all(
                    state.get_task(dep_id).status == TaskStatus.COMPLETED
                    for dep_id in t.dependencies
                    if state.get_task(dep_id)
                )
                if deps_satisfied:
                    ready_task = t
                    break

        if not ready_task:
            # Check completion
            if all(t.status == TaskStatus.COMPLETED for t in state.tasks):
                state.status = TaskStatus.COMPLETED
                self.audit_compiler.compile_evidence_bundle(state)
                self.memory.record_learning(
                    session_id=state.session_id,
                    goal=state.user_goal,
                    outcome="COMPLETED_SUCCESSFULLY",
                    notes=f"All {len(state.tasks)} tasks completed and verified."
                )
                log_comp = state.log("COMPLETE", "Goal successfully achieved! All tasks verified. Audit evidence compiled.")
                self._notify(log_comp)
            elif any(t.status == TaskStatus.FAILED for t in state.tasks):
                state.status = TaskStatus.FAILED
                self.audit_compiler.compile_evidence_bundle(state)
                log_fail = state.log("COMPLETE", "Goal execution ended with failure in task DAG.", level="ERROR")
                self._notify(log_fail)
            return state

        state.active_task_id = ready_task.id
        ready_task.start_time = time.time()

        # Step 3: Guardrail & HITL Check (only if not already approved)
        is_already_approved = bool(ready_task.approval_request and ready_task.approval_request.status == ApprovalStatus.APPROVED)
        
        if ready_task.requires_approval and not is_already_approved:
            if auto_approve_hitl:
                if ready_task.approval_request:
                    ready_task.approval_request.status = ApprovalStatus.APPROVED
                log_auto = state.log("GUARDRAIL", f"Auto-approving high-risk task '{ready_task.title}' (Auto-signoff enabled)", task_id=ready_task.id)
                self._notify(log_auto)
            else:
                self.hitl_manager.pause_for_approval(state, ready_task)
                self._notify(state.trace_logs[-1])
                return state

        # Step 4: Execute Tool
        ready_task.status = TaskStatus.RUNNING
        log_exec = state.log("EXECUTE", f"Executing task: '{ready_task.title}' using tool '{ready_task.tool_name}'", task_id=ready_task.id, payload=ready_task.params)
        self._notify(log_exec)

        tool = self.tool_registry.get(ready_task.tool_name)
        if not tool:
            ready_task.status = TaskStatus.FAILED
            ready_task.error = f"Tool '{ready_task.tool_name}' not registered in environment."
            log_err = state.log("EXECUTE", ready_task.error, level="ERROR", task_id=ready_task.id)
            self._notify(log_err)
            return state

        result = tool.execute(ready_task.params, context=state.working_memory)
        ready_task.result = result.model_dump()

        # Step 5: Observe Output
        if result.success:
            log_obs = state.log("OBSERVE", f"Observation from {tool.name}: {result.output}", task_id=ready_task.id, payload=result.evidence)
            self._notify(log_obs)

            # Step 7: Invariant Verification
            ready_task.status = TaskStatus.VERIFYING
            is_verified, proof_text, proof_evidence = self.verifier.verify_task_outcome(ready_task, state.working_memory)
            
            if is_verified:
                ready_task.status = TaskStatus.COMPLETED
                ready_task.end_time = time.time()
                if result.artifacts:
                    ready_task.evidence_artifacts.extend(result.artifacts)
                log_ver = state.log("VERIFY", f"Invariant Verification PASSED: {proof_text}", level="SUCCESS", task_id=ready_task.id, payload=proof_evidence)
                self._notify(log_ver)
            else:
                log_ver_fail = state.log("VERIFY", f"Verification FAILED: {proof_text}", level="WARNING", task_id=ready_task.id)
                self._notify(log_ver_fail)
                self._handle_failure_and_recover(state, ready_task, f"Verification failure: {proof_text}")
        else:
            log_tool_err = state.log("OBSERVE", f"Execution error in {tool.name}: {result.error}", level="WARNING", task_id=ready_task.id)
            self._notify(log_tool_err)
            self._handle_failure_and_recover(state, ready_task, result.error or "Unknown tool failure")

        return state

    def _handle_failure_and_recover(self, state: ExecutionState, task: TaskNode, error: str):
        """Step 6: Self-Healing & Adaptive Recovery"""
        log_rec_start = state.log("RECOVER", f"Initiating Root Cause Analysis for error: '{error}'", level="WARNING", task_id=task.id)
        self._notify(log_rec_start)

        can_recover = self.recovery_engine.attempt_recovery(task, error, state.working_memory)
        if can_recover:
            log_rec_succ = state.log("RECOVER", f"Recovery strategy applied: {task.recovery_notes}. Task queued for retry.", level="INFO", task_id=task.id)
            self._notify(log_rec_succ)
            task.status = TaskStatus.PENDING
        else:
            task.status = TaskStatus.FAILED
            task.error = error
            log_rec_fail = state.log("RECOVER", f"Unrecoverable failure in task '{task.title}': {error}", level="ERROR", task_id=task.id)
            self._notify(log_rec_fail)

    def run_until_complete_or_blocked(self, state: ExecutionState, auto_approve_hitl: bool = False, max_steps: int = 25) -> ExecutionState:
        """Continuously steps runtime until goal is completed or paused for human approval."""
        step_count = 0
        while state.status == TaskStatus.RUNNING and step_count < max_steps:
            self.step(state, auto_approve_hitl=auto_approve_hitl)
            step_count += 1
        return state

GLOBAL_RUNTIME = CentraOperatorRuntime()
