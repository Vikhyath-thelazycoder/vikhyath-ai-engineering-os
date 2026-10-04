"""Path guard (doc 14 §4, spec §2.4, §70 I): a project's operations may touch only

- its own root (`<project>/…`, including `.vikhyath/`),
- its own machine-local data (`$VIKHYATH_HOME/projects/<same id>/…`),
- the OS itself (this plugin's files, the installed bundles, bundle-derived caches under `$VIKHYATH_HOME/cache`).

Paths are resolved first, so `..` and symlinks cannot escape. Anything else — another project's root or data, the
user's home, system files — raises IsolationError and is reported to the registered violation hooks (P18 events).
"""
from pathlib import Path

from ..paths import repo_root


class IsolationError(PermissionError):
    def __init__(self, path, reason):
        super().__init__(f"isolation: {path} is outside this project's allowed roots ({reason})")
        self.path = str(path)
        self.reason = reason


_violation_hooks = []


def on_violation(callback):
    """Register callback(project, path, reason, mode); used by observability to emit ISOLATION_VIOLATION_BLOCKED."""
    if callback not in _violation_hooks:
        _violation_hooks.append(callback)
    return callback


def _within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


class PathGuard:
    def __init__(self, project, bundle_dir: Path | None = None, extra_roots=()):
        self.project = project
        self.projects_dir = (project.home / "projects").resolve()
        self.own_data = project.data_dir.resolve()
        self.roots = [project.root.resolve(), self.own_data, repo_root().resolve(),
                      (project.home / "bundles").resolve(), (project.home / "cache").resolve()]
        if bundle_dir is not None:
            self.roots.append(bundle_dir.resolve())
        self.roots += [Path(r).resolve() for r in extra_roots]

    def check(self, path, mode: str = "read") -> Path:
        p = Path(path).expanduser().resolve()
        reason = None
        if _within(p, self.projects_dir) and not _within(p, self.own_data):
            reason = "another project's machine-local data"
        elif not any(_within(p, r) for r in self.roots):
            reason = "not in the project, its data dir, or the OS bundle"
        if reason:
            for hook in list(_violation_hooks):
                try:
                    hook(self.project, str(p), reason, mode)
                except Exception:   # an observer must never turn a blocked access into a crash
                    pass
            raise IsolationError(p, reason)
        return p


def guard_for(project, bundle_dir: Path | None = None) -> PathGuard:
    return PathGuard(project, bundle_dir)
