"""Select the smallest sufficient set of checks for a change (P15, D-035): impacted tests (P12 `affected`) + static
checks; the full suite only when nothing narrower is known or on request. Every selection states its reason."""
from pathlib import PurePosixPath

from .detect import Check

KIND_WORDS = (("security", ("security", "auth", "signature", "csrf", "permission", "injection")),
              ("idempotency", ("idempot", "retry", "replay", "duplicate")),
              ("integration", ("integration", "e2e_api", "flow", "contract")),
              ("regression", ("regression", "bug")),
              ("api", ("api", "endpoint", "route", "handler", "webhook", "controller")))


def test_kind(path: str) -> str:
    low = path.lower()
    for kind, words in KIND_WORDS:
        if any(w in low for w in words):
            return kind
    return "unit"


def _module(path: str) -> str:
    p = PurePosixPath(path)
    return ".".join(p.with_suffix("").parts)


def targeted(check: Check, tests):
    """The check's command narrowed to the selected test files, or None when the runner cannot narrow."""
    if not tests:
        return None
    if check.selective == "pytest":
        return [*check.command, *tests]
    if check.selective == "unittest":
        py = [t for t in tests if t.endswith(".py")]
        return [check.command[0], "-m", "unittest", *[_module(t) for t in py]] if py else None
    if check.selective == "node":
        js = [t for t in tests if t.endswith((".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"))]
        return [*check.command, "--", *js] if js else None
    if check.selective == "go":
        pkgs = sorted({"./" + str(PurePosixPath(t).parent) for t in tests if t.endswith("_test.go")})
        return [*check.command[:2], *pkgs] if pkgs else None
    return None


def plan(checks, impact, *, full=False, kinds=None, include_e2e=False):
    """[(check, command, reason, tests)] in run order."""
    tests = [t["file"] for t in (impact or {}).get("tests", [])]
    omitted = (impact or {}).get("omitted", {}).get("tests", 0)
    out = []
    for c in checks:
        if kinds and c.kind not in kinds:
            continue
        if c.kind == "e2e" and not include_e2e:
            continue
        if c.kind == "test":
            narrowed = None if full or omitted else targeted(c, tests)
            if narrowed:
                out.append((c, narrowed, f"{len(tests)} tests affected by the change", tests))
            else:
                why = ("full suite requested" if full else
                       f"{omitted} affected tests beyond the code-surface limit" if omitted else
                       "no affected tests identified" if not tests else
                       f"{c.name} cannot run individual test files")
                out.append((c, c.command, f"full suite: {why}", []))
        else:
            out.append((c, c.command, f"{c.kind} check for the project", []))
    return out
