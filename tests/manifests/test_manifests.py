import json
import os
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))

class TestManifests(unittest.TestCase):
    def test_portable_root_plugin_json(self):
        manifest_path = os.path.join(ROOT_DIR, "plugin.json")
        self.assertTrue(os.path.isfile(manifest_path), "Root plugin.json missing")
        
        with open(manifest_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        self.assertEqual(data.get("$schema"), "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json")
        self.assertEqual(data.get("name"), "vikhyath-ai-engineering-os")
        self.assertEqual(data.get("version"), "1.0.1")
        self.assertIn("description", data)
        self.assertIn("author", data)
        self.assertIn("repository", data)
        self.assertEqual(data.get("license"), "MIT")
        
        # Ensure no host-specific or forbidden fields are in portable root manifest
        forbidden_fields = ["skills", "mcpServers", "interface", "hooks", "tools"]
        for field in forbidden_fields:
            self.assertNotIn(field, data, f"Forbidden field '{field}' in portable root plugin.json")

    def test_codex_manifest(self):
        manifest_path = os.path.join(ROOT_DIR, ".codex-plugin", "plugin.json")
        self.assertTrue(os.path.isfile(manifest_path), "Codex manifest missing")
        
        with open(manifest_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        self.assertEqual(data.get("name"), "vikhyath-ai-engineering-os")
        self.assertEqual(data.get("version"), "1.0.1")
        self.assertEqual(data.get("skills"), "./skills/")
        self.assertIn("interface", data)
        self.assertNotIn("mcpServers", data, "MCP servers prohibited in Codex manifest")

    def test_claude_manifest(self):
        manifest_path = os.path.join(ROOT_DIR, ".claude-plugin", "plugin.json")
        self.assertTrue(os.path.isfile(manifest_path), "Claude manifest missing")
        
        with open(manifest_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        self.assertEqual(data.get("name"), "vikhyath-ai-engineering-os")
        self.assertEqual(data.get("version"), "1.0.1")
        self.assertNotIn("skills", data, "Claude manifest should not contain relative skills path")
        self.assertNotIn("mcpServers", data, "MCP servers prohibited in Claude manifest")

    def test_codex_marketplace_manifest(self):
        mkt_path = os.path.join(ROOT_DIR, ".agents", "plugins", "marketplace.json")
        self.assertTrue(os.path.isfile(mkt_path), "Codex marketplace manifest missing")
        
        with open(mkt_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        self.assertEqual(data.get("name"), "vikhyath-marketplace")
        self.assertIn("plugins", data)
        self.assertGreaterEqual(len(data["plugins"]), 1)
        plugin = data["plugins"][0]
        self.assertEqual(plugin.get("name"), "vikhyath-ai-engineering-os")
        self.assertEqual(plugin.get("version"), "1.0.1")
        self.assertEqual(plugin.get("source"), "./")

    def test_claude_marketplace_manifest(self):
        mkt_path = os.path.join(ROOT_DIR, ".claude-plugin", "marketplace.json")
        self.assertTrue(os.path.isfile(mkt_path), "Claude marketplace manifest missing")
        
        with open(mkt_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        self.assertEqual(data.get("name"), "vikhyath-marketplace")
        self.assertIn("plugins", data)
        self.assertGreaterEqual(len(data["plugins"]), 1)
        plugin = data["plugins"][0]
        self.assertEqual(plugin.get("name"), "vikhyath-ai-engineering-os")
        self.assertEqual(plugin.get("version"), "1.0.1")
        self.assertEqual(plugin.get("source"), "./")

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
