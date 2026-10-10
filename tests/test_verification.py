import unittest
from centra_operator.verification.verifier import GLOBAL_VERIFIER
from centra_operator.verification.audit_evidence import GLOBAL_AUDIT_COMPILER
from centra_operator.engine.state import TaskNode, VerificationContract, ExecutionState, TaskStatus

class TestVerification(unittest.TestCase):
    def test_invariant_verifier_file(self):
        task = TaskNode(
            title="Write Compliance Report",
            description="Write compliance doc",
            tool_name="file_operator",
            verification_contract=VerificationContract(
                target_system="file_operator",
                expected_state={"status": "VERIFIED_OK"},
                verification_query="SHA256 checksum recorded"
            ),
            result={
                "success": True,
                "evidence": {
                    "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                    "path": "workspace_sandbox/evidence/report.md"
                }
            }
        )

        is_verified, proof, ev = GLOBAL_VERIFIER.verify_task_outcome(task, {})
        self.assertTrue(is_verified)
        self.assertIn("SHA256 verified", proof)

    def test_audit_evidence_compilation(self):
        state = ExecutionState(user_goal="Onboard candidate Alex")
        state.status = TaskStatus.COMPLETED
        state.tasks = [
            TaskNode(title="Task 1", description="desc", tool_name="file_operator", status=TaskStatus.COMPLETED)
        ]
        bundle = GLOBAL_AUDIT_COMPILER.compile_evidence_bundle(state)
        
        self.assertEqual(bundle["execution_status"], "COMPLETED")
        self.assertTrue(bundle.get("report_path_md"))
        self.assertTrue(bundle.get("report_path_json"))

if __name__ == "__main__":
    unittest.main()
