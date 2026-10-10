"""Graphify runtime wrapper (P12, D-016, SEC-08/09, D-021).

Installed from the active bundle's `files/graphify` into `$VIKHYATH_HOME/runtimes/graphify-<lock>/` (own venv, no
extras), started per command, with `GRAPHIFY_OUT` pointing at the project's machine-local data dir so nothing is
written into the project. Only update/query/path/explain/affected are allowed; hook/install/watch/serve, the MCP
server and LLM extraction are never reachable through the OS, and provider API keys are not passed to the process.
"""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from ..isolation import atomic
from ..isolation.locks import project_lock

ALLOWED = ("update", "query", "path", "explain", "affected")
BLOCKED_REASON = {
    "hook": "installs git hooks with a detached background rebuild (SEC-08)",
    "install": "writes rule blocks into project CLAUDE.md/AGENTS.md (SEC-08)",
    "uninstall": "edits project host files (SEC-08)",
    "watch": "starts a background file watcher (§2.5)",
    "serve": "starts the MCP server (§2.1, D-021)",
    "extract": "LLM extraction is opt-in only (SEC-09)",
    "label": "LLM community naming is opt-in only (SEC-09)",
}
# The OS owns where the graph lives; callers may not redirect reads or writes.
RESERVED_FLAGS = ("--graph", "--out", "--output", "--memory-dir")
_SECRET_ENV = re.compile(r"(API_KEY|_TOKEN|SECRET|PASSWORD|CREDENTIAL)", re.I)
PROBE = Path(__file__).with_name("graphify_probe.py")
META = "vikhyath-graph.json"
CODE_SUFFIXES = (".py", "pyproject.toml", "uv.lock")
UPDATE_TIMEOUT = 600
QUERY_TIMEOUT = 120


class GraphifyError(RuntimeError):
    pass


class GraphifyBlocked(GraphifyError):
    pass


def source_dir(bundle_dir: Path | None) -> Path | None:
    src = bundle_dir / "files" / "graphify" if bundle_dir else None
    return src if src and (src / "pyproject.toml").is_file() else None


def lock_of(src: Path) -> str:
    """Runtime lock = the bundled Graphify code (sha256 from the bundle index, no reads) + the dependency pins, so a new
    pin or a changed code rule gets a new runtime directory; documentation rewrites do not."""
    h = hashlib.sha256()
    for name in ("pyproject.toml", "uv.lock"):
        f = src / name
        if f.is_file():
            h.update(name.encode() + b"\0" + f.read_bytes())
    index = src.parent.parent / "index.json"
    if index.is_file():
        files = json.loads(index.read_text(encoding="utf-8")).get("files", {})
        prefix = "files/graphify/"
        for dest in sorted(d for d in files if d.startswith(prefix) and d.endswith(CODE_SUFFIXES)):
            h.update(f"{dest}\0{files[dest]['sha256']}\n".encode())
    else:   # unbundled source (tests): file list and sizes
        for p in sorted(src.rglob("*")):
            if p.is_file() and p.name.endswith(CODE_SUFFIXES):
                h.update(f"{p.relative_to(src)}\0{p.stat().st_size}\n".encode())
    return h.hexdigest()[:12]


def runtime_dir(home: Path, lock: str) -> Path:
    return Path(home) / "runtimes" / f"graphify-{lock}"


def _bin(venv: Path, name: str) -> Path:
    return venv / ("Scripts" if os.name == "nt" else "bin") / (name + (".exe" if os.name == "nt" else ""))


def graph_dir(project) -> Path:
    return project.data_dir / "graph"


def _env(out_dir: Path):
    env = {k: v for k, v in os.environ.items() if not _SECRET_ENV.search(k)}
    env["GRAPHIFY_OUT"] = str(out_dir)
    env.pop("PYTHONPATH", None)
    return env


def check_command(sub: str, args=()):
    if sub not in ALLOWED:
        why = BLOCKED_REASON.get(sub, "not on the OS allowlist")
        raise GraphifyBlocked(f"graphify {sub} is blocked by the OS wrapper: {why}. Allowed: {', '.join(ALLOWED)}")
    for a in args:
        if a.split("=", 1)[0] in RESERVED_FLAGS:
            raise GraphifyBlocked(f"{a.split('=', 1)[0]} is set by the OS (graph lives in the project data dir)")


def install(home: Path, src: Path, python: str | None = None, log=print) -> dict:
    """Create the venv and install Graphify (core deps only). A venv cannot be moved (its scripts embed the path), so it
    is built in place and `runtime.json` is written last: a directory without it is incomplete and is rebuilt."""
    lock = lock_of(src)
    final = runtime_dir(home, lock)
    if (final / "runtime.json").is_file():
        return json.loads((final / "runtime.json").read_text(encoding="utf-8"))
    shutil.rmtree(final, ignore_errors=True)
    final.mkdir(parents=True)
    start = time.perf_counter()
    try:
        subprocess.run([python or sys.executable, "-m", "venv", str(final / "venv")], check=True, capture_output=True)
        with tempfile.TemporaryDirectory() as tmp:   # pip writes build/ and egg-info into the source: keep the bundle clean
            build_src = Path(tmp) / "graphify"
            shutil.copytree(src, build_src)
            log(f"installing graphify runtime {lock} (pip, core dependencies only)…")
            p = subprocess.run([str(_bin(final / "venv", "python")), "-m", "pip", "install", "-q",
                                "--disable-pip-version-check", str(build_src)], capture_output=True, text=True)
            if p.returncode:
                raise GraphifyError(f"pip install failed: {(p.stderr or p.stdout).strip()[-800:]}")
        version = subprocess.run([str(_bin(final / "venv", "python")), "-m", "graphify", "--version"],
                                 capture_output=True, text=True).stdout.strip()
        info = {"runtime": "graphify", "lock": lock, "version": version, "python": sys.version.split()[0],
                "installed": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "install_seconds": round(time.perf_counter() - start, 1), "source": str(src)}
        # D-021/D-037: no MCP entry point in the runtime (the mcp extra is not installed either).
        _bin(final / "venv", "graphify-mcp").unlink(missing_ok=True)
        atomic.write_text(final / "runtime.json", json.dumps(info, indent=1) + "\n")
        return info
    except BaseException:
        shutil.rmtree(final, ignore_errors=True)
        raise


def health(home: Path, bundle_dir: Path | None) -> dict:
    """ready | not-installed | broken | no-bundle, with the reason a fallback would be used (§74, MR-09)."""
    src = source_dir(bundle_dir)
    if src is None:
        return {"runtime": "graphify", "status": "no-bundle", "reason": "no active bundle with files/graphify"}
    lock = lock_of(src)
    venv = runtime_dir(home, lock) / "venv"
    base = {"runtime": "graphify", "lock": lock, "path": str(venv.parent)}
    if not (venv.parent / "runtime.json").is_file():
        return {**base, "status": "not-installed", "reason": "run `vikhyath runtime install graphify`"}
    p = subprocess.run([str(_bin(venv, "python")), "-I", "-c", "import graphify.affected, networkx, tree_sitter"],
                       capture_output=True, text=True)
    if p.returncode:
        return {**base, "status": "broken", "reason": (p.stderr.strip().splitlines() or ["import failed"])[-1]}
    info = json.loads((venv.parent / "runtime.json").read_text(encoding="utf-8"))
    return {**base, "status": "ready", "version": info.get("version")}


class Graphify:
    """One project's view of an installed runtime. All paths come from the ProjectRef (no global project)."""

    def __init__(self, project, home: Path, bundle_dir: Path | None):
        self.project = project
        src = source_dir(bundle_dir)
        if src is None:
            raise GraphifyError("graph-based analysis unavailable: no active bundle with files/graphify")
        self.venv = runtime_dir(home, lock_of(src)) / "venv"
        if not (self.venv.parent / "runtime.json").is_file():
            raise GraphifyError("graph-based analysis unavailable: graphify runtime not installed "
                                "(`vikhyath runtime install graphify`)")
        self.out = graph_dir(project)

    @property
    def graph_json(self) -> Path:
        return self.out / "graph.json"

    def _run(self, sub, args=(), timeout=QUERY_TIMEOUT):
        check_command(sub, args)
        self.out.mkdir(parents=True, exist_ok=True)
        extra = [] if sub == "update" else ["--graph", str(self.graph_json)]
        try:
            return subprocess.run([str(_bin(self.venv, "python")), "-m", "graphify", sub, *args, *extra],
                                  cwd=self.project.root, env=_env(self.out), capture_output=True, text=True, timeout=timeout)
        except subprocess.TimeoutExpired as exc:
            raise GraphifyError(f"graphify {sub} timed out after {timeout}s") from exc

    def meta(self) -> dict | None:
        f = self.out / META
        return json.loads(f.read_text(encoding="utf-8")) if f.is_file() else None

    def ensure_graph(self, fingerprint: str, force=False) -> dict:
        """`graphify update` only when the project's code changed since the last build (under the project lock)."""
        with project_lock(self.project, "graph", timeout=UPDATE_TIMEOUT):
            meta = self.meta()
            if not force and meta and meta.get("fingerprint") == fingerprint and self.graph_json.is_file():
                return {**meta, "rebuilt": False}
            start = time.perf_counter()
            p = self._run("update", [".", *(["--force"] if force else [])], timeout=UPDATE_TIMEOUT)
            if p.returncode or not self.graph_json.is_file():
                raise GraphifyError(f"graphify update failed: {(p.stderr or p.stdout).strip()[-500:]}")
            meta = {"fingerprint": fingerprint, "updated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    "update_ms": round((time.perf_counter() - start) * 1000)}
            atomic.write_text(self.out / META, json.dumps(meta, indent=1) + "\n")
            return {**meta, "rebuilt": True}

    def affected(self, paths, depth=2) -> dict:
        p = subprocess.run([str(_bin(self.venv, "python")), "-I", str(PROBE), str(self.graph_json),
                            str(self.project.root), str(depth), *paths], cwd=self.project.root,
                           env=_env(self.out), capture_output=True, text=True, timeout=QUERY_TIMEOUT)
        if p.returncode:
            raise GraphifyError(f"graphify affected failed: {(p.stderr or p.stdout).strip()[-500:]}")
        return json.loads(p.stdout)

    def passthrough(self, sub, args) -> subprocess.CompletedProcess:
        """query / path / explain against the project's graph (output already scoped by Graphify's budget)."""
        if sub in ("update", "affected"):
            raise GraphifyBlocked(f"use `vikhyath codebase {sub}` (the OS manages staleness and the code surface)")
        return self._run(sub, args)
