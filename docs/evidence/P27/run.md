# P27 evidence — integration, offline, hosts (2026-10-11)

- `python -m unittest discover -s tests`: **246 OK, 3 skipped** (the 3 = opt-in real Graphify runtime tests).
- `AGYLITE_RUNTIME_TESTS=1 AGYLITE_TEST_BUNDLE=<scratch>/bundles/current python -m unittest tests.runtimes.test_graphify`: OK (installs Graphify from the bundle, builds a graph, affected/query/explain/path).
- `tests/integration/test_end_to_end.py` with `socket.connect` failing for any non-loopback address: project init → bootstrap (host claude-code) → route (security, lifecycle, impact, browser disabled) → context → codebase affected (structural fallback, related test found) → verify PASSED with evidence → plan T-1.1 → VERIFIED with that evidence → Agent Office: Browser QA disabled, QA "verify: PASSED" → events SESSION_STARTED … VERIFICATION_PASSED, TASK_STARTED → state in `.agylite/`.
- `agylite doctor` 50 passed / 0 failed / 11 warnings; `agylite validate` 23 passed / 0 failed; `agylite bundle verify` → `07cd36edb5d9: intact`; `agylite registry check` → 63 capabilities + bundle valid; `agylite adapters render --check` → current.
- `agylite adapters status`: claude-code, codex, cursor, antigravity → FILES_PRESENT (honest: v1.0.1 is the installed Claude plugin; other hosts absent).
- `agylite runtime status`: unlazy, uiuxpromax, seo, brag ready; graphify not installed in this home (tests install it separately).
