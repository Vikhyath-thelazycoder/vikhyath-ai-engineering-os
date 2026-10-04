"""Project lifecycle (spec §19, §25): completion states, new-vs-existing detection, stack detection, session start."""
import json
import re
from pathlib import Path

from .state import now, read_yaml, write_yaml

# Spec §25: never just DONE / NOT DONE.
COMPLETION_STATES = ("NOT_STARTED", "PLANNED", "IN_PROGRESS", "PARTIALLY_COMPLETE", "BLOCKED",
                     "READY_FOR_VERIFICATION", "VERIFIED", "COMPLETED", "INTENTIONALLY_DEFERRED")
ACTIVE_STATES = ("IN_PROGRESS", "BLOCKED", "READY_FOR_VERIFICATION", "PARTIALLY_COMPLETE")
DONE_STATES = ("VERIFIED", "COMPLETED")
# COMPLETED only after verification evidence exists (spec §25, completion discipline).
TRANSITIONS = {
    "NOT_STARTED": {"PLANNED", "IN_PROGRESS", "INTENTIONALLY_DEFERRED", "BLOCKED"},
    "PLANNED": {"IN_PROGRESS", "BLOCKED", "INTENTIONALLY_DEFERRED", "NOT_STARTED"},
    "IN_PROGRESS": {"PARTIALLY_COMPLETE", "BLOCKED", "READY_FOR_VERIFICATION", "INTENTIONALLY_DEFERRED", "PLANNED"},
    "PARTIALLY_COMPLETE": {"IN_PROGRESS", "BLOCKED", "READY_FOR_VERIFICATION", "INTENTIONALLY_DEFERRED"},
    "BLOCKED": {"IN_PROGRESS", "PLANNED", "INTENTIONALLY_DEFERRED"},
    "READY_FOR_VERIFICATION": {"VERIFIED", "IN_PROGRESS", "BLOCKED"},
    "VERIFIED": {"COMPLETED", "IN_PROGRESS"},
    "COMPLETED": {"IN_PROGRESS"},
    "INTENTIONALLY_DEFERRED": {"PLANNED", "IN_PROGRESS"},
}

CODE_SUFFIXES = {".py", ".js", ".jsx", ".ts", ".tsx", ".go", ".rs", ".java", ".kt", ".rb", ".php", ".cs", ".swift",
                 ".vue", ".svelte", ".dart", ".c", ".cc", ".cpp", ".h", ".scala", ".ex", ".exs", ".html", ".css"}
MANIFESTS = ("package.json", "pyproject.toml", "requirements.txt", "go.mod", "Cargo.toml", "Gemfile", "pom.xml",
             "build.gradle", "build.gradle.kts", "composer.json", "pubspec.yaml", "Package.swift", "mix.exs")
SKIP_DIRS = {".git", ".vikhyath", "node_modules", ".venv", "venv", "__pycache__", "dist", "build", "docs", ".next"}
STACK_MARKERS = {   # dependency name → stack tag
    "react": "react", "next": "next", "vue": "vue", "nuxt": "nuxt", "svelte": "svelte", "@angular/core": "angular",
    "express": "express", "@nestjs/core": "nestjs", "fastify": "fastify", "prisma": "prisma", "@prisma/client": "prisma",
    "django": "django", "flask": "flask", "fastapi": "fastapi", "sqlalchemy": "sqlalchemy", "psycopg2": "postgres",
    "psycopg": "postgres", "pg": "postgres", "mongoose": "mongodb", "stripe": "stripe", "tailwindcss": "tailwind",
}
PYTHON_MARKERS = ("django", "flask", "fastapi", "sqlalchemy", "psycopg2", "psycopg", "stripe")


class TransitionError(ValueError):
    pass


def check_transition(old: str, new: str, evidence: str | None = None):
    if new not in COMPLETION_STATES:
        raise TransitionError(f"unknown status {new}; use one of {', '.join(COMPLETION_STATES)}")
    if old == new:
        return
    if old in TRANSITIONS and new not in TRANSITIONS[old]:
        raise TransitionError(f"{old} → {new} is not allowed (allowed: {', '.join(sorted(TRANSITIONS[old]))})")
    if new in DONE_STATES and not evidence:
        raise TransitionError(f"{new} needs verification evidence (--evidence)")


def _walk(root: Path, depth=3):
    stack = [(root, 0)]
    while stack:
        d, level = stack.pop()
        try:
            entries = list(d.iterdir())
        except OSError:
            continue
        for e in entries:
            if e.is_dir():
                if level < depth and e.name not in SKIP_DIRS and not e.name.startswith("."):
                    stack.append((e, level + 1))
            else:
                yield e


def detect_stage(root: Path, state=None) -> str:
    """Recorded stage wins; otherwise existing if a manifest or source file exists (spec §19.2)."""
    if state and state.get("project", {}).get("stage"):
        return state["project"]["stage"]
    if any((root / m).is_file() for m in MANIFESTS):
        return "existing"
    return "existing" if any(f.suffix in CODE_SUFFIXES for f in _walk(root)) else "new"


def detect_stack(root: Path):
    """Stack tags from manifests (language + notable frameworks); reads only manifest files."""
    tags = []
    pkg = root / "package.json"
    if pkg.is_file():
        tags.append("node")
        try:
            data = json.loads(pkg.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            data = {}
        deps = {**(data.get("dependencies") or {}), **(data.get("devDependencies") or {})}
        tags += [STACK_MARKERS[d] for d in deps if d in STACK_MARKERS]
        if "typescript" in deps:
            tags.append("typescript")
    py_text = ""
    for name in ("pyproject.toml", "requirements.txt"):
        if (root / name).is_file():
            py_text += (root / name).read_text(encoding="utf-8", errors="ignore").lower()
    if py_text:
        tags.append("python")
        tags += [STACK_MARKERS[dep] for dep in PYTHON_MARKERS
                 if re.search(rf"(?<![\w-]){re.escape(dep)}(?![\w-])", py_text)]
    for manifest, tag in (("go.mod", "go"), ("Cargo.toml", "rust"), ("Gemfile", "ruby"), ("pom.xml", "java"),
                          ("build.gradle", "java"), ("build.gradle.kts", "kotlin"), ("composer.json", "php"),
                          ("pubspec.yaml", "dart"), ("Package.swift", "swift"), ("mix.exs", "elixir")):
        if (root / manifest).is_file():
            tags.append(tag)
    return list(dict.fromkeys(tags))


def start_session(project, session_id: str, host: str):
    """Record a session (spec §19.1) under the project's machine-local data dir; returns the session record."""
    path = project.data_dir / "sessions" / session_id / "session.yaml"
    record = read_yaml(path)
    if record is None:
        record = {"session_id": session_id, "project_id": project.project_id, "host": host, "started": now(),
                  "root": str(project.root)}
        write_yaml(path, record)
        record = dict(record, new=True)
    return record
