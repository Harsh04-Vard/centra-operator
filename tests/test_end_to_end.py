import unittest
from centra_operator.engine.runtime import GLOBAL_RUNTIME
from centra_operator.engine.state import TaskStatus

class TestEndToEnd(unittest.TestCase):
    def test_e2e_hr_onboarding(self):
        goal = "Onboard Alex Morgan as Senior Frontend Engineer starting Monday"
        state = GLOBAL_RUNTIME.initialize_session(goal)
        
        # Step through until completed with auto-approve
        state = GLOBAL_RUNTIME.run_until_complete_or_blocked(state, auto_approve_hitl=True)
        self.assertEqual(state.status, TaskStatus.COMPLETED)
        self.assertEqual(len(state.tasks), 5)
        self.assertTrue(all(t.status == TaskStatus.COMPLETED for t in state.tasks))
        self.assertIsNotNone(state.evidence_summary)

    def test_e2e_finance_refund(self):
        goal = "Process customer refund request for Zendesk Ticket #8841 ($75.00)"
        state = GLOBAL_RUNTIME.initialize_session(goal)
        state = GLOBAL_RUNTIME.run_until_complete_or_blocked(state, auto_approve_hitl=True)
        self.assertEqual(state.status, TaskStatus.COMPLETED)
        self.assertEqual(len(state.tasks), 4)
        self.assertTrue(all(t.status == TaskStatus.COMPLETED for t in state.tasks))

    def test_e2e_soc2_offboarding(self):
        goal = "Execute SOC2 access revocation for Alex Morgan EMP-1092"
        state = GLOBAL_RUNTIME.initialize_session(goal)
        state = GLOBAL_RUNTIME.run_until_complete_or_blocked(state, auto_approve_hitl=True)
        self.assertEqual(state.status, TaskStatus.COMPLETED)
        self.assertEqual(len(state.tasks), 3)

if __name__ == "__main__":
    unittest.main()
