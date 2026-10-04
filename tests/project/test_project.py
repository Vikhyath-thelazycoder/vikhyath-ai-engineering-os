"""P10: project state, plan index, reconciliation, decisions, questions, lifecycle, templates and CLI.

Acceptance: state read ≪ full docs (bytes measured); "Add Google Maps navigation to bookings" lands in the existing
booking phase of the one plan with no new mini-plan file (spec §21).
"""
import contextlib
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, ROOT_DIR)

from vikhyath.cli import main  # noqa: E402
from vikhyath.project import decisions, lifecycle, plan_index, questions, reconcile, state  # noqa: E402
from vikhyath.project.identity import detect  # noqa: E402
from vikhyath.routing import Router  # noqa: E402

PHASES = """
## P2 · Accounts and authentication
Status: COMPLETED · Depends: P1 · Paths: src/auth/** · Flags: security · Evidence: docs/evidence/P2.md
Objective: Travellers sign up and sign in.

| ID | Task | Status | Depends | Capabilities | Security | Design | Testing | Acceptance |
|---|---|---|---|---|---|---|---|---|
| T-2.1 | Email sign-in | COMPLETED | T-1.1 | engineering/security | session cookies | — | auth tests | sign-in works |

## P3 · Booking System
Status: IN_PROGRESS · Depends: P2 · Paths: src/bookings/** · Flags: testing · Evidence: —
Objective: Travellers can book, change and cancel trips.

| ID | Task | Status | Depends | Capabilities | Security | Design | Testing | Acceptance |
|---|---|---|---|---|---|---|---|---|
| T-3.1 | Booking model and API | IN_PROGRESS | T-2.1 | engineering/backend | — | — | API tests | create/cancel booking |
| T-3.2 | Booking confirmation page | PLANNED | T-3.1 | design/frontend | — | layout | UI tests | page shows booking |

## P4 · Payments
Status: PLANNED · Depends: P3 · Paths: src/payments/** · Flags: security · Evidence: —
Objective: Pay for bookings with Stripe.

"""
FILLER = "\n".join(f"Paragraph {i}: " + "realistic project prose about the travel product. " * 12 for i in range(40))


def run_cli(*argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = main(list(argv))
    return code, out.getvalue(), err.getvalue()


class ProjectEnv(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name)
        self.home = base / "home"
        self.root = base / "travel"
        (self.root / "src" / "bookings").mkdir(parents=True)
        (self.root / ".git").mkdir()
        (self.root / ".git" / "HEAD").write_text("ref: refs/heads/main\n")
        (self.root / "package.json").write_text(json.dumps({"dependencies": {"react": "18", "stripe": "1"}}))
        (self.root / "src" / "bookings" / "api.ts").write_text("export const x = 1\n")
        self.env = mock.patch.dict(os.environ, {"VIKHYATH_HOME": str(self.home)})
        self.env.start()
        code, _, err = run_cli("project", "init", "--docs", "--project", str(self.root))
        self.assertEqual(code, 0, err)
        plan = self.root / "docs" / "IMPLEMENTATION_PLAN.md"
        plan.write_text(plan.read_text().replace("## Change history", PHASES.lstrip() + "## Change history"))
        self.project = detect(self.root, home=self.home)

    def tearDown(self):
        self.env.stop()
        self.tmp.cleanup()

    def state_and_index(self):
        st = state.require_state(self.project)
        return st, plan_index.load_index(self.project, st)


class TestPlanIndex(ProjectEnv):
    def test_index_fields_and_current_phase(self):
        st, index = self.state_and_index()
        self.assertEqual([p["phase_id"] for p in index["phases"]], ["P1", "P2", "P3", "P4"])
        p3 = plan_index.phase(index, "P3")
        for field in ("phase_id", "phase_name", "status", "active_tasks", "dependencies", "affected_paths",
                      "security_flags", "design_flags", "testing_flags", "last_updated", "evidence_pointer"):
            self.assertIn(field, p3)   # spec §49
        self.assertEqual((p3["status"], p3["active_tasks"], p3["dependencies"]), ("IN_PROGRESS", ["T-3.1"], ["P2"]))
        self.assertTrue(p3["design_flags"] and p3["testing_flags"])
        self.assertEqual(index["current_phase"], "P3")
        self.assertEqual(plan_index.phase(index, "P2")["evidence_pointer"], "docs/evidence/P2.md")
        section = plan_index.phase_section(self.project, st, index, "P3")
        self.assertTrue(section.startswith("## P3 · Booking System") and "T-3.2" in section and "## P4" not in section)

    def test_index_not_rebuilt_when_plan_unchanged(self):
        st, _ = self.state_and_index()
        with mock.patch.object(plan_index, "build_index") as build:
            plan_index.load_index(self.project, st)
        build.assert_not_called()
        plan = self.root / "docs" / "IMPLEMENTATION_PLAN.md"
        plan.write_text(plan.read_text() + "\n")
        self.assertIsNotNone(plan_index.load_index(self.project, st))

    def test_invalid_status_rejected(self):
        with self.assertRaises(plan_index.PlanError):
            plan_index.parse_plan("## P1 · X\nStatus: DONE\n")
        with self.assertRaises(plan_index.PlanError):
            plan_index.parse_plan("## P1 · X\nStatus: PLANNED\n\n| ID | Task | Status |\n|---|---|---|\n| T-1.1 | a | DONE |\n")


class TestReconcile(ProjectEnv):
    def test_google_maps_lands_in_booking_phase_without_new_files(self):
        before = sorted(p.relative_to(self.root).as_posix() for p in self.root.rglob("*") if p.is_file())
        st = state.require_state(self.project)
        report = reconcile.reconcile(self.project, st, Router(), "Add Google Maps navigation to bookings.")
        self.assertEqual(report["status"], "planned")
        self.assertEqual(report["phase"], {"phase_id": "P3", "phase_name": "Booking System"})
        self.assertEqual(report["task"]["id"], "T-3.3")
        self.assertTrue(report["impact"]["security_impact"]["required"])
        self.assertEqual(report["impact"]["affected_phase"], "P3")
        after = sorted(p.relative_to(self.root).as_posix() for p in self.root.rglob("*") if p.is_file())
        self.assertEqual(sorted(set(after) - set(before)), [], "no new (mini-)plan files")
        _, index = self.state_and_index()
        self.assertIn("T-3.3", [t["id"] for t in plan_index.phase(index, "P3")["tasks"]])
        text = (self.root / "docs" / "IMPLEMENTATION_PLAN.md").read_text()
        self.assertIn("T-3.3 added to P3 Booking System", text)
        self.assertEqual(text.count("## P3 ·"), 1)

    def test_impact_has_all_spec_55_fields(self):
        st = state.require_state(self.project)
        imp = reconcile.reconcile(self.project, st, Router(), "Fix the payment webhook security.")["impact"]
        for f in ("affected_domain", "affected_subdomain", "affected_phase", "affected_files", "dependencies",
                  "security_impact", "design_impact", "testing_impact", "performance_impact", "deployment_impact",
                  "documentation_impact", "rollback_impact"):
            self.assertIn(f, imp)
        self.assertEqual(imp["affected_phase"], "P4")

    def test_unmatched_request_needs_phase_then_new_phase(self):
        st = state.require_state(self.project)
        report = reconcile.reconcile(self.project, st, Router(), "Add a loyalty points programme")
        self.assertEqual(report["status"], "needs_phase")
        report = reconcile.reconcile(self.project, st, Router(), "Add a loyalty points programme",
                                     new_phase="Loyalty programme")
        self.assertEqual((report["phase"]["phase_id"], report["task"]["id"]), ("P5", "T-5.1"))

    def test_task_added_to_completed_phase_reopens_it(self):
        st, index = self.state_and_index()
        _, reopened = reconcile.add_task(self.project, st, index, "P2", "Add passkey sign-in")
        self.assertTrue(reopened)
        self.assertEqual(plan_index.phase(plan_index.load_index(self.project, st), "P2")["status"], "IN_PROGRESS")

    def test_status_transitions_and_evidence(self):
        st, index = self.state_and_index()
        with self.assertRaises(lifecycle.TransitionError):
            reconcile.set_status(self.project, st, index, "T-3.2", "COMPLETED", "x")   # PLANNED → COMPLETED
        with self.assertRaises(lifecycle.TransitionError):
            reconcile.set_status(self.project, st, index, "T-3.1", "DONE")
        reconcile.set_status(self.project, st, index, "T-3.1", "READY_FOR_VERIFICATION")
        index = plan_index.load_index(self.project, st)
        with self.assertRaises(lifecycle.TransitionError):
            reconcile.set_status(self.project, st, index, "T-3.1", "VERIFIED")        # no evidence
        reconcile.set_status(self.project, st, index, "T-3.1", "VERIFIED", "tests/booking: 12 passed")
        index = plan_index.load_index(self.project, st)
        self.assertEqual(plan_index.phase(index, "P3")["tasks"][0]["status"], "VERIFIED")
        last = state.require_state(self.project)["verification"]["last"]
        self.assertEqual((last["task"], last["result"]), ("T-3.1", "VERIFIED"))
        reconcile.set_status(self.project, st, index, "P4", "IN_PROGRESS")
        self.assertEqual(plan_index.phase(plan_index.load_index(self.project, st), "P4")["status"], "IN_PROGRESS")


class TestStateCost(ProjectEnv):
    def test_state_read_much_smaller_than_docs(self):
        docs = self.root / "docs"
        for name in ("PRD.md", "TRD.md", "ARCHITECTURE.md", "SECURITY.md", "DESIGN.md", "SYSTEM_WORKFLOW.md", "FEATURES.md"):
            (docs / name).write_text((docs / name).read_text() + FILLER)
        st, index = self.state_and_index()
        state_bytes = sum((self.project.state_dir / f).stat().st_size for f in ("state.yaml", "plan-index.yaml"))
        doc_bytes = sum(p.stat().st_size for p in docs.glob("*.md"))
        self.assertLess(state_bytes * 5, doc_bytes, f"state {state_bytes} B vs docs {doc_bytes} B")
        lines = state.summary_lines(st, index)
        self.assertLess(len("\n".join(lines).encode()), 600)
        self.assertIn("phase P3 Booking System (IN_PROGRESS) · active tasks: T-3.1", lines)


class TestDecisionsAndQuestions(ProjectEnv):
    def test_decisions_supersede_relevance_and_render(self):
        d1 = decisions.add(self.project, kind="security", topic="API keys",
                           decision="All private API keys remain server-side.", reason="Client keys leak")
        decisions.add(self.project, kind="design", topic="Visual direction", decision="Minimal editorial, no gradients",
                      reason="Brand")
        d3 = decisions.add(self.project, kind="architecture", topic="Queue", decision="Use Postgres queue",
                           reason="One datastore")
        d4 = decisions.add(self.project, kind="architecture", topic="Queue", decision="Use Redis streams",
                           reason="Throughput", supersedes=d3["decision_id"])
        self.assertEqual((d1["decision_id"], d4["decision_id"], d4["supersedes"]), ("D-001", "D-004", "D-003"))
        self.assertEqual([d["decision_id"] for d in decisions.find(self.project, kind="architecture")], ["D-004"])

        def ids(caps):
            return [d["decision_id"] for d in decisions.relevant(self.project, caps)]
        self.assertEqual(ids(["design/visual-quality"]), ["D-002"])
        self.assertEqual(ids(["engineering/security", "codebase/impact-analysis"]), ["D-001", "D-004"])
        self.assertEqual(ids(["seo/auditing"]), [])
        md = (self.root / "docs" / "PROJECT_DECISIONS.md").read_text()
        self.assertIn("| D-003 | ", md)
        self.assertIn("SUPERSEDED", md)
        with self.assertRaises(decisions.DecisionError):
            decisions.add(self.project, kind="vibes", topic="x", decision="y", reason="z")

    def test_question_priorities_inference_and_answers(self):
        bank = questions.load_bank()
        self.assertEqual(questions.validate_bank(bank), [])
        ask, skipped = questions.next_questions(bank, "Build me a travel booking SaaS with AI trip planning",
                                                stage="new", stack=["react", "stripe"])
        self.assertEqual({q["priority"] for q in ask}, {"BLOCKING"})
        self.assertIn("product-goal", [q["id"] for q in ask])
        self.assertEqual(skipped["frontend"], "inferred from the project (react)")
        self.assertIn("deferred", skipped["analytics"])
        answers = {q["id"]: "x" for q in ask}
        ask2, _ = questions.next_questions(bank, "Build me a travel booking SaaS with AI trip planning", stage="new",
                                           stack=["react", "stripe"], answers=answers)
        self.assertTrue(ask2 and "BLOCKING" not in {q["priority"] for q in ask2})
        self.assertIn("ai", [q["id"] for q in ask2])
        ask3, _ = questions.next_questions(bank, "Fix the typo in the footer", stage="existing")
        self.assertEqual(ask3, [])


class TestLifecycle(unittest.TestCase):
    def test_stage_and_stack_detection(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(lifecycle.detect_stage(root), "new")
            (root / "requirements.txt").write_text("Django==5.0\npsycopg2\n")
            self.assertEqual(lifecycle.detect_stage(root), "existing")
            self.assertEqual(lifecycle.detect_stack(root), ["python", "django", "postgres"])
            self.assertEqual(lifecycle.detect_stage(root, {"project": {"stage": "new"}}), "new")

    def test_completion_states_are_spec_25(self):
        self.assertEqual(len(lifecycle.COMPLETION_STATES), 9)
        self.assertNotIn("DONE", lifecycle.COMPLETION_STATES)


class TestTemplates(unittest.TestCase):
    REQUIRED = {
        "PRD.md": ["Problem", "Target users", "Goals", "Non-goals", "Features", "Workflows", "Constraints",
                   "Success criteria", "Assumptions", "Open questions"],
        "TRD.md": ["Stack", "Architecture", "Infrastructure", "APIs", "Database", "Integrations", "AI/LLM system",
                   "Runtime", "Deployment", "Environment variables", "Dependencies"],
        "ARCHITECTURE.md": ["Major components", "Boundaries", "Data flow", "Trust boundaries", "Integrations",
                            "Infrastructure", "Failure modes"],
        "SYSTEM_WORKFLOW.md": ["User action", "Backend behavior", "Data flow", "AI flow", "External API flow",
                               "State changes", "Verification"],
        "SECURITY.md": ["Assets and threats", "Secrets", "Security tests"],
        "DESIGN.md": ["Visual direction", "Component principles", "Typography", "Color", "Spacing", "Responsive rules",
                      "Interaction", "Accessibility", "Motion", "Reference sources"],
        "FEATURES.md": ["Feature list"],
        "IMPLEMENTATION_PLAN.md": ["P1 · Foundations", "Change history"],
        "PROJECT_DECISIONS.md": [],
    }

    def test_templates_have_spec_20_sections(self):
        base = Path(ROOT_DIR) / "templates" / "project-docs"
        self.assertEqual(sorted(p.name for p in base.glob("*.md")), sorted(self.REQUIRED))
        for name, headings in self.REQUIRED.items():
            text = (base / name).read_text(encoding="utf-8")
            for h in headings:
                self.assertIn(f"\n## {h}\n", text, f"{name}: ## {h}")
            self.assertIn("{{PROJECT_NAME}}", text)
        plan = (base / "IMPLEMENTATION_PLAN.md").read_text(encoding="utf-8")
        self.assertEqual(plan_index.parse_plan(plan)[0]["phase_id"], "P1")
        self.assertIn(decisions.MARK_START, (base / "PROJECT_DECISIONS.md").read_text(encoding="utf-8"))


class TestCli(ProjectEnv):
    def test_cli_flow(self):
        p = ("--project", str(self.root))
        code, out, _ = run_cli("plan", "reconcile", "Add", "Google", "Maps", "navigation", "to", "bookings", *p)
        self.assertEqual(code, 0)
        self.assertIn("phase_id: P3", out)
        self.assertEqual(run_cli("plan", "set-status", "T-3.2", "IN_PROGRESS", *p)[0], 0)
        code, _, err = run_cli("plan", "set-status", "T-3.2", "COMPLETED", *p)
        self.assertEqual(code, 1)
        self.assertIn("not allowed", err)
        code, out, _ = run_cli("state", *p, "--json")
        self.assertEqual(json.loads(out)["current_phase"]["active_tasks"], ["T-3.1", "T-3.2"])
        self.assertEqual(run_cli("decide", "add", "--kind", "security", "--topic", "Keys", "--decision", "Server-side",
                                 "--reason", "Leaks", *p)[0], 0)
        code, out, _ = run_cli("context", "engineering/security", "--level", "1", *p)
        self.assertIn("D-001 [security] Keys: Server-side", out)
        code, out, _ = run_cli("bootstrap", "--session", "s1", *p)
        self.assertIn("phase: P3 Booking System (IN_PROGRESS)", out)
        self.assertIn("plan: docs/IMPLEMENTATION_PLAN.md#P3", out)
        self.assertTrue((self.project.data_dir / "sessions" / "s1" / "session.yaml").is_file())
        self.assertEqual(run_cli("project", "init", *p)[0], 1)    # already initialised

    def test_relink_moves_data_without_merging(self):
        run_cli("bootstrap", "--session", "s1", "--project", str(self.root))
        old_id = self.project.project_id
        moved = self.root.parent / "travel-moved"
        self.root.rename(moved)
        new = detect(moved, home=self.home)
        self.assertNotEqual(new.project_id, old_id)
        code, _, err = run_cli("project", "relink", "--from", old_id, "--project", str(moved))
        self.assertEqual(code, 0, err)
        self.assertTrue((new.data_dir / "sessions" / "s1" / "session.yaml").is_file())
        self.assertFalse((self.home / "projects" / old_id).exists())
        self.assertEqual(state.require_state(new)["project"]["project_id"], new.project_id)
        self.assertIn(old_id, state.read_yaml(new.data_dir / "project.yaml")["aliases"])


if __name__ == "__main__":
    unittest.main()
