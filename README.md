# Vikhyath AI Engineering OS

> A thin, portable plugin and orchestration layer that selectively routes AI coding agent tasks to specialized engineering capabilities from proven external repositories.

## What is this?

Vikhyath AI Engineering OS is a **thin orchestration plugin**, not a monolithic framework or always-on daemon. It coordinates multiple high-quality external engineering repositories so the right capability is routed at the right time — without loading unnecessary instructions into context, without duplicating upstream code, and without introducing MCP.

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
            (plugin.json / Agent Plugins 1.0)
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

## Supported Hosts & Packaging

| Host | Support Status | Packaging / Manifest |
|---|---|---|
| **Codex** | ✅ Verified | `.codex-plugin/plugin.json` & `.agents/plugins/marketplace.json` |
| **Antigravity** | ✅ Verified | `plugin.json` (root portable manifest) & `.agents/skills/vikhyath-os/` |
| **Claude Code** | ✅ Verified | `.claude-plugin/plugin.json` & `.claude-plugin/marketplace.json` |

## Capabilities Matrix

All external dependencies are version-pinned by full 40-character Git commit SHAs:

| Capability | Upstream Source | Pinned SHA | Role | Priority | Routing Trigger |
|---|---|---|---|---|---|
| **ECC** | [affaan-m/ECC](https://github.com/affaan-m/ECC) | `ca185ef5...` | Engineering foundation | 100 | Engineering tasks (planning, TDD, verification) |
| **Graphify** | [Graphify-Labs/graphify](https://github.com/Graphify-Labs/graphify) | `91f4d120...` | Codebase intelligence | 90 | Complex / unfamiliar repositories |
| **Unlazy** | [Leonxlnx/unlazy](https://github.com/Leonxlnx/unlazy) | `473d4b80...` | Completion discipline | 80 | Substantial / exhaustive tasks |
| **Addy Skills** | [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | `d2c37ef6...` | Production engineering | 75 | Hardening, testing, performance |
| **Agency Agents** | [msitarzewski/agency-agents](https://github.com/msitarzewski/agency-agents) | `3c958888...` | Specialist agents | 70 | Domain-specific expertise on demand |
| **gstack** | [garrytan/gstack](https://github.com/garrytan/gstack) | `0d1bd561...` | Product & release review | 60 | Review, QA, shipping workflows |
| **OpenDesign** | [nexu-io/open-design](https://github.com/nexu-io/open-design) | `349748ee...` | Design capability | 50 | UI/UX and design systems |
| **Ponytail** | [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) | `2ed6c52c...` | Simplicity review | 40 | Explicit request (Default: OFF) |
| **Karpathy Skills** | [multica-ai/andrej-karpathy-skills](https://github.com/multica-ai/andrej-karpathy-skills) | `2c606141...` | Engineering principles | 30 | Reference principles |

## How Routing Works

The router answers: **"What capabilities are actually required for this task?"**

```text
Task
 → Classify task intent
 → Select minimum capability set
 → Instruct host to route execution to selected capabilities
 → Verify completion
 → Clear active capability context
```

| Task | Routed Capabilities | Inactive Capabilities |
|---|---|---|
| Simple bug fix | ECC | Everything else |
| Large unfamiliar repo | ECC + Graphify | Unlazy, OpenDesign, Ponytail |
| Security auth change | ECC + Addy security | Ponytail, OpenDesign |
| Large feature | ECC + Graphify + Unlazy | Ponytail |
| UI redesign | ECC + OpenDesign | Graphify, Unlazy |
| Production release | ECC + gstack review | Ponytail, OpenDesign |
| Simplicity review | Ponytail | Everything else |

## Installation

### 1. Codex

Add the marketplace and install the plugin:

```bash
# Step 1: Add the marketplace
codex plugin marketplace add Vikhyath-thelazycoder/vikhyath-ai-engineering-os

# Step 2: Install the plugin
codex plugin install vikhyath-ai-engineering-os@vikhyath-marketplace
```

### 2. Claude Code

Add the marketplace and install the plugin:

```bash
# Step 1: Add the marketplace
claude plugin marketplace add Vikhyath-thelazycoder/vikhyath-ai-engineering-os

# Step 2: Install the plugin
claude plugin install vikhyath-ai-engineering-os@vikhyath-marketplace
```

### 3. Antigravity

Clone or reference this repository within your workspace root. Antigravity discovers the portable [`plugin.json`](plugin.json) and workspace skill adapter at [`.agents/skills/vikhyath-os/`](.agents/skills/vikhyath-os/SKILL.md) automatically.

### External Capabilities Setup

Vikhyath routes to external capabilities; it does not bundle their source code. Install or reference the external tools as needed:

```bash
# ECC (primary engineering foundation)
codex plugin marketplace add affaan-m/ECC && codex plugin install ecc@ecc-marketplace

# Addy Agent Skills (production engineering)
codex plugin marketplace add addyosmani/agent-skills && codex plugin install agent-skills

# Ponytail (simplicity / YAGNI review — on-demand)
codex plugin marketplace add DietrichGebert/ponytail && codex plugin install ponytail

# Graphify (codebase intelligence CLI tool)
pip install graphify-ai
```

See `integrations/` for detailed metadata and host-specific options for each capability.

## Conflict Resolution

When capabilities provide overlapping or conflicting advice, the deterministic 8-level hierarchy resolves priority:

1. **User requirements** (always authoritative)
2. **Project security / safety constraints**
3. **Project architecture**
4. **ECC engineering workflow**
5. **Specialized security / testing guidance (Addy)**
6. **Domain specialist agents (Agency)**
7. **Product / review workflows (gstack)**
8. **Simplicity optimization (Ponytail)**

## Diagnostics & Validation

```bash
# Structural and integrity diagnostic check
./scripts/doctor

# Pre-release validation test suite (offline)
./scripts/validate

# Online GitHub commit SHA verification
./scripts/validate --online

# Capability and context benchmark
./scripts/benchmark

# Python unit test discovery
python3 -m unittest discover -s tests -p "test_*.py"
```

## Updating & Rollback

```bash
# Update Vikhyath OS plugin via Codex
codex plugin update vikhyath-ai-engineering-os@vikhyath-marketplace

# Rollback or pin to a specific release
codex plugin install vikhyath-ai-engineering-os@vikhyath-marketplace#v1.0.1
```

## Absolute Guardrails & Non-Negotiables

- ❌ **NO MCP**: Zero MCP servers, `.mcp.json`, or MCP adapters.
- ❌ **NO Upstream Copies**: No vendor/third-party duplicated repositories.
- ❌ **NO Giant Prompt**: No monolithic `SYSTEM.md` or `MASTER_PROMPT.md`.
- ❌ **NO Always-On Swarm**: Single-responsibility progressive activation.
- ❌ **NO Daemons / Background Services**: Pure thin plugin architecture.

## Benchmark Analysis & Context Efficiency

- **Verified Capabilities**: 9 external repositories coordinated through a unified schema.
- **Progressive Activation**: Only 1–3 capabilities active per typical task session.
- **Estimated Context Reduction**: Architecture-level estimate of ~60% to 85% fewer instructions loaded per task compared to all-loaded baselines (*not directly measured with token instrumentation*).

## License

MIT — see [LICENSE](LICENSE).

## Version

Version `1.0.1` — see [VERSION](VERSION) and [CHANGELOG.md](CHANGELOG.md).
