"""P11 acceptance (doc 14, spec §2.4, §70 scenario I): working on project A never reads project B or C, never
changes their state, and never surfaces their decisions or credentials. Every file open is recorded with a
`sys.addaudithook` "open" hook, so reads through any API (pathlib, open, yaml) are caught."""
import contextlib
import hashlib
import io
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, ROOT_DIR)

from tests.context.fixtures import make_bundle, make_project  # noqa: E402
from agylite.cli import main  # noqa: E402
from agylite.context.loader import ContextLoader  # noqa: E402
from agylite.isolation import IsolationError, guard_for, on_violation  # noqa: E402
from agylite.project import decisions, plan_index, state  # noqa: E402
from agylite.project.identity import detect  # noqa: E402

_OPENED = []
_RECORDING = [False]


def _audit(event, args):
    if _RECORDING[0] and event == "open" and args and isinstance(args[0], (str, bytes, os.PathLike)):
        _OPENED.append(os.fsdecode(args[0]))


sys.addaudithook(_audit)

PROJECTS = {
    "auricvista": ("security", "AuricVista keys", "AuricVista keys stay in the AWS secrets manager"),
    "javali": ("design", "JAVALI design system", "JAVALI uses dark brutalist cards"),
    "clientc": ("security", "Client C credentials", "Client C credentials live in vault ABC"),
}
PLAN_PHASE = """## P2 · Booking System
Status: IN_PROGRESS · Depends: P1 · Paths: src/bookings/** · Flags: testing · Evidence: —
Objective: Customers can book.

| ID | Task | Status | Depends | Capabilities | Security | Design | Testing | Acceptance |
|---|---|---|---|---|---|---|---|---|
| T-2.1 | Booking API | IN_PROGRESS | — | engineering/backend | — | — | API tests | works |

"""


def cli(*argv):
    out = io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
        code = main(list(argv))
    return code, out.getvalue()


def tree_hash(*dirs):
    h = hashlib.sha256()
    for d in dirs:
        for p in sorted(Path(d).rglob("*")) if Path(d).exists() else []:
            if p.is_file() and "locks" not in p.parts:
                h.update(str(p).encode() + p.read_bytes())
    return h.hexdigest()


class TestMultiProject(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name)
        self.home = base / "home"
        self.bundle = make_bundle(self.home)
        self.env = mock.patch.dict(os.environ, {"AGYLITE_HOME": str(self.home)})
        self.env.start()
        self.refs = {}
        for name, (kind, topic, decision) in PROJECTS.items():
            root = make_project(base, name, origin=f"git@github.com:example/{name}.git")
            (root / "package.json").write_text('{"dependencies": {"react": "18"}}')
            (root / ".env").write_text(f"{name.upper()}_API_KEY=sk_live_{name}_0123456789abcdef\n")
            self.assertEqual(cli("project", "init", "--docs", "--project", str(root))[0], 0)
            plan = root / "docs" / "IMPLEMENTATION_PLAN.md"
            plan.write_text(plan.read_text().replace("## Change history", PLAN_PHASE + "## Change history"))
            ref = detect(root, home=self.home)
            decisions.add(ref, kind=kind, topic=topic, decision=decision, reason="fixture")
            self.refs[name] = ref

    def tearDown(self):
        self.env.stop()
        self.tmp.cleanup()

    def work_on(self, name, session):
        """One realistic turn on a project; returns (files opened, combined output)."""
        p = ("--project", str(self.refs[name].root))
        _OPENED.clear()
        _RECORDING[0] = True
        try:
            outs = [cli("bootstrap", "--session", session, *p)[1],
                    cli("context", "--route", "Fix the payment webhook security.", "--session", session, *p)[1],
                    cli("context", "--route", "Make the landing page feel premium.", "--session", session, *p)[1],
                    cli("plan", "reconcile", "Add", "Google", "Maps", "navigation", "to", "bookings", *p)[1],
                    cli("decide", "list", *p)[1]]
        finally:
            _RECORDING[0] = False
        return list(_OPENED), "\n".join(outs)

    def forbidden_roots(self, name):
        out = []
        for other, ref in self.refs.items():
            if other != name:
                out += [str(ref.root.resolve()), str(ref.data_dir.resolve())]
        return out

    def test_interleaved_sessions_never_cross_projects(self):
        order = ["auricvista", "javali", "clientc", "auricvista", "clientc", "javali"]
        for i, name in enumerate(order):
            others = [n for n in self.refs if n != name]
            before = {o: tree_hash(self.refs[o].root, self.refs[o].data_dir) for o in others}
            opened, output = self.work_on(name, f"s-{name}")
            resolved = [str(Path(p).resolve()) for p in opened]
            leaked = [p for p in resolved for root in self.forbidden_roots(name) if p.startswith(root + os.sep)]
            self.assertEqual(leaked, [], f"turn {i} on {name} opened another project's files")
            self.assertTrue(any(p.startswith(str(self.refs[name].root.resolve())) for p in resolved))
            for o in others:
                self.assertEqual(tree_hash(self.refs[o].root, self.refs[o].data_dir), before[o],
                                 f"working on {name} changed {o}")
                self.assertNotIn(PROJECTS[o][2], output, f"{o}'s decision surfaced while working on {name}")
            self.assertNotIn("sk_live_", output, "credentials must never reach context output")
        # Each project's own decisions do surface where relevant (scenario I is about *other* projects).
        self.assertIn("AuricVista keys stay in the AWS secrets manager", self.work_on("auricvista", "s2")[1])
        self.assertIn("JAVALI uses dark brutalist cards", self.work_on("javali", "s3")[1])

    def test_guard_blocks_cross_project_reads_and_reports_them(self):
        a, b = self.refs["auricvista"], self.refs["javali"]
        seen = []
        on_violation(lambda project, path, reason, mode: seen.append((project.project_id, path, reason)))
        loader = ContextLoader(a, "s1", self.bundle)
        link = a.root / "docs" / "shortcut.md"
        link.symlink_to(b.root / "docs" / "DESIGN.md")
        targets = [b.root / ".agylite" / "decisions.yaml", b.data_dir / "project.yaml",
                   a.root / ".." / "javali" / ".env", Path("/etc/hosts"), link]
        for t in targets:
            with self.assertRaises(IsolationError, msg=str(t)):
                loader.read(t, display=str(t), level="L3")
        mine = [s for s in seen if s[0] == a.project_id]
        self.assertEqual(len(mine), len(targets))
        guard = guard_for(a, self.bundle)
        guard.check(a.root / "docs" / "PRD.md")                  # own project
        guard.check(a.data_dir / "sessions" / "s1", "write")      # own data
        guard.check(self.bundle / "index.json")                    # OS bundle
        guard.check(Path(ROOT_DIR) / "capabilities" / "engineering" / "security" / "CARD.md")   # OS cards

    def test_state_apis_refuse_paths_outside_the_project(self):
        a, b = self.refs["auricvista"], self.refs["javali"]
        with self.assertRaises(IsolationError):
            state.checked(a, b.state_dir / "state.yaml", "write")
        bad = {"project": {"name": "x", "project_id": a.project_id, "stage": "existing"},
               "plan": {"path": "../javali/docs/IMPLEMENTATION_PLAN.md"}}
        with self.assertRaises(IsolationError):
            plan_index.load_index(a, bad, rebuild=True)


if __name__ == "__main__":
    unittest.main()
