"""P14: design-token checks, UI/UX Pro Max wrapper (persist only into the project), design routing scenarios."""
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, ROOT_DIR)

from tests.context.fixtures import make_project  # noqa: E402
from vikhyath.design import tokens  # noqa: E402
from vikhyath.project.identity import detect  # noqa: E402
from vikhyath.routing import ProjectFacts, Router, capability_ids  # noqa: E402
from vikhyath.runtimes import uiux  # noqa: E402

STAGED_UIUX = Path(ROOT_DIR) / ".staging" / "upstream" / "uiuxpromax"


def write(root, files):
    for rel, text in files.items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text(text, encoding="utf-8")


class TestTokens(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_disciplined_palette_passes(self):
        write(self.root, {"src/theme.css": ":root{--accent:#2563eb;--fg:#111111;--muted:#6b7280;--bg:#ffffff}\n"
                                           ".card{border-radius:8px;font-family:'Inter',sans-serif}\n"
                                           ".btn{border-radius:8px;color:#1d4ed8}\n"})
        r = tokens.check(self.root)
        self.assertEqual(r["status"], "PASS", r)
        self.assertEqual({c["check"]: c["count"] for c in r["checks"]}["accent hues"], 1)

    def test_drift_is_reported(self):
        css = "".join(f".c{i}{{color:{c};border-radius:{i + 2}px}}\n" for i, c in enumerate(
            ["#ef4444", "#22c55e", "#3b82f6", "#a855f7", "#f59e0b", "#ec4899", "#14b8a6"]))
        css += ".g1{color:#64748b}.g2{color:#78716c}.f{font-family:'Inter'}.h{font-family:'Playfair Display'}"
        css += ".m{fontFamily: 'Roboto'}.x{font-family:'Lobster'}"
        write(self.root, {"app/styles.scss": css, "node_modules/x/a.css": ".z{color:#ff00aa}"})
        r = tokens.check(self.root)
        by = {c["check"]: c for c in r["checks"]}
        self.assertEqual(by["accent hues"]["status"], "FAIL")
        self.assertEqual(by["grey families"]["count"], 2)        # slate (cool) + stone (warm)
        self.assertEqual(by["corner radii"]["count"], 7)
        self.assertEqual(by["font families"]["count"], 4)
        self.assertEqual(r["status"], "FAIL")
        self.assertNotIn("#ff00aa", str(r))                      # vendored dirs skipped


@unittest.skipUnless(STAGED_UIUX.is_dir(), "needs the staged uiuxpromax upstream")
class TestUIUX(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name)
        self.bundle = base / "home" / "bundles" / "b1"
        (self.bundle / "files").mkdir(parents=True)
        (self.bundle / "files" / "uiuxpromax").symlink_to(STAGED_UIUX)
        self.project = detect(make_project(base), home=base / "home")

    def tearDown(self):
        self.tmp.cleanup()

    def test_search_and_persist_inside_project(self):
        p = uiux.search(self.bundle, "fintech dashboard", domain="style", cwd=self.project.root)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertTrue(p.stdout.strip())
        base = Path(self.tmp.name).resolve()
        before = set(base.rglob("*"))
        p = uiux.design_system(self.bundle, self.project, "fintech dashboard calm", project_name="Ledger", persist=True)
        self.assertEqual(p.returncode, 0, p.stderr)
        new = set(base.rglob("*")) - before
        self.assertTrue(new)
        self.assertTrue(all(f.is_relative_to(self.project.root.resolve() / "design-system") for f in new), new)
        self.assertTrue((self.project.root / "design-system" / "ledger" / "MASTER.md").is_file())


class TestDesignRouting(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.router = Router()

    def test_scenario_d_design_only(self):
        r = self.router.route("This landing page looks generic. Make it feel premium.", project=ProjectFacts(stage="existing"))
        self.assertEqual(r["domains"], ["design"])
        self.assertIsNone(r["lifecycle"])
        self.assertFalse([c for c in capability_ids(r) if not c.startswith("design/")])

    def test_mobile_routes_to_native_rules(self):
        r = self.router.route("build the onboarding screens for our React Native app", project=ProjectFacts(stage="existing"))
        self.assertIn("design/frontend", capability_ids(r))


if __name__ == "__main__":
    unittest.main()
