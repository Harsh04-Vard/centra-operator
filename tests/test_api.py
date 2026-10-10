import unittest
from fastapi.testclient import TestClient
from centra_operator.web.app import app
from centra_operator.engine.state import TaskStatus

class TestFastAPIWebEndpoints(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_root_index_html(self):
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertIn("CentrAlign Operator", res.text)
        self.assertIn("Goal Dispatcher", res.text)

    def test_memory_endpoint(self):
        res = self.client.get("/api/memory")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("employees", data)
        self.assertIn("sops", data)
        self.assertTrue(len(data["sops"]) >= 3)

    def test_api_goal_and_hitl_cycle(self):
        # 1. Dispatch goal with HITL required
        res = self.client.post("/api/goals", json={
            "goal": "Process customer refund for Zendesk Ticket #8841 ($75.00)",
            "auto_approve": False
        })
        self.assertEqual(res.status_code, 200)
        state = res.json()
        self.assertEqual(state["status"], "AWAITING_APPROVAL")
        self.assertEqual(len(state["pending_approvals"]), 1)

        session_id = state["session_id"]
        approval_id = state["pending_approvals"][0]["id"]

        # 2. Submit approval
        res_decision = self.client.post(
            f"/api/session/{session_id}/approvals/{approval_id}/decision",
            json={"decision": "APPROVED", "feedback": "Signoff granted"}
        )
        self.assertEqual(res_decision.status_code, 200)
        resumed = res_decision.json()
        self.assertEqual(resumed["status"], "COMPLETED")

        # 3. Retrieve evidence
        res_ev = self.client.get(f"/api/evidence/{session_id}")
        self.assertEqual(res_ev.status_code, 200)
        ev_data = res_ev.json()
        self.assertEqual(ev_data["execution_status"], "COMPLETED")

if __name__ == "__main__":
    unittest.main()
