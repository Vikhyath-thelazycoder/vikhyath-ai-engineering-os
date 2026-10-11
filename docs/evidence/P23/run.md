# P23 evidence — Agent Office dashboard (2026-10-11)

- `vikhyath dashboard --port 8799 --idle-minutes 0.5` (this repository, scratch `VIKHYATH_HOME`) → "Agent Office for vikhyath-ai-engineering-os: http://127.0.0.1:8799/".
  - `/api/agents`: 31 seats with state/say/last from the real event log (e.g. Router "routed → 1 agents").
  - `/api/activity`: newest first, starting with "Dashboard started".
  - `/api/state`: branch `feat/v2-os-transformation`, bundle `495f026f381e`, verification `local-test-first`.
  - `/api/hosts`: claude-code INSTALLED (the user's v1.0.1 plugin), others FILES_PRESENT.
  - `/api/runtimes`: graphify not-installed, unlazy/uiuxpromax/seo ready.
  - `/` → 200 text/html; `/../config/dashboard.yaml` → 404.
- Tests (`tests/dashboard/test_dashboard.py`, 8): layout covers all 63 capabilities exactly once; security route → Security + Sec tests working, Mapper waiting, Specialists working (Agency source), sources listed; failed verification and risk alert → blocked with reasons; passed verification → idle "verify: PASSED"; blocked task → Planner blocked; Browser QA always disabled; Simplicity off, working only when routed; 30-minute-old work back to idle; server loopback-only, page and 5 endpoints 200, path escape 404, POST 405, idle exit with DASHBOARD_STARTED/DASHBOARD_SLEEPING events.
- `python -m unittest discover -s tests`: **236 OK, 3 skipped**.
