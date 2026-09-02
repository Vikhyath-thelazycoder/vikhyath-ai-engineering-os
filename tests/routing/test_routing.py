import os
import unittest
import yaml

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))

class TestRouting(unittest.TestCase):
    def setUp(self):
        routing_path = os.path.join(ROOT_DIR, "config", "routing.yaml")
        priorities_path = os.path.join(ROOT_DIR, "config", "priorities.yaml")
        
        with open(routing_path, "r", encoding="utf-8") as f:
            self.routing = yaml.safe_load(f)
            
        with open(priorities_path, "r", encoding="utf-8") as f:
            self.priorities = yaml.safe_load(f)

    def test_simple_bugfix_routing(self):
        rule = self.routing["routing"]["simple-bugfix"]
        self.assertIn("ecc", rule["activate"])
        self.assertNotIn("graphify", rule["activate"])
        self.assertNotIn("ponytail", rule["activate"])

    def test_complex_codebase_routing(self):
        rule = self.routing["routing"]["complex-codebase"]
        self.assertIn("ecc", rule["activate"])
        self.assertIn("graphify", rule["activate"])

    def test_security_task_routing(self):
        rule = self.routing["routing"]["security-task"]
        self.assertIn("ecc", rule["activate"])
        self.assertIn("addy", rule["activate"])

    def test_simplicity_review_routing(self):
        rule = self.routing["routing"]["simplicity-review"]
        self.assertEqual(rule["activate"], ["ponytail"])

    def test_review_release_routing(self):
        rule = self.routing["routing"]["review-release"]
        self.assertIn("ecc", rule["activate"])
        self.assertIn("gstack", rule["activate"])

    def test_conflict_hierarchy(self):
        hierarchy = self.priorities["conflict_hierarchy"]
        levels = [item["source"] for item in hierarchy]
        self.assertEqual(levels[0], "user-requirements")
        self.assertEqual(levels[1], "project-security")
        self.assertEqual(levels[2], "project-architecture")
        self.assertEqual(levels[3], "ecc")

if __name__ == "__main__":
    unittest.main()
