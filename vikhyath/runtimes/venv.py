"""Shared isolated-venv mechanics for Python runtimes (D-016, D-037): lock, in-place build, completion marker."""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from ..isolation import atomic

CODE_SUFFIXES = (".py", "pyproject.toml", "uv.lock")


class VenvError(RuntimeError):
    pass


def bin_path(venv: Path, name: str) -> Path:
    return venv / ("Scripts" if os.name == "nt" else "bin") / (name + (".exe" if os.name == "nt" else ""))


def lock_of(src: Path, repo: str) -> str:
    """Pins + sha256 of the bundled code files (from the bundle index, no reads); docs do not change the lock."""
    h = hashlib.sha256()
    for name in ("pyproject.toml", "uv.lock"):
        f = src / name
        if f.is_file():
            h.update(name.encode() + b"\0" + f.read_bytes())
    index = src.parent.parent / "index.json"
    if index.is_file():
        files = json.loads(index.read_text(encoding="utf-8")).get("files", {})
        prefix = f"files/{repo}/"
        for dest in sorted(d for d in files if d.startswith(prefix) and d.endswith(CODE_SUFFIXES)):
            h.update(f"{dest}\0{files[dest]['sha256']}\n".encode())
    else:   # unbundled source (tests): file list and sizes
        for p in sorted(src.rglob("*")):
            if p.is_file() and p.name.endswith(CODE_SUFFIXES):
                h.update(f"{p.relative_to(src)}\0{p.stat().st_size}\n".encode())
    return h.hexdigest()[:12]


def install(final: Path, src: Path, *, name: str, lock: str, extras=(), python=None, version_cmd=None,
            remove_scripts=(), log=print) -> dict:
    """Build the venv in place (venv scripts embed their path) from a temporary copy of the source (pip writes build/
    and egg-info into it; the bundle stays clean). `runtime.json` is written last as the completion marker."""
    if (final / "runtime.json").is_file():
        return json.loads((final / "runtime.json").read_text(encoding="utf-8"))
    shutil.rmtree(final, ignore_errors=True)
    final.mkdir(parents=True)
    start = time.perf_counter()
    py = bin_path(final / "venv", "python")
    try:
        subprocess.run([python or sys.executable, "-m", "venv", str(final / "venv")], check=True, capture_output=True)
        with tempfile.TemporaryDirectory() as tmp:
            build_src = Path(tmp) / name
            shutil.copytree(src, build_src)
            if not (build_src / "README.md").exists():   # declared `readme` not bundled (docs excluded)
                (build_src / "README.md").write_text(f"{name} (bundled by Vikhyath OS)\n", encoding="utf-8")
            spec = str(build_src) + (f"[{','.join(extras)}]" if extras else "")
            log(f"installing {name} runtime {lock} (pip{', extras ' + ','.join(extras) if extras else ', core only'})…")
            p = subprocess.run([str(py), "-m", "pip", "install", "-q", "--disable-pip-version-check", spec],
                               capture_output=True, text=True)
            if p.returncode:
                raise VenvError(f"pip install failed: {(p.stderr or p.stdout).strip()[-800:]}")
        version = (subprocess.run([str(py), *version_cmd], capture_output=True, text=True).stdout.strip()
                   if version_cmd else "")
        for script in remove_scripts:
            bin_path(final / "venv", script).unlink(missing_ok=True)
        info = {"runtime": name, "lock": lock, "version": version, "extras": list(extras),
                "python": sys.version.split()[0], "installed": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "install_seconds": round(time.perf_counter() - start, 1), "source": str(src)}
        atomic.write_text(final / "runtime.json", json.dumps(info, indent=1) + "\n")
        return info
    except BaseException:
        shutil.rmtree(final, ignore_errors=True)
        raise


def add_extras(final: Path, src: Path, name: str, extras, log=print) -> dict:
    """Install optional extras into an existing runtime (explicit only) and record them."""
    info = json.loads((final / "runtime.json").read_text(encoding="utf-8"))
    missing = [e for e in extras if e not in info.get("extras", [])]
    if not missing:
        return info
    py = bin_path(final / "venv", "python")
    with tempfile.TemporaryDirectory() as tmp:
        build_src = Path(tmp) / name
        shutil.copytree(src, build_src)
        if not (build_src / "README.md").exists():
            (build_src / "README.md").write_text(f"{name} (bundled by Vikhyath OS)\n", encoding="utf-8")
        log(f"adding extras {','.join(missing)} to {name}…")
        p = subprocess.run([str(py), "-m", "pip", "install", "-q", "--disable-pip-version-check",
                            f"{build_src}[{','.join(missing)}]"], capture_output=True, text=True)
        if p.returncode:
            raise VenvError(f"pip install failed: {(p.stderr or p.stdout).strip()[-800:]}")
    info["extras"] = sorted({*info.get("extras", []), *missing})
    atomic.write_text(final / "runtime.json", json.dumps(info, indent=1) + "\n")
    return info
