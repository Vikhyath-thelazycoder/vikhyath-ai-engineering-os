"""UI/UX Pro Max engine (P14, design/*): the bundled stdlib `search.py`, run under the core Python per command.

Searches are read-only. `--persist` writes only `design-system/<slug>/` under the project root (output dir forced by
the OS, never elsewhere); an existing MASTER.md is kept unless `force` (prior design decisions are not lost).
"""
import subprocess
import sys
from pathlib import Path

DOMAINS = ("style", "color", "chart", "landing", "product", "ux", "typography", "icons", "gsap", "react", "web",
           "google-fonts")


class UIUXError(RuntimeError):
    pass


def script(bundle_dir: Path | None) -> Path | None:
    p = bundle_dir / "files" / "uiuxpromax" / "src" / "ui-ux-pro-max" / "scripts" / "search.py" if bundle_dir else None
    return p if p and p.is_file() else None


def health(bundle_dir: Path | None) -> dict:
    s = script(bundle_dir)
    if s is None:
        return {"runtime": "uiuxpromax", "status": "no-bundle", "reason": "no active bundle with the UI/UX Pro Max engine"}
    return {"runtime": "uiuxpromax", "status": "ready", "version": f"python {sys.version.split()[0]} (stdlib)"}


def _run(bundle_dir, args, cwd: Path):
    s = script(bundle_dir)
    if s is None:
        raise UIUXError(health(bundle_dir)["reason"])
    # -B -E -s (not -I): the engine imports sibling modules from its directory; no bytecode written into the bundle.
    return subprocess.run([sys.executable, "-B", "-E", "-s", str(s), *args], cwd=cwd, capture_output=True, text=True, timeout=120)


def search(bundle_dir, query, *, domain=None, stack=None, max_results=3, as_json=False, cwd: Path):
    args = [query, "--max-results", str(max_results)]
    if domain:
        args += ["--domain", domain]
    if stack:
        args += ["--stack", stack]
    if as_json:
        args.append("--json")
    return _run(bundle_dir, args, cwd)


def design_system(bundle_dir, project, query, *, project_name=None, persist=False, page=None, force=False,
                  dials=None):
    args = [query, "--design-system", "--project-name", project_name or project.name]
    for name, value in (dials or {}).items():
        if value:
            args += [f"--{name}", str(value)]
    if persist:
        args += ["--persist", "--output-dir", str(project.root)]
        if page:
            args += ["--page", page]
        if force:
            args.append("--force")
    return _run(bundle_dir, args, project.root)
