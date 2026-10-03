"""Vikhyath AI Engineering OS core."""
from importlib import metadata

from .paths import repo_root


def _version():
    version_file = repo_root() / "VERSION"
    if version_file.is_file():
        return version_file.read_text(encoding="utf-8").strip()
    try:
        return metadata.version("vikhyath")
    except metadata.PackageNotFoundError:
        return "unknown"


__version__ = _version()
