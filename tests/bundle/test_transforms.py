import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, ROOT_DIR)

from vikhyath.bundle import checks  # noqa: E402
from vikhyath.bundle.transforms import gstack, rewrites  # noqa: E402

FM = "---\nname: demo\ndescription: Demo skill.\n---\n"
TMPL = FM + """
{{PREAMBLE}}

# Demo skill heading that is long enough to anchor

{{KEEP_ME}}

This literal paragraph is long enough to be a strong anchor.

{{SECTION:alpha}}

Closing literal paragraph that is also a strong anchor.
"""
GEN = FM + """<!-- AUTO-GENERATED -->
## Preamble (run first)
run gstack-skill-start and send telemetry

# Demo skill heading that is long enough to anchor

KEPT METHODOLOGY TEXT

This literal paragraph is long enough to be a strong anchor.

> generated pointer

Closing literal paragraph that is also a strong anchor.
"""


class TestGstackRenderer(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        root = Path(self._tmp.name)
        (root / "demo" / "sections").mkdir(parents=True)
        (root / "demo" / "SKILL.md.tmpl").write_text(TMPL, encoding="utf-8")
        (root / "demo" / "SKILL.md").write_text(GEN, encoding="utf-8")
        (root / "demo" / "sections" / "manifest.json").write_text(json.dumps({"sections": [
            {"id": "alpha", "file": "alpha.md", "title": "Alpha step", "trigger": "running step 2"}]}), encoding="utf-8")
        self.renderer = gstack.Renderer(root, None)

    def tearDown(self):
        self._tmp.cleanup()

    def test_keeps_methodology_drops_runtime_and_points_to_sections(self):
        out, unresolved = self.renderer.render("demo/SKILL.md.tmpl", TMPL)
        self.assertEqual(unresolved, [])
        self.assertIn("KEPT METHODOLOGY TEXT", out)
        self.assertNotIn("gstack-skill-start", out)
        self.assertNotIn("telemetry", out)
        self.assertIn("Read `sections/alpha.md` when running step 2.", out)
        self.assertNotIn("{{", out)
        self.assertTrue(out.startswith(FM))

    def test_unknown_placeholder_is_reported_not_guessed(self):
        tmpl = TMPL.replace("{{KEEP_ME}}", "{{NEVER_GENERATED}}")
        out, unresolved = self.renderer.render("other/SKILL.md.tmpl", tmpl)
        self.assertEqual(unresolved, ["NEVER_GENERATED"])
        self.assertIn("gstack placeholder NEVER_GENERATED not recovered", out)

    def test_weak_anchor_is_not_used(self):
        isolated, groups = gstack.align("{{A}}\n---\n{{B}}\n\nThis closing literal is long enough to anchor safely.\n",
                                        "a text\n---\nmore a\n---\nb text\n\nThis closing literal is long enough to anchor safely.\n")
        self.assertEqual(isolated, {})
        self.assertEqual(len(groups), 1)


class TestRewrites(unittest.TestCase):
    def test_each_rewrite_applies(self):
        samples = {
            ("unlazy", "SKILL.md"): "Install:\nnode <skill-dir>/scripts/install-hooks.mjs\n",
            ("beyondseo", "SKILL.md"): ("For an installation request, follow [the host-specific guide](docs/agent-installation.md), "
                                        "including Cursor, Lovable workspace imports and agents managing Vercel projects. Rest.\n\n"
                                        "For Lovable execution, read [the Lovable host guide](docs/lovable.md) for details.\n\nNext."),
            ("ecc", "rules/README.md"): "```bash\n./install.sh typescript\n./install.sh python\n```\n",
            ("uiuxpromax", ".claude/skills/ui-ux-pro-max/SKILL.md"): 'python "${CLAUDE_PLUGIN_ROOT}/.claude/skills/ui-ux-pro-max/scripts/search.py"',
        }
        self.assertEqual(set(samples), set(rewrites.REWRITES))
        for (repo, path), text in samples.items():
            out = rewrites.apply(repo, path, text)
            self.assertNotEqual(out, text)
            self.assertNotIn("install-hooks.mjs", out)
            self.assertNotIn("docs/lovable.md", out)
            self.assertNotIn("./install.sh", out)
            self.assertNotIn("CLAUDE_PLUGIN_ROOT", out)

    def test_drift_raises(self):
        with self.assertRaises(rewrites.RewriteDrift):
            rewrites.apply("unlazy", "SKILL.md", "upstream rewrote this section")


class TestChecks(unittest.TestCase):
    def test_hard_mcp_config(self):
        self.assertTrue(checks.hard_violations("x", "a/.mcp.json", "files/x/a/.mcp.json", b"{}"))
        self.assertTrue(checks.hard_violations("x", "c.yaml", "files/x/c.yaml", b"mcpServers:\n  a: {}"))
        self.assertFalse(checks.hard_violations("x", "doc.md", "files/x/doc.md", b"mcpServers mentioned in prose"))
        self.assertFalse(checks.hard_violations("graphify", "tests/fixtures/sample.mcp.json",
                                                "files/graphify/tests/fixtures/sample.mcp.json", b'{"mcpServers": {}}'))

    def test_soft_debts_only_for_adapt(self):
        self.assertEqual(checks.soft_debts("f.md", "ADAPT", b"call mcp__chrome__click"), [("mcp_mentions", "f.md")])
        self.assertEqual(checks.soft_debts("f.md", "PRESERVE", b"call mcp__chrome__click"), [])


if __name__ == "__main__":
    unittest.main()
