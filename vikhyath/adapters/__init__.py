"""Host adapters (P19–P22): packaging and status only; every host calls the same CLI (D-042)."""
from .base import HOSTS, record_runtime
from .hosts import ADAPTERS, all_adapters, get

__all__ = ["ADAPTERS", "HOSTS", "all_adapters", "get", "record_runtime"]
