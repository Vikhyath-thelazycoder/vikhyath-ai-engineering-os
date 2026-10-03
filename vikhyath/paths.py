"""Filesystem locations used by the core (D-010)."""
import os
from pathlib import Path


def repo_root() -> Path:
    """The plugin repository this package was loaded from."""
    return Path(__file__).resolve().parents[1]


def vikhyath_home() -> Path:
    """Machine-local OS home: $VIKHYATH_HOME, default ~/.vikhyath."""
    env = os.environ.get("VIKHYATH_HOME")
    return Path(env).expanduser() if env else Path.home() / ".vikhyath"


def bundles_dir() -> Path:
    return vikhyath_home() / "bundles"


def current_bundle() -> Path | None:
    """Resolve the active bundle pointer, or None before the first build."""
    pointer = bundles_dir() / "current"
    return pointer.resolve() if pointer.exists() else None
