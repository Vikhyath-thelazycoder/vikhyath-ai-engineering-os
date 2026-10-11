"""Filesystem locations used by the core (D-010)."""
import os
from pathlib import Path


def repo_root() -> Path:
    """The plugin repository this package was loaded from."""
    return Path(__file__).resolve().parents[1]


def agylite_home() -> Path:
    """Machine-local OS home: $AGYLITE_HOME, else the legacy $VIKHYATH_HOME (D-044), else ~/.agylite — or an existing
    pre-rename ~/.vikhyath when ~/.agylite does not exist yet (nothing is moved automatically)."""
    env = os.environ.get("AGYLITE_HOME") or os.environ.get("VIKHYATH_HOME")
    if env:
        return Path(env).expanduser()
    new, legacy = Path.home() / ".agylite", Path.home() / ".vikhyath"
    return legacy if legacy.is_dir() and not new.exists() else new


def bundles_dir() -> Path:
    return agylite_home() / "bundles"


def current_bundle() -> Path | None:
    """Resolve the active bundle pointer, or None before the first build."""
    pointer = bundles_dir() / "current"
    return pointer.resolve() if pointer.exists() else None
