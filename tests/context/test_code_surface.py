"""P12 acceptance: a change's code surface is narrowed to ≤ code_files_per_task files plus the related tests; nothing is
dropped silently; unresolved paths are UNKNOWN; the router carries the impact step for existing projects only.
Runs the §74 structural fallback (no Graphify runtime needed)."""
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, ROOT_DIR)

from tests.context.fixtures import make_project  # noqa: E402
from agylite.codebase import FALLBACK_NOTICE, affected  # noqa: E402
from agylite.codebase import structural  # noqa: E402
from agylite.project.identity import detect  # noqa: E402
from agylite.routing import ProjectFacts, Router  # noqa: E402


def write(root: Path, files: dict):
    for rel, text in files.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")


class TestCodeSurface(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name)
        self.home = base / "home"
        self.root = make_project(base)
        files = {"app/__init__.py": "", "app/core.py": "def charge(x):\n    return x\n",
                 "tests/test_core.py": "from app.core import charge\n", "tests/test_mod_00.py": "from app import mod_00\n",
                 "tests/__init__.py": "", "tests/conftest.py": "from app.core import charge\n",
                 "web/src/api.ts": "export const api = 1;\n",
                 "web/src/handler.ts": "import { api } from './api';\nexport const h = api;\n",
                 "web/src/__tests__/handler.test.ts": "import { h } from '../handler';\n",
                 "web/node_modules/x/index.js": "require('./api')\n", "README.md": "# demo\n"}
        files.update({f"app/mod_{i:02d}.py": "from app.core import charge\n" for i in range(30)})
        files["app/deep.py"] = "from .mod_00 import charge\n"   # depth 2 via a relative import
        write(self.root, files)
        self.project = detect(self.root, home=self.home)

    def tearDown(self):
        self.tmp.cleanup()

    def run_affected(self, paths, **kw):
        return affected(self.project, paths, home=self.home, bundle_dir=None, **kw)

    def test_limit_applied_and_reported(self):
        r = self.run_affected(["app/core.py"])
        self.assertEqual(r["method"], "structural")
        self.assertTrue(r["notice"].startswith(FALLBACK_NOTICE))
        self.assertEqual(r["limit"], 12)
        self.assertLessEqual(len(r["files"]), 12)
        self.assertEqual(r["files"][0], {"file": "app/core.py", "reason": "changed", "depth": 0})
        # 1 changed + 30 direct importers + app/deep.py at depth 2 = 32 code files; 20 omitted, never silently
        self.assertEqual(r["omitted"]["files"], 32 - 12)
        tests = [t["file"] for t in r["tests"]]
        self.assertIn("tests/test_core.py", tests)
        self.assertIn("tests/test_mod_00.py", tests)   # depth-2 importer of core via mod_00
        self.assertFalse(any("node_modules" in f["file"] for f in r["files"]))
        self.assertNotIn("tests/conftest.py", tests)   # test support, not a runnable test
        self.assertNotIn("tests/conftest.py", [f["file"] for f in r["files"]])

    def test_relative_python_import_reaches_depth_two(self):
        r = self.run_affected(["app/mod_00.py"])
        files = {f["file"]: f["depth"] for f in r["files"]}
        self.assertEqual(files.get("app/deep.py"), 1)
        self.assertEqual([t["file"] for t in r["tests"]], ["tests/test_mod_00.py"])

    def test_js_relative_imports_and_named_tests(self):
        r = self.run_affected(["web/src/api.ts"])
        self.assertIn("web/src/handler.ts", [f["file"] for f in r["files"]])
        self.assertEqual([t["file"] for t in r["tests"]], ["web/src/__tests__/handler.test.ts"])

    def test_directory_expands_and_unknowns(self):
        r = self.run_affected(["web/src", "app/gone.py", "../outside.py"])
        self.assertIn("web/src/api.ts", [f["file"] for f in r["files"]])
        reasons = {u["path"]: u["reason"] for u in r["unknown"]}
        self.assertIn("app/gone.py", reasons)
        self.assertTrue(any("isolation" in v for v in reasons.values()))

    def test_default_is_git_working_tree(self):
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)
        subprocess.run(["git", "add", "-A"], cwd=self.root, check=True)
        subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "init"], cwd=self.root,
                       check=True)
        (self.root / "app" / "core.py").write_text("def charge(x):\n    return x * 2\n", encoding="utf-8")
        r = self.run_affected(None)
        self.assertEqual((r["source"], r["changed"]), ("git-status", ["app/core.py"]))

    def test_project_untouched(self):
        before = sorted(p.relative_to(self.root) for p in self.root.rglob("*"))
        self.run_affected(["app/core.py"])
        self.assertEqual(sorted(p.relative_to(self.root) for p in self.root.rglob("*")), before)

    def test_test_file_detection(self):
        for path in ("tests/x.py", "pkg/test_a.py", "a_test.go", "src/b.test.tsx", "src/c.spec.js", "FooTests.swift"):
            self.assertTrue(structural.is_test(path), path)
        for path in ("app/core.py", "src/contest.ts", "latest.py"):
            self.assertFalse(structural.is_test(path), path)


class TestRouterImpactStep(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.router = Router()

    def test_existing_change_gets_impact_step(self):
        r = self.router.route("add refund support to the payment webhook", paths=["app/webhook.py"],
                              project=ProjectFacts(stage="existing"))
        self.assertGreaterEqual(r["schema_version"], 3)
        self.assertEqual(r["impact"]["command"], "agylite codebase affected --paths app/webhook.py")
        self.assertEqual(r["impact"]["code_files_limit"], 12)

    def test_new_project_has_no_impact_step(self):
        r = self.router.route("build a booking app", project=ProjectFacts(stage="new"))
        self.assertIsNone(r["impact"])


if __name__ == "__main__":
    unittest.main()
