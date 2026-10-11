# Agent Office (dashboard)

```bash
agylite dashboard [--open] [--demo] [--port N] [--idle-minutes M]
```

A pixel office where every capability is an agent at a desk in its domain's room (design D-043, mockup
`docs/design/agent-office-mockup.html`).

- **Layout:** `config/dashboard.yaml` — 6 rooms and 31 seats covering all 63 capabilities exactly once.
- **States** (`agylite/dashboard/agents.py`) from the project's event log: working (selected or loading context),
  waiting (a dependency of a selected capability), blocked with the reason (failed verification, blocked task, risk
  alert), idle (no event for 10 minutes), off (Simplicity until asked), disabled (Browser QA, by policy). Speech bubbles
  show the latest event text.
- **API** (read-only JSON): `/api/agents`, `/api/activity`, `/api/state`, `/api/hosts`, `/api/runtimes`.
- **Server:** standard-library HTTP on 127.0.0.1 only, random free port, POST refused, path escapes refused, strict
  content security policy, no web fonts (works offline). It exits after 10 minutes without a page poll or on Ctrl+C,
  emitting DASHBOARD_STARTED / DASHBOARD_SLEEPING. `--demo` replays sample events instead of the log.
