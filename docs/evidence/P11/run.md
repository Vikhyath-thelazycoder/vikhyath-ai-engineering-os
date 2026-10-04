# P11 evidence — multi-project isolation (2026-10-04)

Interpreter: `Python 3.14.7`, macOS (APFS, `fcntl.flock`). All fixtures are temporary directories with their own `VIKHYATH_HOME`.

## What was built
- `vikhyath/isolation/guard.py`: a project may touch only its root, its own `$VIKHYATH_HOME/projects/<id>/`, and OS files (this plugin, `bundles/`, bundle-derived `cache/`). Paths are resolved first (`..` and symlinks cannot escape). Violations raise `IsolationError` and are reported to registered hooks (P18 turns them into `ISOLATION_VIOLATION_BLOCKED` events).
- `vikhyath/isolation/locks.py`: per-project named `flock` locks under the project's data dir (re-entrant per thread, timeout → `LockTimeout`).
- `vikhyath/isolation/atomic.py`: temp-file + fsync + rename for every OS write.
- Wired in: `ContextLoader.read` (guard), session cache and context index (atomic), `state` (guard + `state` lock + atomic), `plan_index` (guard), `reconcile` (`plan` lock; the index is re-read inside the lock), `decisions` (`decisions` lock), `lifecycle.start_session`, `register`.

## Acceptance (doc 14 tests)
| Test | Result |
|---|---|
| Three projects (AuricVista, JAVALI, client C) with distinct decisions and a `.env` credential each; six interleaved turns (bootstrap, two routed context loads, plan reconcile, decision list) recorded with a `sys.addaudithook("open")` hook | **0 opens** under another project's root or data dir; other projects' files byte-identical after each turn; no other project's decision text and no `sk_live_` credential in any output. A turn on A: 464 opens = 37 in A's root, 9 in A's data dir, 418 OS files (cards, configs, bundle). Each project's own decisions do appear. |
| Guard: B's `decisions.yaml`, B's data dir, `../javali/.env`, `/etc/hosts`, and a symlink in A pointing at B's DESIGN.md | all 5 blocked with `IsolationError`, each reported once to the violation hook; own docs, own data, bundle and OS cards allowed |
| State/plan APIs with a plan path of `../javali/...` or a write to B's state | blocked |
| Same-project concurrency: 4 processes × 25 locked increments of one state field | **100** (no lost update) |
| 3 processes × 5 `add_task` on the same phase | 16 unique task ids (1 + 15), 15 history rows |
| Writer thread rewriting a 60 KB state while the reader parses it 300× | 0 parse errors, 0 incomplete documents, no stray temp files |
| Lock held in project A: same lock times out in 0.2 s; project B's lock and A's `plan` lock are free; nested acquire in one thread works | pass |
| Identical request + identical session id in A and B | separate cache files under each project's data dir; B is all misses after A; A's cache file refuses B's project id |
| Same repo name, different origins | different project ids and data dirs |

## Suite
`python -m unittest discover -s tests`: **141 tests OK** (11 new in `tests/isolation/`).
