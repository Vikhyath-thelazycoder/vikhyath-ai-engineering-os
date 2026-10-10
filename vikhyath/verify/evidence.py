"""Machine-readable verification evidence (P15, D-035): one JSON file per run in `<project>/.vikhyath/evidence/`,
recorded as the project's last verification. Evidence is a command + exit code + counts; descriptions such as
"looks correct" or screenshots are rejected."""
import json
import re
from datetime import datetime, timezone

from ..isolation import atomic
from ..isolation.guard import guard_for
from . import policy

FORBIDDEN = re.compile(r"screenshot|visual inspection|looks correct|looks good|seems to work", re.I)


class EvidenceError(ValueError):
    pass


def validate(record) -> list:
    cfg = policy.load_policy()
    required = (cfg.get("evidence") or {}).get("required_fields") or ["command", "exit_code", "result", "at"]
    results = (cfg.get("evidence") or {}).get("results") or ["PASSED", "FAILED", "NOT_TESTED", "BLOCKED"]
    p = []
    for i, check in enumerate(record.get("checks", [])):
        for f in required:
            if check.get(f) in (None, ""):
                p.append(f"check {i}: missing {f}")
        if check.get("result") not in results:
            p.append(f"check {i}: result must be one of {results}")
        text = " ".join(str(check.get(k, "")) for k in ("command", "result", "note"))
        if FORBIDDEN.search(text):
            p.append(f"check {i}: '{FORBIDDEN.search(text).group(0)}' is not evidence (command + exit code + counts)")
    if record.get("result") not in results:
        p.append("overall result missing")
    return p


def overall(checks) -> str:
    results = [c["result"] for c in checks]
    if not results:
        return "NOT_TESTED"
    if "FAILED" in results:
        return "FAILED"
    if "BLOCKED" in results:
        return "BLOCKED"
    return "PASSED"


def write(project, record) -> str:
    problems = validate(record)
    if problems:
        raise EvidenceError("; ".join(problems))
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    rel = f".vikhyath/evidence/{stamp}.json"
    path = guard_for(project).check(project.root / rel, "write")
    path.parent.mkdir(parents=True, exist_ok=True)
    atomic.write_text(path, json.dumps(record, indent=1, ensure_ascii=False) + "\n")
    return rel
