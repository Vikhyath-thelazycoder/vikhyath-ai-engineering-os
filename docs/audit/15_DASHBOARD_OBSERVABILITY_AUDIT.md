# 15 — Dashboard & Observability Audit (Phase 3, spec §30–32, §72–73)

## Inputs from upstream (REFERENCE only; no UI copied)

| Source | Useful concept | Not taken |
|---|---|---|
| Agent Beacon | Versioned JSONL event envelope: `event.{kind,action,category,id}`, `session`, `harness`, `tool`, `gen_ai.usage` (tokens), `severity`; per-host hook payload parsers; 77 detection rules with tests | Go endpoint agent, cloud forwarding, browser extension, OTel collector |
| ECC | Stop-hook cost tracker (per-session token/cost), pre-compact state save, `ecc2` session store/state machine | Rust daemon, TUI, SQLite store, desktop notifications |
| gstack | `context-save`/`context-restore` structure; review dashboard idea | Telemetry, Supabase sync |

## Event model (P18)

- Append-only JSONL at `$VIKHYATH_HOME/projects/<id>/events/<yyyy-mm-dd>.jsonl` (per project; rotation by day).
- Envelope: `schema_version`, `ts`, `event` (one of SESSION_STARTED, PROJECT_DETECTED, DOMAIN_SELECTED, CAPABILITIES_SELECTED, CONTEXT_LOADED, TASK_STARTED, TASK_BLOCKED, TASK_COMPLETED, VERIFICATION_STARTED, VERIFICATION_PASSED, VERIFICATION_FAILED, STATE_UPDATED, PHASE_CHANGED, DASHBOARD_STARTED, DASHBOARD_SLEEPING, UPSTREAM_UPDATED, UPSTREAM_ROLLBACK, BROWSER_FALLBACK_ACTIVATED, ISOLATION_VIOLATION_BLOCKED, RISK_DETECTED), `project_id`, `session_id`, `host`, `capabilities[]`, `bytes_loaded`, `est_tokens`, `duration_ms`, `details{}`.
- Redaction before write: values matching secret patterns (keys/tokens/passwords/Authorization headers) are replaced with `[REDACTED:<type>]`. The same redactor runs on diagnostics output (§78–79).
- Risk detection: an OS evaluator for a CEL subset runs adapted Beacon rules over OS events. Each rule's embedded tests become unit tests.

## Dashboard (P23)

| Requirement | Design |
|---|---|
| Vikhyath-owned, data-driven (§31, §71) | Single static HTML/JS page bundled with the OS; reads JSON from the local server (projects, sessions, phase progress from `plan-index.yaml`, active/queued tasks, capability states, event stream, verification counts). |
| No daemon (§2.5, §32) | `vikhyath dashboard` starts a **stdlib HTTP server bound to 127.0.0.1** on a random free port and opens the browser. It exits after a configurable idle timeout (default 15 min without requests and no active session) or on `vikhyath dashboard stop`. A host SessionStart hook may start it only if the user enabled `dashboard.autostart`. |
| Lifecycle states | OFFLINE → STARTING → ACTIVE ⇄ IDLE → SLEEPING (process exited; state file says sleeping) → STOPPING; ERROR on bind/IO failure. Recorded in `$VIKHYATH_HOME/dashboard.json` and as DASHBOARD_* events. |
| Not the execution engine | Read-only views plus at most "open plan item" and "stop dashboard" controls; no task execution from the UI. |
| Agent states (§72) | SLEEPING, IDLE, QUEUED, STARTING, WORKING, WAITING, BLOCKED, VERIFYING, COMPLETED, FAILED: derived from session records + events. |
| Capability states (§73) | UNAVAILABLE, AVAILABLE, SELECTED, LOADING, ACTIVE, CACHED, DISABLED, FAILED: derived from registry + routing/context events. |
| Security | Localhost bind only, random port, per-launch token in the URL, no external assets. |

## Acceptance (P23)

Start, idle and auto-stop measured. Data comes from fixture projects (no hardcoded UI state, §71). Kill the process mid-session → state shows SLEEPING/ERROR correctly on the next start. Startup time recorded in benchmarks.
