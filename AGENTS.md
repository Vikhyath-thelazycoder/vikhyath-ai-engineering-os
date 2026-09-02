# Vikhyath AI Engineering OS — Agent Instructions

This repository is the **Vikhyath AI Engineering OS**, a thin orchestration/plugin layer.

## Core Behavior

1. **Progressive activation**: Only load skills relevant to the current task
2. **No MCP**: Do not use or suggest MCP servers
3. **No upstream copies**: External capabilities remain external dependencies
4. **Context efficiency**: Minimize token usage by activating only what's needed

## Available Skills

Refer to `skills/` for Vikhyath-specific routing and orchestration skills:

- `vikhyath-engineering/` — Engineering task routing via ECC
- `vikhyath-routing/` — Capability classification and activation
- `vikhyath-production/` — Production readiness via Addy + gstack
- `vikhyath-security/` — Security-focused capability activation
- `vikhyath-review/` — Code review and quality orchestration

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

See `config/capabilities.yaml` for the capability registry and `config/routing.yaml` for routing rules.
