"""P12 Graphify wrapper (D-016, SEC-08/09, D-021, §74). Fast tests need no runtime. The real-runtime test installs
Graphify into a temporary home and is opt-in (network for pip, ~15 s). It installs from a built bundle when
VIKHYATH_TEST_BUNDLE names one (what users get: extraction rules applied), else from the staged upstream:

    VIKHYATH_RUNTIME_TESTS=1 [VIKHYATH_TEST_BUNDLE=$VIKHYATH_HOME/bundles/current] python -m unittest tests.runtimes.test_graphify
"""
import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, ROOT_DIR)

from tests.context.fixtures import make_project  # noqa: E402
from vikhyath.cli import main  # noqa: E402
from vikhyath.codebase import FALLBACK_NOTICE, affected  # noqa: E402
from vikhyath.project.identity import detect  # noqa: E402
from vikhyath.runtimes import graphify  # noqa: E402

STAGED = Path(ROOT_DIR) / ".staging" / "upstream" / "graphify"
FIXTURE = {"app/__init__.py": "", "app/payments.py": "def charge(x):\n    return x\n",
           "app/webhook.py": "from app.payments import charge\n\ndef handle(e):\n    return charge(e)\n",
           "app/unrelated.py": "def other():\n    return 1\n",
           "tests/test_webhook.py": "from app.webhook import handle\n\ndef test_handle():\n    assert handle(1) == 1\n"}


def fake_bundle(home: Path, source: Path | None = None) -> Path:
    bundle = home / "bundles" / "b1"
    target = bundle / "files" / "graphify"
    target.parent.mkdir(parents=True)
    if source:
        target.symlink_to(source)
    else:
        target.mkdir()
        (target / "pyproject.toml").write_text("[project]\nname='graphifyy'\n", encoding="utf-8")
    return bundle


class TestWrapperPolicy(unittest.TestCase):
    def test_blocked_subcommands(self):
        for sub in ("hook", "install", "uninstall", "watch", "serve", "extract", "label", "clone", "anything"):
            with self.assertRaises(graphify.GraphifyBlocked, msg=sub):
                graphify.check_command(sub)
        for sub in graphify.ALLOWED:
            graphify.check_command(sub, ["x"])

    def test_os_owns_graph_location(self):
        for flag in ("--graph", "--out=/tmp/x", "--output", "--memory-dir"):
            with self.assertRaises(graphify.GraphifyBlocked):
                graphify.check_command("query", ["q", flag])

    def test_env_points_out_of_project_and_drops_secrets(self):
        with mock.patch.dict(os.environ, {"OPENAI_API_KEY": "sk-x", "GITHUB_TOKEN": "t", "PYTHONPATH": "/x",
                                          "HOME": "/h"}):
            env = graphify._env(Path("/data/projects/p1/graph"))
        self.assertEqual(env["GRAPHIFY_OUT"], "/data/projects/p1/graph")
        self.assertNotIn("OPENAI_API_KEY", env)
        self.assertNotIn("GITHUB_TOKEN", env)
        self.assertNotIn("PYTHONPATH", env)
        self.assertEqual(env["HOME"], "/h")

    def test_lock_changes_with_pins(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = fake_bundle(Path(tmp)) / "files" / "graphify"
            a = graphify.lock_of(src)
            (src / "uv.lock").write_text("v2", encoding="utf-8")
            self.assertNotEqual(a, graphify.lock_of(src))


class TestHealthAndFallback(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name)
        self.home = base / "home"
        self.root = make_project(base)
        for rel, text in FIXTURE.items():
            (self.root / rel).parent.mkdir(parents=True, exist_ok=True)
            (self.root / rel).write_text(text, encoding="utf-8")
        self.project = detect(self.root, home=self.home)

    def tearDown(self):
        self.tmp.cleanup()

    def test_health_states(self):
        self.assertEqual(graphify.health(self.home, None)["status"], "no-bundle")
        bundle = fake_bundle(self.home)
        h = graphify.health(self.home, bundle)
        self.assertEqual(h["status"], "not-installed")
        self.assertIn("vikhyath runtime install graphify", h["reason"])

    def test_not_installed_falls_back_with_notice(self):
        r = affected(self.project, ["app/payments.py"], home=self.home, bundle_dir=fake_bundle(self.home))
        self.assertEqual(r["method"], "structural")
        self.assertIn(FALLBACK_NOTICE, r["notice"])
        self.assertIn("not installed", r["notice"])
        self.assertEqual([f["file"] for f in r["files"]], ["app/payments.py", "app/webhook.py"])
        self.assertEqual([t["file"] for t in r["tests"]], ["tests/test_webhook.py"])

    def test_cli_blocks_and_reports(self):
        err = io.StringIO()
        with mock.patch.dict(os.environ, {"VIKHYATH_HOME": str(self.home)}), contextlib.redirect_stderr(err):
            self.assertEqual(main(["codebase", "query", "x", "--project", str(self.root)]), 1)
        self.assertIn("graph-based analysis unavailable", err.getvalue())
        out = io.StringIO()
        with mock.patch.dict(os.environ, {"VIKHYATH_HOME": str(self.home)}), contextlib.redirect_stdout(out):
            self.assertEqual(main(["codebase", "affected", "--paths", "app/payments.py", "--json",
                                   "--project", str(self.root)]), 0)
        self.assertEqual(json.loads(out.getvalue())["method"], "structural")
        with self.assertRaises(SystemExit):   # not a subcommand at all: argparse rejects it
            with contextlib.redirect_stderr(io.StringIO()):
                main(["codebase", "hook"])


@unittest.skipUnless(os.environ.get("VIKHYATH_RUNTIME_TESTS") and STAGED.is_dir(),
                     "opt-in: VIKHYATH_RUNTIME_TESTS=1 and a staged graphify upstream")
class TestRealRuntime(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        base = Path(cls.tmp.name)
        cls.home = base / "home"
        built = os.environ.get("VIKHYATH_TEST_BUNDLE")
        cls.bundle = Path(built).resolve() if built else fake_bundle(cls.home, STAGED)
        cls.info = graphify.install(cls.home, cls.bundle / "files" / "graphify", log=lambda *_: None)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def setUp(self):
        self.root = make_project(Path(self.tmp.name), name=f"p-{self._testMethodName}")
        for rel, text in FIXTURE.items():
            (self.root / rel).parent.mkdir(parents=True, exist_ok=True)
            (self.root / rel).write_text(text, encoding="utf-8")
        self.project = detect(self.root, home=self.home)

    def test_health_ready_without_mcp(self):
        self.assertEqual(graphify.health(self.home, self.bundle)["status"], "ready")
        venv = graphify.runtime_dir(self.home, self.info["lock"]) / "venv"
        self.assertFalse(graphify._bin(venv, "graphify-mcp").exists())
        p = subprocess.run([str(graphify._bin(venv, "python")), "-c", "import mcp"], capture_output=True)
        self.assertNotEqual(p.returncode, 0)   # the mcp extra is never installed

    def test_graph_affected_tests_and_isolation(self):
        before = sorted(p.relative_to(self.root) for p in self.root.rglob("*"))
        r = affected(self.project, ["app/payments.py"], home=self.home, bundle_dir=self.bundle)
        self.assertEqual(r["method"], "graph", r["notice"])
        self.assertTrue(r["graph"]["rebuilt"])
        self.assertEqual([f["file"] for f in r["files"]], ["app/payments.py", "app/webhook.py"])
        self.assertEqual([t["file"] for t in r["tests"]], ["tests/test_webhook.py"])
        # graph in the OS data dir, nothing written into the project (no graphify-out, hooks or rule files)
        self.assertTrue((self.project.data_dir / "graph" / "graph.json").is_file())
        self.assertEqual(sorted(p.relative_to(self.root) for p in self.root.rglob("*")), before)
        again = affected(self.project, ["app/payments.py"], home=self.home, bundle_dir=self.bundle)
        self.assertFalse(again["graph"]["rebuilt"])   # unchanged code: no rebuild

    def test_query_passthrough(self):
        g = graphify.Graphify(self.project, self.home, self.bundle)
        from vikhyath.codebase import structural
        files, _ = structural.scan(self.root)
        g.ensure_graph(structural.fingerprint(self.root, files))
        for sub, terms in (("query", ["how is a webhook charged"]), ("explain", ["handle"]),
                           ("path", ["handle", "charge"])):
            p = g.passthrough(sub, terms)
            self.assertEqual(p.returncode, 0, f"{sub}: {p.stderr}")
            self.assertIn("app/" if sub != "path" else "charge", p.stdout)


if __name__ == "__main__":
    unittest.main()
