"""Per-project file locks (doc 14 §7): concurrent sessions on the same project serialize read-modify-write cycles.

Lock files live in the project's machine-local data dir (`$VIKHYATH_HOME/projects/<id>/locks/<name>.lock`), so
different projects never contend. `flock` locks belong to the open file, so they also exclude other threads of the
same process; a thread that already holds a lock may re-enter it.
"""
import os
import threading
import time
from contextlib import contextmanager
from pathlib import Path

try:
    import fcntl
except ImportError:   # Windows
    fcntl = None
    import msvcrt

_held = threading.local()


class LockTimeout(TimeoutError):
    pass


def _try_lock(fd) -> bool:
    try:
        if fcntl:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        else:
            msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
        return True
    except OSError:
        return False


def _unlock(fd):
    if fcntl:
        fcntl.flock(fd, fcntl.LOCK_UN)
    else:
        os.lseek(fd, 0, os.SEEK_SET)
        msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)


def lock_path(project, name: str) -> Path:
    return project.data_dir / "locks" / f"{name}.lock"


@contextmanager
def project_lock(project, name: str = "state", timeout: float = 30.0):
    path = lock_path(project, name)
    held = getattr(_held, "paths", None)
    if held is None:
        held = _held.paths = {}
    key = str(path)
    if held.get(key):
        held[key] += 1
        try:
            yield
        finally:
            held[key] -= 1
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(path, os.O_RDWR | os.O_CREAT, 0o600)
    deadline = time.monotonic() + timeout
    delay = 0.001
    try:
        while not _try_lock(fd):
            if time.monotonic() > deadline:
                raise LockTimeout(f"could not lock {path} within {timeout}s (another session is writing)")
            time.sleep(delay)
            delay = min(delay * 2, 0.05)
        held[key] = 1
        try:
            yield
        finally:
            held.pop(key, None)
            _unlock(fd)
    finally:
        os.close(fd)
