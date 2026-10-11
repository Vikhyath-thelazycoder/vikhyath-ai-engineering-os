# Observability

- **Event log:** `~/.agylite/projects/<id>/events/<day>.jsonl`, one JSON object per line (doc 15 envelope: id, time,
  event, severity, project, session, host, capabilities, bytes, est. tokens, duration, details). Every value passes
  through the redactor before it is written (private keys, bearer tokens, URL credentials, JWTs, cloud and vendor
  keys, secret-named fields).
- **Event types:** session/project, routing (DOMAIN_SELECTED, CAPABILITIES_SELECTED), CONTEXT_LOADED, tasks and phases,
  verification, dashboard, upstream update/rollback, BROWSER_EXCEPTION_REQUESTED, ISOLATION_VIOLATION_BLOCKED,
  RISK_DETECTED.
- **Risk detection:** `agylite events observe` evaluates host tool events against the bundled Beacon rules (77 rules,
  CEL subset with session correlation; every rule's own tests pass). Alerts are logged, not blocking.
- **Diagnostics:** `agylite doctor` (structure, manifests, no-MCP, registry, runtimes, host environment, supply chain —
  output redacted), `agylite validate`, `agylite benchmark --compare`.

```bash
agylite events list [--type CONTEXT_LOADED] [--tail 50]
agylite events rules --test
```
