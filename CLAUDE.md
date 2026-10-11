# Agylite — Claude Code instructions

This repository is Agylite, a local engineering OS for coding agents (one CLI, one curated bundle, no MCP).

- Start from `agylite route "<request>"` and load only the routed capabilities with `agylite context <ids>`.
- Follow the route's lifecycle; verify with `agylite verify` and record evidence. No browser or screenshot verification.
- Do not suggest or enable MCP servers.
- The living plan is `docs/plan/IMPLEMENTATION_PLAN.md` ("Resume here" section); decisions are in
  `docs/audit/21_AUDIT_DECISIONS.md`; architecture in `docs/architecture/`.
- Tests: `python -m unittest discover -s tests`. Diagnostics: `agylite doctor`, `agylite validate`.

## Install

```bash
claude plugin marketplace add Vikhyath-thelazycoder/vikhyath-ai-engineering-os
claude plugin install agylite@agylite-marketplace
scripts/install          # central install into ~/.agylite and the local bundle
```
