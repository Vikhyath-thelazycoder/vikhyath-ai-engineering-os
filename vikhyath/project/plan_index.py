"""Implementation-plan index (spec §20.7, §49): read the living markdown plan once, answer from a compact index.

Plan format (templates/project-docs/IMPLEMENTATION_PLAN.md):

    ## P4 · Booking System
    Status: IN_PROGRESS · Depends: P3 · Paths: src/bookings/** · Flags: security, testing · Evidence: docs/evidence/P4.md
    Objective: Travellers can book, change and cancel trips.

    | ID | Task | Status | Depends | Capabilities | Security | Design | Testing | Acceptance |
    |---|---|---|---|---|---|---|---|---|
    | T-4.1 | Booking model and API | COMPLETED | — | engineering/backend | — | — | API tests | … |

`plan-index.yaml` stores the §49 fields per phase plus each phase's character range, so one phase can be loaded
without the rest. The index is rebuilt only when the plan file's size or mtime changes.
"""
import hashlib
import re

from .lifecycle import ACTIVE_STATES, COMPLETION_STATES
from .state import SCHEMA_VERSION, now, read_yaml, write_yaml

INDEX_FILE = "plan-index.yaml"
PHASE_RE = re.compile(r"^##[ \t]+(P\d+[A-Za-z]?)[ \t]*[·:—–-][ \t]*(.+?)[ \t]*$", re.M)
H2_RE = re.compile(r"^##[ \t]+\S", re.M)
TASK_COLUMNS = ("ID", "Task", "Status", "Depends", "Capabilities", "Security", "Design", "Testing", "Acceptance")
EMPTY = {"", "—", "-", "–", "n/a", "none"}


class PlanError(ValueError):
    pass


def _cells(line: str):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def _list(value: str):
    return [v.strip() for v in re.split(r"[,;]", value or "") if v.strip() and v.strip().lower() not in EMPTY]


def _meta(block: str):
    """`Key: value · Key: value` lines (and `Objective: …`) at the top of a phase section."""
    meta = {}
    for line in block.splitlines():
        if line.startswith("|") or line.startswith("#"):
            break
        for part in line.split("·"):
            if ":" in part:
                k, v = part.split(":", 1)
                if re.fullmatch(r"[A-Za-z][A-Za-z ]{0,30}", k.strip()):
                    meta[k.strip().lower()] = v.strip()
    return meta


def _tasks(block: str):
    rows, header = [], None
    for line in block.splitlines():
        if not line.lstrip().startswith("|"):
            if header and rows:
                break
            continue
        cells = _cells(line)
        if header is None:
            header = [c.lower() for c in cells]
            continue
        if all(set(c) <= set("-: ") for c in cells):
            continue
        rows.append(dict(zip(header, cells)))
    return rows


def parse_plan(text: str):
    """Phases with §49 fields and section ranges; raises PlanError on invalid statuses or duplicate ids."""
    heads = list(PHASE_RE.finditer(text))
    phases, seen_tasks = [], set()
    for i, m in enumerate(heads):
        start = m.start()
        nxt = H2_RE.search(text, m.end())
        end = heads[i + 1].start() if i + 1 < len(heads) else len(text)
        if nxt and nxt.start() < end:
            end = nxt.start()
        block = text[m.end():end]
        meta = _meta(block.lstrip("\n"))
        status = (meta.get("status") or "NOT_STARTED").upper()
        if status not in COMPLETION_STATES:
            raise PlanError(f"{m.group(1)}: status {status} is not a spec §25 state")
        tasks = []
        for row in _tasks(block):
            tid = row.get("id", "")
            if not tid:
                continue
            tstatus = (row.get("status") or "NOT_STARTED").upper()
            if tstatus not in COMPLETION_STATES:
                raise PlanError(f"{tid}: status {tstatus} is not a spec §25 state")
            if tid in seen_tasks:
                raise PlanError(f"duplicate task id {tid}")
            seen_tasks.add(tid)
            tasks.append({"id": tid, "title": row.get("task", ""), "status": tstatus,
                          "security": row.get("security", "").lower() not in EMPTY,
                          "design": row.get("design", "").lower() not in EMPTY,
                          "testing": row.get("testing", "").lower() not in EMPTY})
        flags = {f.lower() for f in _list(meta.get("flags", ""))}
        phases.append({
            "phase_id": m.group(1),
            "phase_name": m.group(2),
            "status": status,
            "objective": meta.get("objective", ""),
            "active_tasks": [t["id"] for t in tasks if t["status"] in ACTIVE_STATES],
            "tasks": [{"id": t["id"], "title": t["title"], "status": t["status"]} for t in tasks],
            "dependencies": _list(meta.get("depends", "")),
            "affected_paths": _list(meta.get("paths", "")),
            "security_flags": "security" in flags or any(t["security"] for t in tasks),
            "design_flags": "design" in flags or any(t["design"] for t in tasks),
            "testing_flags": "testing" in flags or any(t["testing"] for t in tasks),
            "last_updated": meta.get("updated"),
            "evidence_pointer": None if meta.get("evidence", "").lower() in EMPTY else meta.get("evidence"),
            "section": {"start": start, "end": end},
        })
    ids = [p["phase_id"] for p in phases]
    if len(set(ids)) != len(ids):
        raise PlanError("duplicate phase ids")
    return phases


def current_phase(phases):
    for wanted in (("IN_PROGRESS", "BLOCKED", "READY_FOR_VERIFICATION", "PARTIALLY_COMPLETE"), ("PLANNED", "NOT_STARTED")):
        for p in phases:
            if p["status"] in wanted:
                return p["phase_id"]
    return None


def plan_file(project, state):
    return project.root / ((state or {}).get("plan", {}).get("path") or "docs/IMPLEMENTATION_PLAN.md")


def index_path(project):
    return project.state_dir / INDEX_FILE


def build_index(project, state):
    path = plan_file(project, state)
    if not path.is_file():
        return None
    text = path.read_text(encoding="utf-8")
    st = path.stat()
    phases = parse_plan(text)
    index = {"schema_version": SCHEMA_VERSION, "plan_path": path.relative_to(project.root).as_posix(),
             "plan_sha256": hashlib.sha256(text.encode()).hexdigest(), "plan_size": st.st_size,
             "plan_mtime_ns": st.st_mtime_ns, "built": now(), "current_phase": current_phase(phases),
             "phases": phases}
    write_yaml(index_path(project), index)
    return index


def load_index(project, state, rebuild=False):
    """The plan index; rebuilt only when the plan changed (one stat, no plan read on the fast path)."""
    path = plan_file(project, state)
    index = None if rebuild else read_yaml(index_path(project))
    if index is not None:
        if not path.is_file():
            return None
        st = path.stat()
        if (index.get("plan_size"), index.get("plan_mtime_ns")) == (st.st_size, st.st_mtime_ns):
            return index
    return build_index(project, state)


def phase(index, phase_id):
    for p in (index or {}).get("phases", []):
        if p["phase_id"].lower() == phase_id.lower():
            return p
    raise PlanError(f"no phase {phase_id} in the plan")


def phase_section(project, state, index, phase_id):
    """Only the requested phase's text (spec §49 "load full sections only when required")."""
    p = phase(index, phase_id)
    text = plan_file(project, state).read_text(encoding="utf-8")
    return text[p["section"]["start"]:p["section"]["end"]]
