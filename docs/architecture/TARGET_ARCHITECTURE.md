# Agylite architecture

Agylite is one local core (the `agylite` Python package and CLI) with thin host adapters. Every host — Claude Code,
Codex, Cursor, Antigravity — calls the same CLI, so routing, context, state and verification behave identically
everywhere. No MCP server is used or configured.

```
host (Claude Code · Codex · Cursor · Antigravity)
  │  entry skills (skills/agylite-*) + SessionStart hook (Claude Code)
  ▼
agylite CLI ─ route ─ context ─ plan/state ─ verify ─ codebase ─ design ─ seo ─ media ─ dashboard ─ update
  │
  ├─ ~/.agylite/bundles/<id>/      curated upstream files + registry + provenance (built locally, offline after)
  ├─ ~/.agylite/runtimes/<name>-<lock>/   isolated engines (Graphify, BeyondSEO, Brag music) started per command
  ├─ ~/.agylite/projects/<id>/     per-project machine data: events, cache, graph, sessions
  └─ <project>/.agylite/           per-project owned state: state, plan index, decisions, evidence
```

## Components

| Component | Package | Document |
|---|---|---|
| Capability registry (63 capabilities, 9 domains) | `agylite/registry` | [CAPABILITY_MODEL](CAPABILITY_MODEL.md), [DOMAIN_MODEL](DOMAIN_MODEL.md) |
| Deterministic router | `agylite/routing` | [ROUTING_ARCHITECTURE](ROUTING_ARCHITECTURE.md) |
| Context engine (L0–L3, budgets, session cache) | `agylite/context` | [CONTEXT_ENGINE](CONTEXT_ENGINE.md) |
| Project state, plan, decisions, lifecycle | `agylite/project` | [PROJECT_STATE](PROJECT_STATE.md) |
| Isolation guard, locks, atomic writes | `agylite/isolation` | [MULTI_PROJECT_ISOLATION](MULTI_PROJECT_ISOLATION.md) |
| Bundle build, transforms, closure | `agylite/bundle` | [UPSTREAM_BUNDLING](UPSTREAM_BUNDLING.md), [PROVENANCE_SYSTEM](PROVENANCE_SYSTEM.md) |
| Update, rollback, gc | `agylite/update` | [UPDATE_ROLLBACK](UPDATE_ROLLBACK.md) |
| Local verification | `agylite/verify` | [TESTING_ARCHITECTURE](TESTING_ARCHITECTURE.md), [VERIFICATION_POLICY](VERIFICATION_POLICY.md) |
| Runtimes | `agylite/runtimes`, `agylite/codebase`, `agylite/seo`, `agylite/design` | [SEO_ARCHITECTURE](SEO_ARCHITECTURE.md) |
| Events, redaction, risk rules | `agylite/events` | [OBSERVABILITY](OBSERVABILITY.md) |
| Agent Office | `agylite/dashboard` | [DASHBOARD_ARCHITECTURE](DASHBOARD_ARCHITECTURE.md) |
| Host adapters | `agylite/adapters` | [HOST_ADAPTERS](HOST_ADAPTERS.md) |
| Security model | all | [SECURITY_MODEL](SECURITY_MODEL.md) |

## Principles (each enforced by tests or diagnostics)

1. **Load only what the task needs.** Hosts see a few short entry skills; everything else is routed and loaded in
   budgeted sections. Measured: ~915 est. tokens per turn vs ~31,800 for the same upstreams installed directly
   (`docs/benchmarks/RESULTS.md`).
2. **Deterministic first.** Routing is rules + tags + BM25 fallback, no model call (p95 0.34 ms).
3. **Local test-first verification.** Done means recorded evidence from tests, types, lint and build; never a browser,
   DevTools or a screenshot.
4. **No always-on behaviour.** No daemons, no upstream hooks; runtimes start per command; the dashboard exits when idle.
5. **Projects never touch each other.** A path guard, per-project locks and per-project data directories.
6. **Every bundled file is traceable** to an upstream repository, commit, path and hash, with its license.
