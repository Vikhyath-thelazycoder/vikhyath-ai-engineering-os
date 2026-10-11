"""BeyondSEO runtime (P16, D-016, SEC-11, D-041): isolated venv `runtimes/seo-<lock>`, started per command.

Core install has no browser; the `browser` extra (Playwright + Chromium, ~557 MB) and the `reports` extra are added
only on explicit request. Browser use stays inside this runtime (config/verification.yaml `scoped_browser_use`) and its
captures are SEO evidence, never engineering verification. `watch` (recurring monitor) is blocked; `edit apply` and
`edit rollback` write to live websites and need a per-task authorization (agylite/seo/authorization.py).
Output goes to the project's data dir unless `--out` points inside the project.
"""
import os
import re
import subprocess
import time
from pathlib import Path

from . import venv as pyvenv

EXTRAS = ("browser", "reports")
BLOCKED = {"watch": "recurring monitor process (§2.5)"}
LIVE_WRITE = {("edit", "apply"), ("edit", "rollback")}
_SECRET_ENV = re.compile(r"(API_KEY|_TOKEN|SECRET|PASSWORD|CREDENTIAL)", re.I)
TIMEOUT = 3600


class SEOError(RuntimeError):
    pass


def source_dir(bundle_dir: Path | None) -> Path | None:
    src = bundle_dir / "files" / "beyondseo" if bundle_dir else None
    return src if src and (src / "pyproject.toml").is_file() else None


def runtime_dir(home: Path, lock: str) -> Path:
    return Path(home) / "runtimes" / f"seo-{lock}"


def _final(home, bundle_dir):
    src = source_dir(bundle_dir)
    if src is None:
        raise SEOError("no active bundle with files/beyondseo")
    return src, runtime_dir(home, pyvenv.lock_of(src, "beyondseo"))


def install(home: Path, bundle_dir: Path | None, extras=(), log=print) -> dict:
    bad = [e for e in extras if e not in EXTRAS]
    if bad:
        raise SEOError(f"unknown extra {bad[0]}; available: {', '.join(EXTRAS)}")
    src, final = _final(home, bundle_dir)
    try:
        info = pyvenv.install(final, src, name="beyondseo", lock=final.name.split("-", 1)[1],
                              version_cmd=["-m", "beyondseo", "--version"], log=log)
        if extras:
            info = pyvenv.add_extras(final, src, "beyondseo", extras, log=log)
            if "browser" in extras and not info.get("chromium"):
                log("installing Chromium for the browser extra (scoped to SEO; large download)…")
                p = subprocess.run([str(pyvenv.bin_path(final / "venv", "python")), "-m", "playwright", "install",
                                    "chromium"], capture_output=True, text=True,
                                   env={**os.environ, "PLAYWRIGHT_BROWSERS_PATH": str(final / "browsers")})
                if p.returncode:
                    raise SEOError(f"playwright install failed: {(p.stderr or p.stdout).strip()[-500:]}")
        return info
    except pyvenv.VenvError as exc:
        raise SEOError(str(exc)) from exc


def health(home: Path, bundle_dir: Path | None) -> dict:
    try:
        _src, final = _final(home, bundle_dir)
    except SEOError as exc:
        return {"runtime": "seo", "status": "no-bundle", "reason": str(exc)}
    if not (final / "runtime.json").is_file():
        return {"runtime": "seo", "status": "not-installed", "reason": "run `agylite runtime install seo`",
                "path": str(final)}
    import json
    info = json.loads((final / "runtime.json").read_text(encoding="utf-8"))
    p = subprocess.run([str(pyvenv.bin_path(final / "venv", "python")), "-I", "-c", "import beyondseo, bs4"],
                       capture_output=True, text=True)
    if p.returncode:
        return {"runtime": "seo", "status": "broken", "reason": (p.stderr.strip().splitlines() or ["?"])[-1]}
    return {"runtime": "seo", "status": "ready", "version": info.get("version"), "extras": info.get("extras", []),
            "path": str(final)}


def check_command(args) -> tuple:
    """(command, action) after policy checks; raises SEOError for blocked commands."""
    if not args:
        raise SEOError("name a BeyondSEO command, e.g. crawl <url>")
    cmd = args[0]
    if cmd in BLOCKED:
        raise SEOError(f"beyondseo {cmd} is blocked by the OS wrapper: {BLOCKED[cmd]}")
    action = args[1] if cmd == "edit" and len(args) > 1 else None
    return cmd, action


def run(project, home: Path, bundle_dir, args, *, out: Path | None = None, timeout=TIMEOUT):
    """Run one BeyondSEO command in the project. `--out` defaults to the project's data dir (not the project tree)."""
    _src, final = _final(home, bundle_dir)
    if not (final / "runtime.json").is_file():
        raise SEOError("SEO runtime not installed (`agylite runtime install seo`)")
    args = list(args)
    if "--out" not in args and args[0] not in ("edit", "readiness", "report"):
        out = out or project.data_dir / "seo" / time.strftime("%Y%m%dT%H%M%S")
        out.parent.mkdir(parents=True, exist_ok=True)
        args += ["--out", str(out)]
    env = {k: v for k, v in os.environ.items() if not _SECRET_ENV.search(k)}
    env["PLAYWRIGHT_BROWSERS_PATH"] = str(final / "browsers")
    env.pop("PYTHONPATH", None)
    try:
        return subprocess.run([str(pyvenv.bin_path(final / "venv", "python")), "-m", "beyondseo", *args],
                              cwd=project.root, env=env, capture_output=True, text=True, timeout=timeout), out
    except subprocess.TimeoutExpired as exc:
        raise SEOError(f"beyondseo {args[0]} timed out after {timeout}s") from exc


def capture_report(home: Path, bundle_dir, run_dir: Path) -> list:
    """BeyondSEO capture_quality per page of a run (inside the SEO venv), labelled by agylite.seo.evidence."""
    import json

    from ..seo import evidence
    _src, final = _final(home, bundle_dir)
    probe = Path(__file__).with_name("seo_probe.py")
    p = subprocess.run([str(pyvenv.bin_path(final / "venv", "python")), "-I", str(probe), str(run_dir)],
                       capture_output=True, text=True, timeout=300)
    if p.returncode:
        raise SEOError(f"capture report failed: {(p.stderr or p.stdout).strip()[-400:]}")
    rows = []
    for line in p.stdout.splitlines():
        row = json.loads(line)
        row["presence"] = evidence.label("presence", row["quality"])
        row["absence"] = evidence.label("absence", row["quality"])
        rows.append(row)
    return rows
