"""Structural multi-project isolation (P11, spec §2.4, doc 14): path guard, per-project locks, atomic writes."""
from .atomic import write_bytes, write_text, write_yaml
from .guard import IsolationError, PathGuard, guard_for, on_violation
from .locks import LockTimeout, project_lock

__all__ = ["IsolationError", "LockTimeout", "PathGuard", "guard_for", "on_violation", "project_lock", "write_bytes",
           "write_text", "write_yaml"]
