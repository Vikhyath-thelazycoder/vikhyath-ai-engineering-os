"""Detect a project's own check commands (P15, D-035): tests, typecheck, lint, build — per toolchain, from its config.

Only commands the project already declares or that are standard for its toolchain are used; nothing is installed.
A project's own headless E2E suite is detected as kind `e2e` but never selected by default (it may start a browser).
"""
import json
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:   # pragma: no cover - Python 3.10
    tomllib = None

E2E_MARKERS = ("playwright", "cypress", "puppeteer", "webdriver", "selenium", "e2e")


@dataclass
class Check:
    kind: str                      # test | typecheck | lint | build | security | e2e
    name: str
    command: list
    toolchain: str
    selective: str | None = None   # how to pass selected tests: "pytest" | "unittest" | "node" | "go" | None
    cwd: str = "."
    notes: list = field(default_factory=list)


def _toml(path: Path) -> dict:
    if tomllib is None or not path.is_file():
        return {}
    try:
        return tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _python(root: Path):
    py = _toml(root / "pyproject.toml")
    has_code = any(root.glob("*.py")) or any(root.glob("*/**/*.py"))
    if not (py or (root / "setup.py").is_file() or (root / "requirements.txt").is_file() or has_code):
        return []
    exe = sys.executable
    tool = py.get("tool", {})
    checks = []
    reqs = ""
    for name in ("requirements.txt", "requirements-dev.txt"):
        if (root / name).is_file():
            reqs += (root / name).read_text(encoding="utf-8", errors="ignore")
    pytest_cfg = ("pytest" in tool or "pytest" in reqs or (root / "pytest.ini").is_file()
                  or (root / "conftest.py").is_file() or (root / "tests" / "conftest.py").is_file())
    if pytest_cfg:
        checks.append(Check("test", "pytest", [exe, "-m", "pytest", "-q"], "python", "pytest"))
    elif (root / "tests").is_dir() or any(root.glob("test_*.py")):
        start = "tests" if (root / "tests").is_dir() else "."
        checks.append(Check("test", "unittest", [exe, "-m", "unittest", "discover", "-s", start, "-t", "."],
                            "python", "unittest"))
    if "mypy" in tool or (root / "mypy.ini").is_file():
        checks.append(Check("typecheck", "mypy", [exe, "-m", "mypy", "."], "python"))
    if "pyright" in tool or (root / "pyrightconfig.json").is_file():
        checks.append(Check("typecheck", "pyright", ["pyright"], "python"))
    if "ruff" in tool or (root / "ruff.toml").is_file() or (root / ".ruff.toml").is_file():
        checks.append(Check("lint", "ruff", [exe, "-m", "ruff", "check", "."], "python"))
    elif (root / ".flake8").is_file():
        checks.append(Check("lint", "flake8", [exe, "-m", "flake8"], "python"))
    if "bandit" in tool:
        checks.append(Check("security", "bandit", [exe, "-m", "bandit", "-q", "-r", "."], "python"))
    checks.append(Check("build", "compileall", [exe, "-m", "compileall", "-q", "-x", r"(^|/)(\.|node_modules|venv)", "."],
                        "python"))
    return checks


def _node(root: Path):
    pkg = root / "package.json"
    if not pkg.is_file():
        return []
    try:
        scripts = (json.loads(pkg.read_text(encoding="utf-8")).get("scripts") or {})
    except (OSError, ValueError):
        return []
    pm = ("pnpm" if (root / "pnpm-lock.yaml").is_file() else "yarn" if (root / "yarn.lock").is_file()
          else "bun" if (root / "bun.lockb").is_file() or (root / "bun.lock").is_file() else "npm")
    run = [pm, "run"] if pm != "yarn" else ["yarn"]
    checks = []
    for name, body in scripts.items():
        low = f"{name} {body}".lower()
        is_e2e = any(m in low for m in E2E_MARKERS)
        if name == "test" or (name.startswith("test:") and not is_e2e):
            kind = "e2e" if is_e2e else "test"
            sel = "node" if any(r in body for r in ("jest", "vitest", "mocha", "node --test")) else None
            checks.append(Check(kind, name, [*run, name], "node", sel if kind == "test" else None))
        elif is_e2e:
            checks.append(Check("e2e", name, [*run, name], "node"))
        elif name in ("typecheck", "type-check", "types", "tsc") or body.strip().startswith("tsc"):
            checks.append(Check("typecheck", name, [*run, name], "node"))
        elif name in ("lint", "eslint") or name.startswith("lint:"):
            checks.append(Check("lint", name, [*run, name], "node"))
        elif name == "build":
            checks.append(Check("build", name, [*run, name], "node"))
    if not any(c.kind == "typecheck" for c in checks) and (root / "tsconfig.json").is_file():
        checks.append(Check("typecheck", "tsc", ["npx", "--no-install", "tsc", "--noEmit"], "node"))
    return checks


def _go(root: Path):
    if not (root / "go.mod").is_file():
        return []
    return [Check("test", "go test", ["go", "test", "./..."], "go", "go"),
            Check("lint", "go vet", ["go", "vet", "./..."], "go"),
            Check("build", "go build", ["go", "build", "./..."], "go")]


def _rust(root: Path):
    if not (root / "Cargo.toml").is_file():
        return []
    return [Check("test", "cargo test", ["cargo", "test"], "rust"),
            Check("lint", "cargo clippy", ["cargo", "clippy", "--", "-D", "warnings"], "rust"),
            Check("build", "cargo build", ["cargo", "build"], "rust")]


def detect(root: Path):
    """All checks this project declares, in policy order (config/verification.yaml `checks`)."""
    root = Path(root)
    checks = _python(root) + _node(root) + _go(root) + _rust(root)
    for c in checks:
        exe = c.command[0]
        if exe != sys.executable and shutil.which(exe) is None:
            c.notes.append(f"{exe} not found on PATH")
    order = {"test": 0, "security": 1, "typecheck": 2, "lint": 3, "build": 4, "e2e": 5}
    return sorted(checks, key=lambda c: order.get(c.kind, 9))
