# Testing and local verification

```bash
agylite verify --plan          # what would run for the current change, and why
agylite verify [--task T-1.2]  # run it, rerun failures once, write evidence, update state
agylite test                   # impacted tests only
agylite verify --all           # full suites (release verification)
```

1. **Detect** the project's own commands (`agylite/verify/detect.py`): Python (pytest or unittest, mypy/pyright,
   ruff/flake8, bandit, compileall), Node (package.json scripts and tsc; E2E scripts recognised and excluded by
   default), Go, Rust. Nothing is installed.
2. **Select** (`select.py`): the tests `agylite codebase affected` relates to the change, narrowed per runner
   (pytest/unittest files, jest/vitest paths, go packages), each tagged unit / api / integration / idempotency /
   security / regression; plus typecheck, lint and build. The full suite runs only when nothing narrower is known,
   when impacted tests exceed the code-surface limit, or with `--all`.
3. **Run** (`run.py`): timeout per check; counts parsed from pytest, unittest, jest/vitest and go output; a short
   diagnosis from failing lines; a missing tool is BLOCKED, not FAILED; failed tests are rerun once and a pass on rerun
   is reported as flaky but stays FAILED.
4. **Evidence** (`evidence.py`): `<project>/.agylite/evidence/<time>.json`, validated against the policy's required
   fields; recorded as the project's last verification; VERIFICATION_STARTED/PASSED/FAILED events.

Example (tests/verify): a payment-webhook change selects webhook (api), signature and auth (security), idempotency and
integration-flow tests, not an unrelated reports test, plus the build check.

Agylite's own suite: `python -m unittest discover -s tests` (245 tests; the real-runtime Graphify tests are opt-in with
`AGYLITE_RUNTIME_TESTS=1`).
