# Multi-project isolation

Working on one project never reads or changes another.

- **Identity:** a project id from its git origin (or path); every API takes an explicit project handle, never a global
  "current project".
- **Path guard** (`agylite/isolation/guard.py`): allowed roots are the project, its own data dir
  (`~/.agylite/projects/<id>/`), the OS install and the bundle. Paths are resolved first (no `..` or symlink escape);
  a blocked access raises and emits ISOLATION_VIOLATION_BLOCKED.
- **Locks and atomic writes:** per-project locks for state, plan, events, graph and verification; files are written
  to a temporary name and renamed.
- **Caches and graphs** are keyed per project.

Tested: three interleaved projects with an audit hook on every file open → 0 cross-project reads; 4 × 25 concurrent
updates → no lost update; 300 concurrent reads → no partial file.
