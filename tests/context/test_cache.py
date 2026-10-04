"""P9 acceptance: a second identical load in the same session is a cache hit with no file reread (spec §17)."""
import os
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, ROOT_DIR)

from tests.context.fixtures import make_bundle, make_project  # noqa: E402
from vikhyath.context import levels  # noqa: E402
from vikhyath.context import loader as loader_mod  # noqa: E402
from vikhyath.context.budget import load_budgets  # noqa: E402
from vikhyath.context.cache import SessionCache  # noqa: E402
from vikhyath.context.loader import ContextLoader  # noqa: E402
from vikhyath.project.identity import detect  # noqa: E402

CAPS = ["engineering/security", "engineering/backend", "testing/security"]


class TestSessionCache(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name)
        self.home = base / "home"
        self.bundle = make_bundle(self.home)
        self.project = detect(make_project(base), home=self.home)
        self.budgets = load_budgets()

    def tearDown(self):
        self.tmp.cleanup()

    def assemble(self, session, **kw):
        loader = ContextLoader(self.project, session, self.bundle, **kw)
        l1 = levels.domain_context(loader, CAPS, self.budgets)
        l2 = levels.capability_context(loader, CAPS, self.budgets, query="webhook signature")
        loader.finish(CAPS)
        return loader, l1["text"] + l2["text"]

    def test_second_identical_load_rereads_nothing(self):
        first, text1 = self.assemble("s1")
        self.assertTrue(first.log and all(e["cache"] == "miss" for e in first.log))
        with mock.patch.object(Path, "read_text", autospec=True, side_effect=Path.read_text) as reads:
            second, text2 = self.assemble("s1")
        reread = [str(c.args[0]) for c in reads.call_args_list
                  if str(c.args[0]).startswith(str(self.bundle)) or str(c.args[0]).endswith("CARD.md")]
        self.assertEqual(reread, [], "cached content must not be reread")
        self.assertTrue(second.log and all(e["cache"] == "hit" and e["bytes"] == 0 for e in second.log))
        self.assertIn("[cached]", text2)
        self.assertLess(len(text2), len(text1) / 4)

    def test_other_session_and_no_cache_resend(self):
        self.assemble("s1")
        other, _ = self.assemble("s2")
        self.assertTrue(all(e["cache"] == "miss" for e in other.log))
        fresh, _ = self.assemble("s1", use_cache=False)
        self.assertTrue(all(e["cache"] == "miss" for e in fresh.log))
        anonymous, _ = self.assemble(None)
        self.assertIsNone(anonymous.cache)

    def test_changed_project_file_is_a_miss(self):
        card = Path(ROOT_DIR) / "capabilities" / "engineering" / "security" / "CARD.md"
        self.assemble("s1")
        st = card.stat()
        try:
            os.utime(card, ns=(st.st_atime_ns, st.st_mtime_ns + 1_000_000))
            loader = ContextLoader(self.project, "s1", self.bundle)
            levels.domain_context(loader, ["engineering/security"], self.budgets)
            self.assertEqual(loader.log[0]["cache"], "miss")
        finally:
            os.utime(card, ns=(st.st_atime_ns, st.st_mtime_ns))

    def test_cache_keyed_by_project_and_session(self):
        loader, _ = self.assemble("s1")
        path = loader.cache.path
        self.assertEqual(path, self.project.data_dir / "sessions" / "s1" / "context-cache.json")
        with self.assertRaises(ValueError):
            SessionCache(path, "another-project", "s1")

    def test_context_index_built_once_per_bundle(self):
        self.assemble("s1")
        with mock.patch.object(loader_mod, "build_context_index") as build:
            self.assemble("s3")
        build.assert_not_called()

    def test_cached_assembly_is_fast(self):
        self.assemble("s1")
        start = time.perf_counter()
        self.assemble("s1")
        self.assertLess(time.perf_counter() - start, 1.0)


if __name__ == "__main__":
    unittest.main()
