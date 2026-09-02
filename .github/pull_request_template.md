## Summary of Changes

A clear, concise explanation of what this pull request changes and why.

## Motivation & Context

Fixes #(issue number) or explains why the change is necessary.

## Core Architectural Guardrails Checklist

Please confirm that your changes strictly adhere to the non-negotiable architectural principles:

- [ ] **NO MCP**: Zero MCP servers, zero `.mcp.json` files, zero MCP configs added.
- [ ] **NO Vendoring**: No third-party source files or upstream repositories copied into this repo.
- [ ] **Thin Layer Preserved**: No daemons, background services, or always-running swarms introduced.
- [ ] **Progressive Activation**: Only relevant capabilities are activated for tasks; no global prompt bloat.
- [ ] **Dependency Pinning**: Any new external capability is pinned to a full 40-character hexadecimal Git commit SHA.
- [ ] **Deterministic Priorities**: Routing rules and conflict hierarchies remain consistent with `config/priorities.yaml`.

## Testing & Validation Checklist

- [ ] `python3 -m unittest discover -s tests -p "test_*.py"` passes with 0 failures
- [ ] `./scripts/doctor` passes with 0 errors
- [ ] `./scripts/validate` passes with 0 failures
- [ ] `./scripts/validate --online` verified (if modifying capability SHAs)
- [ ] `./scripts/benchmark` verified
- [ ] Documentation (README.md, CONTRIBUTING.md, host manifests) updated if relevant
