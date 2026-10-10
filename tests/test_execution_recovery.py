import unittest
from centra_operator.tools.browser_tool import BrowserOperatorTool
from centra_operator.engine.recovery import GLOBAL_RECOVERY_ENGINE
from centra_operator.engine.state import TaskNode, TaskStatus

class TestExecutionRecovery(unittest.TestCase):
    def test_resilient_selector_fallback(self):
        tool = BrowserOperatorTool()
        tool.execute({"action": "navigate", "url": "https://portal.internal.acme.corp/onboarding"})
        
        # Click with fuzzy text instead of direct ID
        res = tool.execute({"action": "click", "selector": "Submit Onboarding"})
        self.assertTrue(res.success)
        self.assertEqual(res.evidence.get("action"), "click")

    def test_self_healing_engine_rca(self):
        task = TaskNode(
            title="Submit Onboarding Form",
            description="Submit web form",
            tool_name="browser_operator",
            params={"action": "click", "selector": "#invalid-outdated-button"}
        )
        
        recovered = GLOBAL_RECOVERY_ENGINE.attempt_recovery(task, "Element not found with selector '#invalid-outdated-button'", {})
        self.assertTrue(recovered)
        self.assertEqual(task.status, TaskStatus.RECOVERING)
        self.assertEqual(task.retry_count, 1)
        self.assertIn("RCA [SELECTOR_CHANGED]", task.recovery_notes)

if __name__ == "__main__":
    unittest.main()
