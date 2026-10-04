"""Per-project, per-session context cache (spec §17).

Keyed by (project_id, session_id) through its location, then by file path + content identity. Bundle files are
identified by the sha256 recorded in the bundle index (immutable, no stat or read needed); project files by
(size, mtime_ns) from one stat. A hit means the content is already in this session's context, so the loader returns
a short marker instead of rereading and resending the file.
"""
import json
import os
from datetime import datetime, timezone
from pathlib import Path


def _now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class SessionCache:
    def __init__(self, path: Path, project_id: str, session_id: str):
        self.path = path
        self.project_id = project_id
        self.session_id = session_id
        self.data = {"project_id": project_id, "session_id": session_id, "created": _now(), "entries": {},
                     "active_capabilities": [], "load_log": []}
        if path.is_file():
            loaded = json.loads(path.read_text(encoding="utf-8"))
            if loaded.get("project_id") != project_id or loaded.get("session_id") != session_id:
                raise ValueError(f"cache {path} belongs to another project/session")
            self.data = loaded

    def hit(self, key: str, *, sha256: str | None = None, stat: os.stat_result | None = None, sections=()):
        """True when `key` was loaded in this session with the same content identity and covered `sections`."""
        e = self.data["entries"].get(key)
        if not e:
            return False
        if sha256 is not None and e.get("sha256") != sha256:
            return False
        if stat is not None and (e.get("size"), e.get("mtime_ns")) != (stat.st_size, stat.st_mtime_ns):
            return False
        return set(sections) <= set(e.get("sections") or [])

    def record(self, key: str, *, level: str, sha256: str | None = None, stat: os.stat_result | None = None,
               sections=()):
        prev = self.data["entries"].get(key) or {}
        same = (prev.get("sha256"), prev.get("size"), prev.get("mtime_ns")) == (
            sha256, stat.st_size if stat else None, stat.st_mtime_ns if stat else None)
        merged = sorted(set(sections) | (set(prev.get("sections") or []) if same else set()))
        self.data["entries"][key] = {"sha256": sha256, "size": stat.st_size if stat else None,
                                     "mtime_ns": stat.st_mtime_ns if stat else None, "sections": merged,
                                     "level": level, "loaded_at": _now()}

    def log(self, item: dict):
        self.data["load_log"].append(item)
        del self.data["load_log"][:-500]   # keep the log bounded

    def set_active(self, capabilities):
        self.data["active_capabilities"] = list(capabilities)

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(f".{os.getpid()}.tmp")
        tmp.write_text(json.dumps(self.data, indent=1, sort_keys=True), encoding="utf-8")
        os.replace(tmp, self.path)
