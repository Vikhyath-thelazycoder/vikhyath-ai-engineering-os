"""P17: Brag plan (brag-slim default, full only with local Hyperframes), scenario H routes to media only."""
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, ROOT_DIR)

from tests.context.fixtures import make_project  # noqa: E402
from vikhyath.project.identity import detect  # noqa: E402
from vikhyath.routing import Router, capability_ids  # noqa: E402
from vikhyath.runtimes import brag  # noqa: E402


class TestBrag(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name)
        self.bundle = base / "home" / "bundles" / "b1"
        for mode in ("brag-slim", "brag"):
            (self.bundle / "files" / "brag" / "skills" / mode).mkdir(parents=True)
            (self.bundle / "files" / "brag" / "skills" / mode / "SKILL.md").write_text(f"# {mode}\n", encoding="utf-8")
        self.project = detect(make_project(base), home=base / "home")

    def tearDown(self):
        self.tmp.cleanup()

    def test_slim_default_and_full_needs_local_hyperframes(self):
        self.assertEqual(brag.plan(self.project, self.bundle)["mode"], "brag-slim")
        p = brag.plan(self.project, self.bundle, full=True)
        if brag.hyperframes(self.project.root) is None:
            self.assertEqual(p["mode"], "brag-slim")
            self.assertIn("does not fetch", p["why"])
        hf = self.project.root / "node_modules" / ".bin" / "hyperframes"
        hf.parent.mkdir(parents=True)
        hf.write_text("#!/bin/sh\n", encoding="utf-8")
        self.assertEqual(brag.plan(self.project, self.bundle, full=True)["mode"], "brag")
        self.assertIn("never verification evidence", p["note"])

    def test_no_bundle(self):
        with self.assertRaises(brag.BragError):
            brag.plan(self.project, None)


class TestScenarioH(unittest.TestCase):
    def test_launch_video_activates_media_only(self):
        r = Router().route("Make a launch video plan for our product.")
        ids = capability_ids(r)
        self.assertTrue(ids and all(c.startswith("media/") for c in ids), ids)
        self.assertIsNone(r["lifecycle"])
        self.assertIsNone(r["impact"])


if __name__ == "__main__":
    unittest.main()
