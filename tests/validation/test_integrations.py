import glob
import os
import re
import unittest
import yaml

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))

class TestIntegrations(unittest.TestCase):
    def test_all_integrations_present_and_valid(self):
        expected_integrations = {
            "ecc",
            "graphify",
            "unlazy",
            "addy",
            "agency",
            "gstack",
            "opendesign",
            "ponytail",
            "karpathy"
        }
        
        integration_files = glob.glob(os.path.join(ROOT_DIR, "integrations", "*.yaml"))
        found_integrations = set()
        hex_sha_regex = re.compile(r'^[0-9a-f]{40}$')
        
        for file_path in integration_files:
            name = os.path.splitext(os.path.basename(file_path))[0]
            found_integrations.add(name)
            
            with open(file_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                
            self.assertIn("source", data, f"{name}.yaml missing source")
            self.assertIn("role", data, f"{name}.yaml missing role")
            self.assertIn("ref", data, f"{name}.yaml missing ref")
            self.assertTrue(hex_sha_regex.match(data["ref"]), f"{name}.yaml ref is not a 40-char hex SHA")
            self.assertIn("integration_type", data, f"{name}.yaml missing integration_type")
            self.assertIn("hosts", data, f"{name}.yaml missing hosts")
            
        self.assertEqual(expected_integrations, found_integrations, "Mismatch in expected integrations")

    def test_skills_frontmatter(self):
        skill_files = glob.glob(os.path.join(ROOT_DIR, "skills", "*", "SKILL.md"))
        self.assertGreaterEqual(len(skill_files), 5, "Expected at least 5 core skills")
        
        for skill_file in skill_files:
            with open(skill_file, "r", encoding="utf-8") as f:
                content = f.read()
                
            self.assertTrue(content.startswith("---"), f"{skill_file} missing frontmatter delimiter")
            self.assertIn("name:", content, f"{skill_file} missing name in frontmatter")
            self.assertIn("description:", content, f"{skill_file} missing description in frontmatter")

    def test_ci_workflow_valid_yaml(self):
        ci_path = os.path.join(ROOT_DIR, ".github", "workflows", "ci.yml")
        self.assertTrue(os.path.isfile(ci_path), ".github/workflows/ci.yml missing")
        with open(ci_path, "r", encoding="utf-8") as f:
            ci = yaml.safe_load(f)
        self.assertIn("name", ci)
        self.assertIn("jobs", ci)

    def test_community_health_files(self):
        expected_files = [
            "CONTRIBUTING.md",
            "SECURITY.md",
            "CODE_OF_CONDUCT.md",
            os.path.join(".github", "pull_request_template.md"),
            os.path.join(".github", "ISSUE_TEMPLATE", "bug_report.md"),
            os.path.join(".github", "ISSUE_TEMPLATE", "feature_request.md"),
            os.path.join(".github", "ISSUE_TEMPLATE", "capability_proposal.md"),
        ]
        for rel_path in expected_files:
            full_path = os.path.join(ROOT_DIR, rel_path)
            self.assertTrue(os.path.isfile(full_path), f"Expected open-source health file missing: {rel_path}")

if __name__ == "__main__":
    unittest.main()
