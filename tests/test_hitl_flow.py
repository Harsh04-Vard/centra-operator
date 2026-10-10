import unittest
from centra_operator.engine.runtime import GLOBAL_RUNTIME
from centra_operator.engine.state import TaskStatus, ApprovalStatus

class TestHITLFlow(unittest.TestCase):
    def test_hitl_pause_and_approval(self):
        goal = "Onboard Alex Morgan as Senior Frontend Engineer"
        state = GLOBAL_RUNTIME.initialize_session(goal)
        
        # Step until paused for HITL
        state = GLOBAL_RUNTIME.run_until_complete_or_blocked(state, auto_approve_hitl=False)
        self.assertEqual(state.status, TaskStatus.AWAITING_APPROVAL)
        self.assertEqual(len(state.pending_approvals), 1)

        approval = state.pending_approvals[0]
        self.assertEqual(approval.risk_level.value, "HIGH")

        # Submit human approval
        res = GLOBAL_RUNTIME.hitl_manager.submit_decision(state, approval.id, "APPROVED", feedback="Approved by VP HR")
        self.assertTrue(res)
        self.assertEqual(len(state.pending_approvals), 0)

        # Continue stepping to completion
        state = GLOBAL_RUNTIME.run_until_complete_or_blocked(state)
        self.assertEqual(state.status, TaskStatus.COMPLETED)

    def test_hitl_rejection(self):
        goal = "Process Zendesk #8841 refund for $75.00"
        state = GLOBAL_RUNTIME.initialize_session(goal)
        state = GLOBAL_RUNTIME.run_until_complete_or_blocked(state, auto_approve_hitl=False)
        
        self.assertEqual(state.status, TaskStatus.AWAITING_APPROVAL)
        approval = state.pending_approvals[0]
        
        # Human rejects the dangerous action
        res = GLOBAL_RUNTIME.hitl_manager.submit_decision(state, approval.id, "REJECTED", feedback="Suspected fraudulent claim")
        self.assertTrue(res)
        
        # Paused task is marked failed
        rejected_task = state.get_task(approval.task_id)
        self.assertEqual(rejected_task.status, TaskStatus.FAILED)

if __name__ == "__main__":
    unittest.main()
