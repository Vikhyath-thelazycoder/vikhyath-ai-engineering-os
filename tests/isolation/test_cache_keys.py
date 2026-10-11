"""P11 (doc 14): cache entries can never be shared between projects, even for identical requests and session ids."""
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, ROOT_DIR)

from tests.context.fixtures import make_bundle, make_project  # noqa: E402
from agylite.context import levels  # noqa: E402
from agylite.context.budget import load_budgets  # noqa: E402
from agylite.context.cache import SessionCache  # noqa: E402
from agylite.context.loader import ContextLoader  # noqa: E402
from agylite.project.identity import detect  # noqa: E402
from agylite.routing import Router  # noqa: E402

REQUEST = "Fix the payment webhook security."


class TestCacheKeys(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name)
        self.home = base / "home"
        self.bundle = make_bundle(self.home)
        self.a = detect(make_project(base, "a", origin="git@github.com:x/a.git"), home=self.home)
        self.b = detect(make_project(base, "b", origin="git@github.com:x/b.git"), home=self.home)
        self.caps = [c["id"] for c in Router().route(REQUEST)["capabilities"]]
        self.budgets = load_budgets()

    def tearDown(self):
        self.tmp.cleanup()

    def load(self, project, session="same-session"):
        loader = ContextLoader(project, session, self.bundle)
        levels.domain_context(loader, self.caps, self.budgets)
        levels.capability_context(loader, self.caps, self.budgets, query=REQUEST)
        loader.finish(self.caps)
        return loader

    def test_identical_request_and_session_id_never_hit_across_projects(self):
        first_a = self.load(self.a)
        self.assertTrue(all(e["cache"] == "miss" for e in first_a.log))
        b = self.load(self.b)
        self.assertTrue(all(e["cache"] == "miss" for e in b.log), "B must not reuse A's cache")
        self.assertNotEqual(first_a.cache.path, b.cache.path)
        self.assertTrue(str(first_a.cache.path).startswith(str(self.a.data_dir)))
        self.assertTrue(str(b.cache.path).startswith(str(self.b.data_dir)))
        self.assertTrue(all(e["cache"] == "hit" for e in self.load(self.a).log))

    def test_cache_file_bound_to_its_project(self):
        path = self.load(self.a).cache.path
        with self.assertRaises(ValueError):
            SessionCache(path, self.b.project_id, "same-session")

    def test_project_ids_differ_for_same_name_different_origin(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "x").mkdir()
            (Path(tmp) / "y").mkdir()
            one = detect(make_project(Path(tmp) / "x", "app", origin="git@github.com:x/app.git"), home=self.home)
            two = detect(make_project(Path(tmp) / "y", "app", origin="git@github.com:y/app.git"), home=self.home)
            self.assertNotEqual(one.project_id, two.project_id)
            self.assertNotEqual(one.data_dir, two.data_dir)


if __name__ == "__main__":
    unittest.main()
