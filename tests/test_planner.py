import unittest
from centra_operator.planner.intent_parser import GLOBAL_INTENT_PARSER
from centra_operator.planner.dag_planner import GLOBAL_DAG_PLANNER

class TestPlanner(unittest.TestCase):
    def test_onboarding_intent_resolution(self):
        goal = "Onboard Alex Morgan as Senior Frontend Engineer starting Monday"
        disambiguated, sop, entities = GLOBAL_INTENT_PARSER.parse_intent(goal)
        
        self.assertEqual(sop.id, "SOP-HR-001")
        self.assertIn("Alex Morgan", disambiguated)
        self.assertEqual(entities.get("role"), "Senior Frontend Engineer")

        tasks = GLOBAL_DAG_PLANNER.build_plan(disambiguated, sop, entities)
        self.assertEqual(len(tasks), 5)
        self.assertEqual(tasks[0].tool_name, "file_operator")
        self.assertTrue(any(t.requires_approval for t in tasks))

    def test_refund_intent_resolution(self):
        goal = "Process refund for Zendesk Ticket #8841 customer requested double charge"
        disambiguated, sop, entities = GLOBAL_INTENT_PARSER.parse_intent(goal)
        
        self.assertEqual(sop.id, "SOP-FIN-004")
        self.assertIn("8841", disambiguated)

        tasks = GLOBAL_DAG_PLANNER.build_plan(disambiguated, sop, entities)
        self.assertEqual(len(tasks), 4)
        refund_task = [t for t in tasks if "issue-refund" in t.id][0]
        self.assertTrue(refund_task.requires_approval)
        self.assertEqual(refund_task.risk_level.value, "HIGH")

if __name__ == "__main__":
    unittest.main()
