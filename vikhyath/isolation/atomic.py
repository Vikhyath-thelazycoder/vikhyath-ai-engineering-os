"""Atomic file writes (doc 14 §7): temp file in the same directory, fsync, rename. Readers see the old or the new
file, never a partial one."""
import os
import secrets
from pathlib import Path

import yaml

_DUMPER = getattr(yaml, "CSafeDumper", yaml.SafeDumper)


def write_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.{os.getpid()}.{secrets.token_hex(4)}.tmp")
    try:
        with open(tmp, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        if tmp.exists():
            tmp.unlink()
    try:   # persist the rename itself (best effort; not supported on every platform)
        fd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)
    except OSError:
        pass


def write_text(path: Path, text: str) -> None:
    write_bytes(path, text.encode("utf-8"))


def write_yaml(path: Path, data) -> None:
    write_text(path, yaml.dump(data, Dumper=_DUMPER, sort_keys=False, allow_unicode=True, width=120))
