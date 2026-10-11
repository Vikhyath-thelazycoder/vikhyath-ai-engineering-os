# Agylite — Agent Instructions

This repository is the **Agylite**, a thin orchestration/plugin layer.

## Core Behavior

1. **Progressive activation**: Only load skills relevant to the current task
2. **No MCP**: Do not use or suggest MCP servers
3. **No upstream copies**: External capabilities remain external dependencies
4. **Context efficiency**: Minimize token usage by activating only what's needed

## Available Skills

Refer to `skills/` for Agylite-specific routing and orchestration skills:

- `agylite-engineering/` — Engineering task routing via ECC
- `agylite-routing/` — Capability classification and activation
- `agylite-production/` — Production readiness via Addy + gstack
- `agylite-security/` — Security-focused capability activation
- `agylite-review/` — Code review and quality orchestration

## Routing Logic

When presented with a task, classify it and activate only the relevant capabilities:

- **Engineering tasks** → ECC
- **Complex codebase** → ECC + Graphify
- **Security-sensitive** → ECC + Addy security + security specialist
- **Large implementation** → ECC + Unlazy
- **Design work** → ECC + OpenDesign
- **Release/review** → ECC + gstack
- **Simplicity audit** → Ponytail (explicit only)

## Conflict Hierarchy

1. User requirements
2. Project security/safety
3. Project architecture
4. ECC engineering workflow
5. Specialized security/testing
6. Domain specialists
7. Product/review workflows
8. Simplicity optimization

## Configuration

See `capabilities/` (one `card.yaml` per capability; `agylite registry list`) for the capability registry and `config/routing.yaml` for routing rules (run `agylite route "<request>"`).
