"""Compact, cheap-to-read project state (spec §18, D-011): `<project>/.vikhyath/`.

state.yaml (identity, stage, stack, plan pointer, answers, last verification) · plan-index.yaml (P10 plan_index) ·
decisions.yaml (P10 decisions) · verification.yaml (verification history). Full documents stay in docs/ and are read
by section only when needed (spec §48–49).
"""
import os
from datetime import datetime, timezone

import yaml

_LOADER = getattr(yaml, "CSafeLoader", yaml.SafeLoader)    # libyaml when available: state reads stay cheap
_DUMPER = getattr(yaml, "CSafeDumper", yaml.SafeDumper)

STATE_FILE = "state.yaml"
VERIFICATION_FILE = "verification.yaml"
SCHEMA_VERSION = 1
DEFAULT_PLAN = "docs/IMPLEMENTATION_PLAN.md"
STAGES = ("new", "existing")


class StateError(RuntimeError):
    pass


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def read_yaml(path):
    if not path.is_file():
        return None
    with open(path, encoding="utf-8") as f:
        return yaml.load(f, Loader=_LOADER)  # noqa: S506 — a SafeLoader variant


def write_yaml(path, data):
    """Atomic write: temp file in the same directory, fsync, rename (no partial file is ever visible)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        yaml.dump(data, f, Dumper=_DUMPER, sort_keys=False, allow_unicode=True, width=120)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def state_path(project):
    return project.state_dir / STATE_FILE


def load_state(project):
    return read_yaml(state_path(project))


def require_state(project):
    state = load_state(project)
    if state is None:
        raise StateError(f"no project state in {project.state_dir} (run `vikhyath project init`)")
    return state


def new_state(project, stage: str, stack=(), plan_path: str = DEFAULT_PLAN):
    if stage not in STAGES:
        raise StateError(f"stage must be one of {STAGES}")
    return {
        "schema_version": SCHEMA_VERSION,
        "project": {"name": project.name, "project_id": project.project_id, "created": now(), "stage": stage},
        "stack": list(stack),
        "plan": {"path": plan_path, "current_phase": None},
        "answers": {},
        "verification": {"last": None},
        "updated": now(),
    }


def save_state(project, state):
    state["updated"] = now()
    write_yaml(state_path(project), state)


def update_state(project, mutate):
    """Read-modify-write of state.yaml; returns the new state."""
    state = require_state(project)
    mutate(state)
    save_state(project, state)
    return state


def record_verification(project, task: str | None, result: str, evidence: str | None):
    entry = {"task": task, "result": result, "evidence": evidence, "at": now()}
    path = project.state_dir / VERIFICATION_FILE
    data = read_yaml(path) or {"schema_version": SCHEMA_VERSION, "results": []}
    data["results"].append(entry)
    write_yaml(path, data)
    update_state(project, lambda s: s["verification"].__setitem__("last", entry))
    return entry


def summary_lines(state, index=None, pending=()):
    """Compact lines for L0 (spec §19.1): stage/stack, phase + active tasks, pending questions, last verification."""
    lines = [f"{state['project']['stage']} project · stack {', '.join(state.get('stack') or []) or 'unknown'}"]
    if index:
        cur = next((p for p in index["phases"] if p["phase_id"] == index.get("current_phase")), None)
        if cur:
            active = ", ".join(cur["active_tasks"]) or "none"
            lines.append(f"phase {cur['phase_id']} {cur['phase_name']} ({cur['status']}) · active tasks: {active}")
        counts = {}
        for p in index["phases"]:
            counts[p["status"]] = counts.get(p["status"], 0) + 1
        lines.append("phases: " + ", ".join(f"{n} {s}" for s, n in sorted(counts.items())))
    if pending:
        by = {}
        for q in pending:
            by[q["priority"]] = by.get(q["priority"], 0) + 1
        lines.append("pending questions: " + ", ".join(f"{n} {p}" for p, n in by.items()))
    last = (state.get("verification") or {}).get("last")
    if last:
        lines.append(" ".join(f"last verification: {last['result']} {last.get('task') or ''} at {last['at']}".split()))
    return lines
