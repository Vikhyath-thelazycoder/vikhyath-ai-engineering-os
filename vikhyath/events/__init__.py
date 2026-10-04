"""Observability (P18, spec §30, §78–79, doc 15): event envelope, redaction, per-project event log, Beacon rules."""
from .log import emit, install_hooks, read

__all__ = ["emit", "install_hooks", "read"]
