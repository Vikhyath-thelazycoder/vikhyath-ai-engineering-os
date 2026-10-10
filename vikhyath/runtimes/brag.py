"""Brag media runtime (P17, Q-4, D-041): launch videos from the bundled Brag skills.

`/brag-slim` is the default (one skill file; the model builds the video with tools already on the machine). Full
`/brag` is used only on explicit request AND when Hyperframes is already available locally (never fetched by the OS:
it needs the network and a browser). The music-cue analyser runs in its own venv (`runtimes/brag-<lock>`, librosa)
installed only on request. Media output is a deliverable in the project, never verification evidence (D-035).
"""
import json
import shutil
import subprocess
from pathlib import Path

from . import venv as pyvenv

TOOLS = ("ffmpeg", "ffprobe", "node", "npx", "python3", "uv")
MUSIC_DEPS = ("librosa>=0.10.2", "numpy>=1.26", "scipy>=1.11", "soundfile>=0.12")


class BragError(RuntimeError):
    pass


def skills_dir(bundle_dir: Path | None) -> Path | None:
    d = bundle_dir / "files" / "brag" / "skills" if bundle_dir else None
    return d if d and (d / "brag-slim" / "SKILL.md").is_file() else None


def hyperframes(project_root: Path) -> str | None:
    """Hyperframes already installed for this project or on PATH (no download)."""
    local = project_root / "node_modules" / ".bin" / "hyperframes"
    if local.exists():
        return str(local)
    return shutil.which("hyperframes")


def plan(project, bundle_dir, *, full=False) -> dict:
    skills = skills_dir(bundle_dir)
    if skills is None:
        raise BragError("no active bundle with the Brag skills")
    tools = {t: bool(shutil.which(t)) for t in TOOLS}
    hf = hyperframes(project.root)
    mode, why = "brag-slim", "default (Q-4): one skill, tools already on the machine"
    if full and hf:
        mode, why = "brag", f"explicitly requested; Hyperframes found at {hf}"
    elif full:
        why = "full /brag requested but Hyperframes is not installed locally; the OS does not fetch it (network + browser)"
    skill = skills / mode / "SKILL.md"
    missing = [t for t in ("ffmpeg",) if not tools[t]]
    return {"mode": mode, "why": why, "skill": f"files/brag/skills/{mode}/SKILL.md",
            "load": f"vikhyath context --file files/brag/skills/{mode}/SKILL.md", "skill_bytes": skill.stat().st_size,
            "tools": tools, "missing": missing, "output_dir": str(project.root / "brag-output"),
            "note": "media output is a deliverable, never verification evidence (config/verification.yaml)"}


def music_dir(home: Path, bundle_dir) -> tuple:
    skills = skills_dir(bundle_dir)
    if skills is None:
        raise BragError("no active bundle with the Brag skills")
    scripts = skills / "brag" / "scripts"
    return scripts, Path(home) / "runtimes" / f"brag-{pyvenv.lock_of(scripts, 'brag')}"


def install_music(home: Path, bundle_dir, log=print) -> dict:
    """Venv with the analyser's declared dependencies (pyproject has `package = false`, so deps are installed directly)."""
    scripts, final = music_dir(home, bundle_dir)
    if (final / "runtime.json").is_file():
        return json.loads((final / "runtime.json").read_text(encoding="utf-8"))
    shutil.rmtree(final, ignore_errors=True)
    final.mkdir(parents=True)
    try:
        subprocess.run([shutil.which("python3") or "python3", "-m", "venv", str(final / "venv")], check=True,
                       capture_output=True)
        log("installing the Brag music-cue analyser (librosa; network)…")
        p = subprocess.run([str(pyvenv.bin_path(final / "venv", "python")), "-m", "pip", "install", "-q",
                            "--disable-pip-version-check", *MUSIC_DEPS], capture_output=True, text=True)
        if p.returncode:
            raise BragError(f"pip install failed: {(p.stderr or p.stdout).strip()[-500:]}")
        info = {"runtime": "brag-music", "lock": final.name.split("-", 1)[1], "deps": list(MUSIC_DEPS)}
        (final / "runtime.json").write_text(json.dumps(info, indent=1) + "\n", encoding="utf-8")
        return info
    except BaseException:
        shutil.rmtree(final, ignore_errors=True)
        raise


def music_cues(home: Path, bundle_dir, audio: Path, out_dir: Path) -> subprocess.CompletedProcess:
    scripts, final = music_dir(home, bundle_dir)
    if not (final / "runtime.json").is_file():
        raise BragError("music-cue analyser not installed (`vikhyath runtime install brag`)")
    out_dir.mkdir(parents=True, exist_ok=True)
    return subprocess.run([str(pyvenv.bin_path(final / "venv", "python")), "-B", str(scripts / "analyze_music_cues.py"),
                           str(audio), "--output-json", str(out_dir / "music-cues.json"),
                           "--output-md", str(out_dir / "music-cues.md")], capture_output=True, text=True, timeout=600)


def health(home: Path, bundle_dir) -> dict:
    if skills_dir(bundle_dir) is None:
        return {"runtime": "brag", "status": "no-bundle", "reason": "no active bundle with the Brag skills"}
    _s, final = music_dir(home, bundle_dir)
    return {"runtime": "brag", "status": "ready", "mode": "brag-slim",
            "music_analyser": "installed" if (final / "runtime.json").is_file() else "not installed (optional)",
            "ffmpeg": bool(shutil.which("ffmpeg"))}
