# P18 evidence — observability (2026-10-04)

Interpreter: `Python 3.14.7`. `<scratch>` = session scratch `VIKHYATH_HOME` with bundle `c98667e034f7`.

## What was built
- `vikhyath/events/schema.py`: doc 15 envelope (`schema_version, id, ts, event, severity, project_id, session_id, host, capabilities, bytes_loaded, est_tokens, duration_ms, details`); all 17 spec §30 events + BROWSER_FALLBACK_ACTIVATED, ISOLATION_VIOLATION_BLOCKED, RISK_DETECTED.
- `vikhyath/events/redact.py`: credential shapes (private keys, Authorization/Bearer, URL credentials, JWT, AWS, GitHub, Slack, Stripe, OpenAI, Anthropic, Google) and secret-named keys → `[REDACTED:<type>]`.
- `vikhyath/events/log.py`: `$VIKHYATH_HOME/projects/<id>/events/<day>.jsonl`, redacted before write, one `O_APPEND` write per line under the project's `events` lock, guard-checked; `emit` never raises into the observed operation.
- `vikhyath/events/rules_cel.py`: CEL-subset evaluator following Beacon's threat-rules spec (missing path = zero value; error absorption in `&&`/`||`; RE2 `(?i)` and `\x{…}` mapping; derived `gen_ai.tool.call.result_text` ported from `threatrules.ToolResultText`), session-scoped correlation (`window`, sequence by timestamp or `order: any`), embedded-test runner.
- Emission: bootstrap (SESSION_STARTED, PROJECT_DETECTED), route / `context --route` (DOMAIN_SELECTED, CAPABILITIES_SELECTED), `ContextLoader.finish` (CONTEXT_LOADED with bytes, est. tokens, files, cache hits), plan add/status (STATE_UPDATED, TASK_STARTED/BLOCKED/COMPLETED, VERIFICATION_STARTED/PASSED, PHASE_CHANGED), decisions and init (STATE_UPDATED), isolation guard (ISOLATION_VIOLATION_BLOCKED), `events observe` (RISK_DETECTED).
- CLI: `vikhyath events list [--tail --type --session]`, `events observe` (Beacon-shaped tool events on stdin, for the P19+ host adapters), `events rules [--test]`.

## Bundled Beacon rules
`vikhyath events rules --test`: **77 rules, 535/535 embedded tests pass** (21 ms). First run: 526/530 + 1 load error — fixed by porting Beacon's derived `result_text` field (4 tests) and RE2 `\x{HHHH}` escapes (1 rule); both follow `spec/threat-rules/SPEC.md` of the pinned upstream.

## Event sequence for one routed request (test + scratch demo)
`project init` → `bootstrap --session s1` → `context --route "Fix the payment webhook security."` → `plan add-task` → `set-status` IN_PROGRESS → READY_FOR_VERIFICATION → VERIFIED:
```
PROJECT_DETECTED, STATE_UPDATED, SESSION_STARTED, PROJECT_DETECTED, DOMAIN_SELECTED, CAPABILITIES_SELECTED,
CONTEXT_LOADED, STATE_UPDATED, TASK_STARTED, STATE_UPDATED, VERIFICATION_STARTED, STATE_UPDATED,
VERIFICATION_PASSED, STATE_UPDATED
```
(exact order asserted in `tests/events/test_events.py`). Demo on the scratch travel project with the real bundle:
```
SESSION_STARTED · PROJECT_DETECTED · DOMAIN_SELECTED · CAPABILITIES_SELECTED [engineering/security, …] ·
CONTEXT_LOADED [engineering/security, …] · RISK_DETECTED high (curl-pipe-to-shell, real Beacon rule)
```
The observed command contained `Authorization: Bearer abcdefgh12345`; `grep -c abcdefgh12345` over the event log and the observed-event buffer: **0** and **0**.

## Other checks (tests)
- Planted secrets of 11 kinds never survive `redact_text`; secret-named keys redacted whatever the value; `est_tokens` and ordinary text untouched; an emitted event with a Stripe key and a password contains neither on disk.
- 4 threads × 50 emits → 200 whole, valid lines.
- A blocked cross-project read writes one ISOLATION_VIOLATION_BLOCKED (severity high) in the acting project only.
- `events observe`: single-event rule fires once per rule and session (dedupe across calls); a correlation (`.env` read, then curl 30 s later) fires across two separate `observe` calls; the buffer is redacted.
- Test runs never touch the real `~/.vikhyath` (routing CLI tests now use a temporary home; verified `~/.vikhyath` does not exist after the suite).

## Suite
`python -m unittest discover -s tests`: **160 tests OK** (19 new). `vikhyath doctor` 45/0, `vikhyath validate --no-unittest` 19/0.
