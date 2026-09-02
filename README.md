# Vikhyath AI Engineering OS

> A plugin-based orchestration layer that selectively activates specialized engineering capabilities from proven external repositories.

## What is this?

Vikhyath AI Engineering OS is a **thin router/plugin**, not a framework. It coordinates multiple high-quality external engineering repositories so the right capability activates at the right time — without loading everything into context, without duplicating upstream code, and without requiring MCP.

## Core Principle

```
Many specialized capabilities → one thin router → one plugin interface → only what is needed → better work
```

## Architecture

```
                         GITHUB
                            │
                            ▼
             Vikhyath AI Engineering OS
                            │
                     Plugin Layer
                            │
             ┌──────────────┼──────────────┐
             ▼              ▼              ▼
           Codex       Antigravity     Claude Code
             │              │              │
             └──────────────┼──────────────┘
                            ▼
                    Vikhyath Router
                            │
                    Capability Registry
                            │
              Progressive Activation
                            │
       ┌────────┬────────┬────────┬─────────┐
       ▼        ▼        ▼        ▼         ▼
      ECC     Graphify  Agency   Addy    gstack
       │        │        │        │         │
       └────────┴────────┴────────┴─────────┘
                            │
                   Conditional capabilities
                            │
                 Unlazy / Ponytail /
                 Karpathy / OpenDesign
```

## Supported Hosts

| Host | Support Level | Integration |
|---|---|---|
| **Codex** | ✅ First-class | `.codex-plugin/plugin.json` |
| **Antigravity** | ✅ First-class | `.agents/skills/` |
| **Claude Code** | ✅ First-class | `.claude-plugin/plugin.json`, `CLAUDE.md` |

## Capabilities

| Capability | Source | Role | Priority | Activation |
|---|---|---|---|---|
| ECC | [affaan-m/ECC](https://github.com/affaan-m/ECC) | Engineering foundation | 100 | Engineering tasks |
| Graphify | [Graphify-Labs/graphify](https://github.com/Graphify-Labs/graphify) | Codebase intelligence | 90 | Complex codebase tasks |
| Unlazy | [Leonxlnx/unlazy](https://github.com/Leonxlnx/unlazy) | Completion discipline | 80 | Substantial tasks |
| Addy Agent Skills | [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | Production engineering | 75 | Relevant engineering tasks |
| Agency Agents | [msitarzewski/agency-agents](https://github.com/msitarzewski/agency-agents) | Specialist perspectives | 70 | Specialist needed |
| gstack | [garrytan/gstack](https://github.com/garrytan/gstack) | Product/release review | 60 | Review/release tasks |
| OpenDesign | [nexu-io/open-design](https://github.com/nexu-io/open-design) | Design capability | 50 | Design tasks |
| Ponytail | [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) | Simplicity review | 40 | Explicit request |
| Karpathy Skills | [multica-ai/andrej-karpathy-skills](https://github.com/multica-ai/andrej-karpathy-skills) | Engineering principles | 30 | Reference |

## How Routing Works

The router answers: **"What capabilities are actually required for this task?"**

| Task | Activated | NOT Activated |
|---|---|---|
| Simple bug fix | ECC | Everything else |
| Large unfamiliar repo | ECC + Graphify | Unlazy, OpenDesign |
| Security auth change | ECC + Addy security | Ponytail, OpenDesign |
| Large feature | ECC + Graphify + Unlazy | Ponytail |
| UI redesign | ECC + OpenDesign | Graphify, Unlazy |
| Production release | ECC + gstack review | Ponytail, OpenDesign |
| Simplicity review | Ponytail | Everything else |

## Installation

### Codex

```bash
codex plugin install Vikhyath-thelazycoder/vikhyath-ai-engineering-os --trust
```

### Claude Code

```bash
claude plugin install Vikhyath-thelazycoder/vikhyath-ai-engineering-os
```

### Antigravity

Clone or reference this repository and the `.agents/` directory will be discovered automatically when set as a workspace.

### External Capabilities

Each external capability has its own installation mechanism. Vikhyath routes to them — it does not bundle them.

Install the capabilities you need:

```bash
# ECC (engineering foundation — recommended)
codex plugin install affaan-m/ECC --trust

# Addy Agent Skills (production engineering)
codex plugin install addyosmani/agent-skills --trust

# Ponytail (simplicity review — on-demand)
codex plugin install DietrichGebert/ponytail --trust

# Graphify (codebase intelligence)
pip install graphify-ai
```

See `integrations/` for detailed integration metadata for each capability.

## Context Management

This OS does **NOT** load all skills, agents, or documentation into every request. Instead:

```
Task → Classify → Select capabilities → Activate only relevant skills → Execute → Verify → Unload
```

This is the key value proposition: **optimize the context window, persist everything else**.

## What This Is NOT

- ❌ Not a standalone daemon or background service
- ❌ Not an MCP server or MCP adapter
- ❌ Not a copy of upstream repositories
- ❌ Not a giant always-loaded prompt
- ❌ Not an always-on multi-agent swarm
- ❌ Not a replacement for any individual capability

## Conflict Resolution

When capabilities provide conflicting guidance:

1. User requirements
2. Project security/safety constraints
3. Project architecture
4. ECC engineering workflow
5. Specialized security/testing guidance
6. Domain specialist agents
7. Product/review workflows
8. Simplicity optimization

## Diagnostics

```bash
# Validate repository structure and configuration
./scripts/doctor

# Run validation suite
./scripts/validate

# Run capability benchmark
./scripts/benchmark
```

## Updating

```bash
# Update the Vikhyath OS plugin
codex plugin update vikhyath-ai-engineering-os

# Check dependency versions
./scripts/doctor
```

## Rolling Back

The `VERSION` file and `CHANGELOG.md` track releases. Pin to a specific version:

```bash
codex plugin install Vikhyath-thelazycoder/vikhyath-ai-engineering-os@v1.0.0
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Follow the existing patterns in `skills/`, `integrations/`, `config/`
4. Run `./scripts/validate` before submitting
5. Submit a pull request

### Guidelines

- Do NOT introduce MCP
- Do NOT copy upstream repositories
- Do NOT create giant always-loaded prompts
- Keep the orchestration layer thin
- Version-pin all external dependencies
- Test across all three target hosts

## License

MIT — see [LICENSE](LICENSE).

## Version

See [VERSION](VERSION) and [CHANGELOG](CHANGELOG.md).
