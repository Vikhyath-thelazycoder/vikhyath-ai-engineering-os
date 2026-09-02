import json
import os
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))

class TestManifests(unittest.TestCase):
    def test_codex_manifest(self):
        manifest_path = os.path.join(ROOT_DIR, ".codex-plugin", "plugin.json")
        self.assertTrue(os.path.isfile(manifest_path), "Codex manifest missing")
        
        with open(manifest_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        self.assertEqual(data.get("name"), "vikhyath-ai-engineering-os")
        self.assertIn("version", data)
        self.assertIn("skills", data)
        self.assertNotIn("mcpServers", data, "MCP servers prohibited in Codex manifest")
        self.assertNotIn(".mcp.json", str(data), ".mcp.json references prohibited")

    def test_claude_manifest(self):
        manifest_path = os.path.join(ROOT_DIR, ".claude-plugin", "plugin.json")
        self.assertTrue(os.path.isfile(manifest_path), "Claude manifest missing")
        
        with open(manifest_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        self.assertEqual(data.get("name"), "vikhyath-ai-engineering-os")
        self.assertIn("version", data)
        self.assertNotIn("mcpServers", data, "MCP servers prohibited in Claude manifest")

    def test_antigravity_skill_adapter(self):
        skill_path = os.path.join(ROOT_DIR, ".agents", "skills", "vikhyath-os", "SKILL.md")
        self.assertTrue(os.path.isfile(skill_path), "Antigravity skill adapter missing")
        
        with open(skill_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        self.assertTrue(content.startswith("---"), "SKILL.md missing frontmatter")
        self.assertIn("name: vikhyath-os", content)
        self.assertIn("description:", content)

if __name__ == "__main__":
    unittest.main()
