"""Structured decision memory (spec §50–52): `<project>/.agylite/decisions.yaml`.

Security and design decisions are separately discoverable by `kind` and are loaded only when the routed capabilities
make them relevant. `docs/PROJECT_DECISIONS.md`, when present, gets a rendered table between markers.
"""
import re
from datetime import date

from ..isolation import atomic
from ..isolation.locks import project_lock
from .state import SCHEMA_VERSION, checked, read_yaml, write_yaml

DECISIONS_FILE = "decisions.yaml"
KINDS = ("architecture", "security", "design", "product", "data", "infrastructure", "testing", "seo", "media", "process")
STATUSES = ("ACTIVE", "SUPERSEDED", "REVOKED")
MARK_START, MARK_END = "<!-- agylite:decisions:start -->", "<!-- agylite:decisions:end -->"
# Which decision kinds a routed domain makes relevant (spec §51 "load only when relevant").
RELEVANT = {"engineering": ("architecture", "data", "infrastructure", "product"), "codebase": ("architecture",),
            "design": ("design", "product"), "testing": ("testing",), "seo": ("seo",), "media": ("media", "product"),
            "observability": ("process",)}
SECURITY_CAPS = ("engineering/security", "testing/security")


class DecisionError(ValueError):
    pass


def _path(project):
    return project.state_dir / DECISIONS_FILE


def load(project):
    return read_yaml(checked(project, _path(project))) or {"schema_version": SCHEMA_VERSION, "decisions": []}


def _save(project, data):
    write_yaml(checked(project, _path(project), "write"), data)
    render_markdown(project, data)


def add(project, *, kind, topic, decision, reason, alternatives=(), impact="", supersedes=None, tags=()):
    if kind not in KINDS:
        raise DecisionError(f"kind must be one of {', '.join(KINDS)}")
    if not (topic and decision and reason):
        raise DecisionError("topic, decision and reason are required")
    from ..events.log import emit
    with project_lock(project, "decisions"):
        entry = _add_locked(project, kind, topic, decision, reason, alternatives, impact, supersedes, tags)
    emit(project, "STATE_UPDATED", details={"change": "decision_recorded", "decision": entry["decision_id"],
                                            "kind": kind, "supersedes": supersedes})
    return entry


def _add_locked(project, kind, topic, decision, reason, alternatives, impact, supersedes, tags):
    data = load(project)
    ids = {d["decision_id"]: d for d in data["decisions"]}
    if supersedes:
        old = ids.get(supersedes)
        if old is None:
            raise DecisionError(f"unknown decision {supersedes}")
        if old["status"] != "ACTIVE":
            raise DecisionError(f"{supersedes} is already {old['status']}")
        old["status"] = "SUPERSEDED"
    nums = [int(m.group(1)) for d in data["decisions"] if (m := re.match(r"D-(\d+)$", d["decision_id"]))]
    entry = {"decision_id": f"D-{max(nums, default=0) + 1:03d}", "date": date.today().isoformat(), "kind": kind,
             "topic": topic, "decision": decision, "reason": reason, "alternatives": list(alternatives),
             "impact": impact, "supersedes": supersedes, "status": "ACTIVE", "tags": list(tags)}
    data["decisions"].append(entry)
    _save(project, data)
    return entry


def find(project, *, kind=None, topic=None, status="ACTIVE"):
    out = []
    for d in load(project)["decisions"]:
        if status and d["status"] != status:
            continue
        if kind and d["kind"] != kind:
            continue
        if topic and topic.lower() not in (d["topic"] + " " + " ".join(d.get("tags") or [])).lower():
            continue
        out.append(d)
    return out


def relevant(project, capability_ids):
    """ACTIVE decisions whose kind matters for these capabilities; security decisions only with security work."""
    kinds = set()
    for cid in capability_ids:
        kinds.update(RELEVANT.get(cid.split("/", 1)[0], ()))
    if any(c in SECURITY_CAPS for c in capability_ids):
        kinds.add("security")
    return [d for d in find(project) if d["kind"] in kinds]


def render_markdown(project, data=None):
    """Refresh the decisions table inside docs/PROJECT_DECISIONS.md (only between the markers, only if present)."""
    path = checked(project, project.root / "docs" / "PROJECT_DECISIONS.md", "write")
    if not path.is_file():
        return False
    text = path.read_text(encoding="utf-8")
    if MARK_START not in text or MARK_END not in text:
        return False
    data = data or load(project)
    rows = ["| ID | Date | Kind | Topic | Decision | Reason | Supersedes | Status |", "|---|---|---|---|---|---|---|---|"]
    for d in data["decisions"]:
        cells = [d["decision_id"], d["date"], d["kind"], d["topic"], d["decision"], d["reason"],
                 d.get("supersedes") or "—", d["status"]]
        rows.append("| " + " | ".join(str(c).replace("|", "\\|").replace("\n", " ") for c in cells) + " |")
    head, rest = text.split(MARK_START, 1)
    _, tail = rest.split(MARK_END, 1)
    new = f"{head}{MARK_START}\n" + "\n".join(rows) + f"\n{MARK_END}{tail}"
    if new != text:
        atomic.write_text(path, new)
    return True
