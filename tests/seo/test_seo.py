"""P16: SEO evidence labels, live-site authorization gate, runtime policy, scenarios E/F routing."""
import contextlib
import io
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, ROOT_DIR)

from tests.context.fixtures import make_project  # noqa: E402
from agylite.cli import main  # noqa: E402
from agylite.project.identity import detect  # noqa: E402
from agylite.routing import Router, capability_ids  # noqa: E402
from agylite.runtimes import seo  # noqa: E402
from agylite.seo import authorization, evidence  # noqa: E402

FULL = {"usable": True, "absence_supported": True, "limits": []}
PARTIAL = {"usable": True, "absence_supported": False, "limits": ["Browser render deadline reached"]}
FAILED = {"usable": False, "absence_supported": False, "limits": ["No successful usable page capture."]}


class TestEvidence(unittest.TestCase):
    def test_labels(self):
        self.assertEqual(evidence.label("presence", FULL)["label"], "FACT")
        self.assertEqual(evidence.label("absence", FULL)["label"], "FACT")
        self.assertEqual(evidence.label("presence", PARTIAL)["label"], "OBSERVATION")
        self.assertEqual(evidence.label("absence", PARTIAL)["label"], "UNKNOWN")
        self.assertEqual(evidence.label("interpretation", basis=["FACT"])["label"], "INFERENCE")
        self.assertEqual(evidence.label("interpretation", basis=["UNKNOWN"])["label"], "HYPOTHESIS")
        self.assertEqual(evidence.label("prediction")["label"], "HYPOTHESIS")

    def test_failed_capture_could_not_be_inspected(self):
        r = evidence.label("absence", FAILED)
        self.assertEqual(r["label"], "UNKNOWN")
        self.assertIn("could not be inspected", r["why"])
        self.assertIn("[UNKNOWN] Meta description missing", evidence.render("Meta description missing", r))


class TestAuthorization(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name)
        self.home = base / "home"
        self.root = make_project(base)
        self.project = detect(self.root, home=self.home)
        self.env = mock.patch.dict(os.environ, {"AGYLITE_HOME": str(self.home)})
        self.env.start()

    def tearDown(self):
        self.env.stop()
        self.tmp.cleanup()

    def test_blocked_without_authorization(self):
        with self.assertRaises(authorization.AuthorizationError):
            authorization.require(self.project, None, action="apply")
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            self.assertEqual(main(["seo", "run", "--project", str(self.root), "edit", "apply", "--site", "x"]), 2)
        self.assertIn("authorize it first", err.getvalue())

    def test_grant_scope_and_expiry(self):
        a = authorization.grant(self.project, site="acme.com", task="T-2.1", reason="publish reviewed meta fixes")
        self.assertEqual(authorization.require(self.project, a["id"], action="apply", site="acme.com")["task"], "T-2.1")
        with self.assertRaises(authorization.AuthorizationError):
            authorization.require(self.project, a["id"], action="apply", site="other.com")
        b = authorization.grant(self.project, site="acme.com", task="T-2.1", reason="r", hours=-1)
        with self.assertRaises(authorization.AuthorizationError):
            authorization.require(self.project, b["id"], action="apply")
        text = (self.root / ".agylite" / "seo-authorizations.yaml").read_text(encoding="utf-8")
        self.assertIn("used:", text)
        self.assertNotIn("password", text.lower())

    def test_policy(self):
        with self.assertRaises(seo.SEOError):
            seo.check_command(["watch", "https://example.com"])
        self.assertEqual(seo.check_command(["edit", "apply"]), ("edit", "apply"))
        self.assertIn(("edit", "apply"), seo.LIVE_WRITE)
        self.assertEqual(seo.health(self.home, None)["status"], "no-bundle")


class TestRouting(unittest.TestCase):
    def test_scenarios_e_f(self):
        r = Router()
        self.assertIn("seo/auditing", capability_ids(r.route("Audit my website.")))
        f = r.route("Why are we not showing up in AI-generated answers?")
        self.assertTrue(all(c.startswith("seo/") for c in capability_ids(f)), capability_ids(f))
        self.assertIsNone(f["lifecycle"])


if __name__ == "__main__":
    unittest.main()
