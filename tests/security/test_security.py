import os
import unittest
import yaml

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))

class TestSecurity(unittest.TestCase):
    def test_no_mcp_configs(self):
        mcp_file = os.path.join(ROOT_DIR, ".mcp.json")
        self.assertFalse(os.path.exists(mcp_file), ".mcp.json must not exist")
        
        for root, _, files in os.walk(ROOT_DIR):
            if ".git" in root:
                continue
            for file in files:
                if file.endswith((".json", ".yaml", ".yml")) and not file.endswith("CLAUDE.md"):
                    path = os.path.join(root, file)
                    with open(path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        self.assertNotIn("mcpServers", content, f"mcpServers found in {path}")

    def test_no_vendor_directories(self):
        vendor_path = os.path.join(ROOT_DIR, "vendor")
        self.assertFalse(os.path.exists(vendor_path), "vendor directory must not exist")

    def test_all_dependencies_pinned(self):
        caps_path = os.path.join(ROOT_DIR, "config", "capabilities.yaml")
        with open(caps_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            
        capabilities = data.get("capabilities", {})
        for name, meta in capabilities.items():
            ref = meta.get("ref")
            self.assertTrue(ref, f"Capability {name} must have pinned ref")
            self.assertGreaterEqual(len(ref), 7, f"Capability {name} ref '{ref}' is invalid or unpinned")

    def test_no_giant_prompt_files(self):
        for prohibited in ["SYSTEM.md", "MASTER_PROMPT.md"]:
            path = os.path.join(ROOT_DIR, prohibited)
            self.assertFalse(os.path.exists(path), f"Prohibited giant prompt file {prohibited} exists")

if __name__ == "__main__":
    unittest.main()
