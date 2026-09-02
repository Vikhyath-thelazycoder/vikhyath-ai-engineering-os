# Vikhyath AI Engineering OS

> A thin, portable orchestration plugin and control layer that selectively routes AI coding agent tasks to specialized engineering capabilities from proven external repositories.

[![CI](https://github.com/Vikhyath-thelazycoder/vikhyath-ai-engineering-os/actions/workflows/ci.yml/badge.svg)](https://github.com/Vikhyath-thelazycoder/vikhyath-ai-engineering-os/actions/workflows/ci.yml)
[![Version](https://img.shields.io/badge/version-1.0.1-blue.svg)](VERSION)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Strictly NO MCP](https://img.shields.io/badge/MCP-Strictly%20Prohibited-red.svg)](#16-no-mcp-statement)
[![Agent Plugins 1.0.0](https://img.shields.io/badge/standard-Agent%20Plugins%201.0.0-purple.svg)](plugin.json)

---

## Table of Contents

1. [What Vikhyath AI Engineering OS Is](#1-what-vikhyath-ai-engineering-os-is)
2. [What Problem It Solves](#2-what-problem-it-solves)
3. [Architecture Overview](#3-architecture-overview)
4. [Capability Routing Model](#4-capability-routing-model)
5. [Supported Capabilities](#5-supported-capabilities)
6. [Why Capabilities Are Activated Progressively](#6-why-capabilities-are-activated-progressively)
7. [Supported Hosts](#7-supported-hosts)
8. [Installation](#8-installation)
9. [First-Use Example](#9-first-use-example)
10. [Example Tasks and Expected Routing](#10-example-tasks-and-expected-routing)
11. [Updating](#11-updating)
12. [Uninstalling](#12-uninstalling)
13. [Troubleshooting](#13-troubleshooting)
14. [Development & Contribution Instructions](#14-development--contribution-instructions)
15. [Security Model](#15-security-model)
16. [No-MCP Statement](#16-no-mcp-statement)
17. [License](#17-license)
18. [Project Status & Version](#18-project-status--version)

---

## 1. What Vikhyath AI Engineering OS Is

**Vikhyath AI Engineering OS** is a thin, portable orchestration plugin for AI coding agents. Rather than bundling or duplicating external code, it serves as an intelligent control and routing layer across major AI coding hosts—including **OpenAI Codex**, **Google Antigravity**, and **Anthropic Claude Code**.

When you assign a task to your AI agent, Vikhyath OS analyzes the task intent and selectively routes execution to proven, specialized external capabilities (such as ECC for engineering foundation, Graphify for codebase intelligence, Addy Agent Skills for production hardening, and gstack for release workflows).

Key characteristics:
- **Thin Orchestration Layer**: Pure declarative routing and instructions—not a monolithic framework.
- **Zero Always-On Swarms or Daemons**: No background services, no persistent processes, no polling daemons.
- **Plugin-Only Architecture**: Implements the [Agent Plugins 1.0.0](https://agent-plugins.org/schemas/1.0.0/plugin.schema.json) standard.
- **External Dependencies Stay External**: All external capabilities remain in their upstream repositories; nothing is copied or vendored.

---

## 2. What Problem It Solves

Modern AI coding agents face three critical challenges when using external developer skills:

1. **Context Window Bloat & Cognitive Degradation**:
   Loading dozens of skills, agent personas, and rulebooks into every task fills the model's context window with irrelevant guidance. This leads to conflicting instructions, hallucinated workflows, higher latency, and increased token costs.
2. **Vendoring & Fragmentation Anti-Pattern**:
   Copy-pasting external tools into individual repositories results in immediate code rot, difficult upstream updates, and license attribution issues.
3. **Monolithic Framework Overkill**:
   Heavy frameworks that require dedicated background daemons or complex socket configurations introduce operational fragility and security risks.

**The Vikhyath OS Solution**:
A unified, portable plugin that dynamically routes tasks to the minimal required capability set just-in-time, keeping context clean, instructions sharp, and external dependencies strictly external.

---

## 3. Architecture Overview

```text
                           GITHUB
                   (Source of Truth)
                           │
                           ▼
              Vikhyath AI Engineering OS
                           │
                 Portable Plugin Layer
            (Agent Plugins 1.0 Specification)
                           │
            ┌──────────────┼──────────────┐
            ▼              ▼              ▼
          Codex       Antigravity    Claude Code
            │              │              │
            └──────────────┼──────────────┘
                           ▼
                    Vikhyath Router
                           │
                  Capability Registry
               (Pinned 40-character SHAs)
                           │
                Progressive Activation
                           │
      ┌───────────┬────────┴─────────┬───────────┐
      ▼           ▼                  ▼           ▼
     ECC       Graphify            Addy        gstack
 (Engineering (Codebase          (Production  (Product &
  Foundation)  Intelligence)      Hardening)   Release)
      │           │                  │           │
      └───────────┴────────┬─────────┴───────────┘
                           │
                 Conditional / On-Demand
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
           Unlazy       Ponytail     Agency /
        (Completion   (Simplicity   OpenDesign /
         Discipline)    Audit)       Karpathy
```

### Core Architectural Tenets
- **GitHub is the Source of Truth**: Upstream repositories are referenced by exact 40-character Git commit SHAs.
- **Zero Vendoring**: Upstream code is never copied or bundled into this repository.
- **Progressive Activation**: The router activates only the minimal capability set necessary for the task at hand.
- **Deterministic Priority Hierarchy**: Ambiguities and overlapping guidelines are resolved via an 8-level precedence model.
- **Zero MCP**: Absolute prohibition of Model Context Protocol servers, adapters, or configurations.

---

## 4. Capability Routing Model

When an agent receives a prompt, the Vikhyath OS Router follows a five-step lifecycle:

```text
Task Prompt
    │
    ▼
1. Classify Intent ────────► Match signals against config/routing.yaml
    │
    ▼
2. Select Capabilities ────► Identify minimum viable capability set
    │
    ▼
3. Route Execution ────────► Instruct host agent with active capability instructions
    │
    ▼
4. Verify Completion ──────► Validate against task acceptance criteria
    │
    ▼
5. Unload Context ─────────► Clear active instructions for subsequent turns
```

### Conflict Resolution Hierarchy

When active capabilities offer overlapping or conflicting guidance, the deterministic 8-level hierarchy in `config/priorities.yaml` governs:

1. **User Requirements** (Always authoritative)
2. **Project Security & Safety Constraints**
3. **Project Architecture Decisions**
4. **ECC Engineering Workflow Methodology** (Priority 100)
5. **Specialized Security & Testing Guidance — Addy** (Priority 75)
6. **Domain Specialist Agents — Agency** (Priority 70)
7. **Product & Review Workflows — gstack** (Priority 60)
8. **Simplicity Optimization — Ponytail** (Priority 40, explicit request only)

---

## 5. Supported Capabilities

All 9 external capabilities are version-pinned using full 40-character cryptographic Git commit SHAs:

| Capability | Upstream Source | Pinned Commit SHA | Role | Priority | Default State | Activation Trigger |
|---|---|---|---|---|---|---|
| **ECC** | [affaan-m/ECC](https://github.com/affaan-m/ECC) | `ca185ef5f7667078a1e70a763bd3a9c71c48acf0` | Engineering Foundation | 100 | **ON** | Engineering, TDD, planning, verification |
| **Graphify** | [Graphify-Labs/graphify](https://github.com/Graphify-Labs/graphify) | `91f4d120b630ee35c79bf3c75ccd186870a808f9` | Codebase Intelligence | 90 | Conditional | Complex or unfamiliar repos, dependency tracing |
| **Unlazy** | [Leonxlnx/unlazy](https://github.com/Leonxlnx/unlazy) | `473d4b80421c36d733042434cd4b938f81a19ef1` | Completion Discipline | 80 | Conditional | Exhaustive, multi-file implementations |
| **Addy Skills** | [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | `d2c37ef6225dd8726cdd369a8030307f48592d26` | Production Engineering | 75 | Conditional | Hardening, security, testing, performance |
| **Agency Agents** | [msitarzewski/agency-agents](https://github.com/msitarzewski/agency-agents) | `3c9588880b7cafaec325a104899fd8bbe27e7d72` | Specialist Agents | 70 | On-Demand | Specialized domain expertise (e.g. frontend, database) |
| **gstack** | [garrytan/gstack](https://github.com/garrytan/gstack) | `0d1bd5616c0ef096bb7ccee336f63c60ee408618` | Product & Release Review | 60 | Conditional | Code review, QA, shipping, release preparation |
| **OpenDesign** | [nexu-io/open-design](https://github.com/nexu-io/open-design) | `349748ee36cb641895679bde7b46a8728ed1c1bb` | Design Capability | 50 | Conditional | UI/UX design, design systems, visual polish |
| **Ponytail** | [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) | `2ed6c52c9d7e5e56942508591085fd45dea277d3` | Simplicity Review | 40 | **OFF** | Explicit request only (YAGNI, overengineering checks) |
| **Karpathy Skills** | [multica-ai/andrej-karpathy-skills](https://github.com/multica-ai/andrej-karpathy-skills) | `2c606141936f1eeef17fa3043a72095b4765b9c2` | Engineering Principles | 30 | Reference | High-level principles (simplicity first, surgical changes) |

---

## 6. Why Capabilities Are Activated Progressively

Progressive activation is not just a stylistic choice; it is fundamental to agent performance:

1. **Attention Concentration**: Large language models maintain higher accuracy and follow instructions more faithfully when their context is focused. Presenting hundreds of unrelated rules degrades attention across all rules.
2. **Elimination of Rule Conflicts**: Different engineering tools advocate different paradigms. For example, exhaustive completion (Unlazy) and ruthless simplification (Ponytail) serve opposing goals if loaded simultaneously. Progressive routing activates them only when appropriate.
3. **Context Efficiency**: Uncoordinated skill loading injects substantial token overhead into every session turn. Progressive activation keeps 1–3 capabilities active per turn, achieving an estimated **~60% to 85% reduction** in active instruction overhead compared to all-loaded baselines (*architecture-level estimate*).

---

## 7. Supported Hosts

| Host | Support Status | Manifest Location | Marketplace Catalog | Verification Level |
|---|---|---|---|---|
| **Codex** | Packaging Supported | `.codex-plugin/plugin.json` | `.agents/plugins/marketplace.json` | Manifest & Marketplace Verified |
| **Claude Code** | Packaging Supported | `.claude-plugin/plugin.json` | `.claude-plugin/marketplace.json` | Manifest & Marketplace Verified |
| **Antigravity** | Runtime Tested | `plugin.json` & `.agents/skills/vikhyath-os/` | Global plugin discovery / `plugins.json` | End-to-End Runtime Tested |

---

## 8. Installation

### Important: Core Lifecycle Concepts

Before installing, understand the distinction between these four stages:

1. **Installation**: Downloading/caching the plugin onto your machine or host environment. Performed **once** per environment.
2. **Registration**: The host registering the plugin in its marketplace catalog or configuration.
3. **Project Activation**: Using the installed plugin within any project workspace without copying files.
4. **Capability Activation**: Vikhyath OS automatically selecting and routing specific external capabilities per task.

> **CRITICAL**: Do **NOT** manually copy or vendor the plugin files into your individual project repositories. The plugin should be installed once globally (or registered in your host's plugin directory) and invoked across projects.

---

### Host-Specific Installation Guides

#### A. OpenAI Codex

- **Prerequisites**: OpenAI Codex CLI installed and authenticated.
- **Support Status**: Packaging supported and marketplace verified.

```bash
# Step 1: Register the marketplace catalog
codex plugin marketplace add Vikhyath-thelazycoder/vikhyath-ai-engineering-os

# Step 2: Install the plugin
codex plugin install vikhyath-ai-engineering-os@vikhyath-marketplace
```

- **Verify Installation**:
  ```bash
  codex plugin list
  ```
- **How to Use in Any Project**:
  Open Codex in any workspace. The plugin is active globally. Assign tasks normally; Vikhyath OS routes execution automatically.
- **How to Update**:
  ```bash
  codex plugin update vikhyath-ai-engineering-os@vikhyath-marketplace
  ```
- **How to Uninstall**:
  ```bash
  codex plugin uninstall vikhyath-ai-engineering-os@vikhyath-marketplace
  codex plugin marketplace remove vikhyath-marketplace
  ```
- **Known Limitations**: External standalone CLI tools (such as Graphify) require a local Python environment (`pip install graphify-ai`).

---

#### B. Anthropic Claude Code

- **Prerequisites**: Node.js and Claude Code CLI (`npm install -g @anthropic-ai/claude-code`) installed and authenticated.
- **Support Status**: Packaging supported and marketplace verified.

```bash
# Step 1: Register the marketplace catalog
claude plugin marketplace add Vikhyath-thelazycoder/vikhyath-ai-engineering-os

# Step 2: Install the plugin
claude plugin install vikhyath-ai-engineering-os@vikhyath-marketplace
```

- **Verify Installation**:
  ```bash
  claude plugin list
  ```
- **How to Use in Any Project**:
  Run `claude` in any project folder. The plugin instructions are automatically loaded.
- **How to Update**:
  ```bash
  claude plugin update vikhyath-ai-engineering-os@vikhyath-marketplace
  ```
- **How to Uninstall**:
  ```bash
  claude plugin uninstall vikhyath-ai-engineering-os@vikhyath-marketplace
  claude plugin marketplace remove vikhyath-marketplace
  ```
- **Known Limitations**: Capabilities that do not offer native Claude Code plugins are applied via instructional guidance.

---

#### C. Google Antigravity

- **Prerequisites**: Antigravity environment installed.
- **Support Status**: Runtime tested and packaging supported.

**Recommended: Global Machine-Wide Installation**
Clone directly into the Antigravity global plugins directory. It is immediately available across all your workspaces:

```bash
git clone https://github.com/Vikhyath-thelazycoder/vikhyath-ai-engineering-os.git ~/.gemini/config/plugins/vikhyath-ai-engineering-os
```

**Alternative: Shared Path Registration**
If you keep the repository in a custom folder, register it in `~/.gemini/config/plugins.json`:

```json
{
  "plugins": [
    {
      "name": "vikhyath-ai-engineering-os",
      "path": "/path/to/cloned/vikhyath-ai-engineering-os"
    }
  ]
}
```

- **Verify Installation**:
  Launch Antigravity; verify that the skill `vikhyath-os` appears in available skills.
- **How to Use in Any Project**:
  Any project opened in Antigravity automatically inherits global plugins. No files need to be copied into the project.
- **How to Update**:
  ```bash
  git -C ~/.gemini/config/plugins/vikhyath-ai-engineering-os pull origin main
  ```
- **How to Uninstall**:
  ```bash
  rm -rf ~/.gemini/config/plugins/vikhyath-ai-engineering-os
  ```
- **Known Limitations**: Upstream `gstack` does not provide native Antigravity packaging; Graphify runs as a CLI tool.

---

### External Capabilities Setup

Vikhyath OS is an orchestration layer that directs tasks to external tools. When you require capabilities that have their own host plugins or CLI tools, install them using their standard methods:

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

*(See the `integrations/` directory for metadata and options for each capability.)*

---

## 9. First-Use Example

To verify that Vikhyath OS is active and operating correctly in your agent session, provide this prompt:

```text
Use Vikhyath AI Engineering OS and report which capabilities you activate for this task.
```

### Expected Output

Your agent should produce a response demonstrating task classification and progressive routing similar to:

```text
[Vikhyath AI Engineering OS]
• Task Intent: General engineering inquiry / verification
• Active Capabilities: [ECC] (Engineering Foundation)
• Inactive Capabilities: Graphify, Unlazy, Addy, Agency, gstack, OpenDesign, Ponytail, Karpathy
• Rationale: No complex codebase, security, or release signals detected. ECC provides sufficient planning and verification discipline for this task.
```

---

## 10. Example Tasks and Expected Routing

These examples demonstrate how the progressive router handles diverse engineering tasks (*documentation only; routing behavior is evaluated dynamically*):

### Example 1: Small Engineering Task
- **User Prompt**: `"Fix the off-by-one boundary check in the token bucket rate limiter in auth/limiter.py"`
- **Routed Capabilities**: **`ECC`**
- **Inactive**: Graphify, Unlazy, Addy, Agency, gstack, OpenDesign, Ponytail, Karpathy
- **Outcome**: Focused surgical fix with unit test verification.

### Example 2: Architecture & Codebase Analysis
- **User Prompt**: `"Trace the data flow and map symbol relationships between the payment webhook handler and the order database in this unfamiliar monorepo"`
- **Routed Capabilities**: **`ECC`** + **`Graphify`**
- **Inactive**: Unlazy, OpenDesign, Ponytail, gstack
- **Outcome**: AST-level dependency graph and structural understanding before touching code.

### Example 3: Security Hardening Review
- **User Prompt**: `"Audit our JWT token validation and password reset handler for session fixation and OWASP Top 10 vulnerabilities"`
- **Routed Capabilities**: **`ECC`** + **`Addy Skills (security-hardening)`**
- **Inactive**: OpenDesign, Ponytail, gstack
- **Outcome**: Security checklist verification and defensive input sanitation.

### Example 4: Large Multi-File Implementation
- **User Prompt**: `"Implement a complete multi-provider billing pipeline across 8 service modules; do not leave placeholders or skip edge cases"`
- **Routed Capabilities**: **`ECC`** + **`Unlazy`** + **`Graphify`**
- **Inactive**: OpenDesign, Ponytail, gstack
- **Outcome**: Depth-tree tracking, complete implementation without stubs, and verification gates.

### Example 5: Production Release Review
- **User Prompt**: `"Prepare release checklist for v2.4.0, run QA smoke tests, and generate client-facing changelog"`
- **Routed Capabilities**: **`ECC`** + **`gstack`**
- **Inactive**: OpenDesign, Ponytail, Unlazy
- **Outcome**: Structured shipping workflow, QA validation, and release readiness sign-off.

---

## 11. Updating

To keep Vikhyath OS up to date with the latest capability pins and routing definitions:

```bash
# Codex
codex plugin update vikhyath-ai-engineering-os@vikhyath-marketplace

# Claude Code
claude plugin update vikhyath-ai-engineering-os@vikhyath-marketplace

# Antigravity (global installation)
git -C ~/.gemini/config/plugins/vikhyath-ai-engineering-os pull origin main
```

### Pinning to a Specific Release
To pin your environment to a specific release tag (e.g., `v1.0.1`):

```bash
# Codex
codex plugin install vikhyath-ai-engineering-os@vikhyath-marketplace#v1.0.1

# Antigravity
git -C ~/.gemini/config/plugins/vikhyath-ai-engineering-os checkout v1.0.1
```

---

## 12. Uninstalling

To cleanly remove the plugin:

```bash
# Codex
codex plugin uninstall vikhyath-ai-engineering-os@vikhyath-marketplace
codex plugin marketplace remove vikhyath-marketplace

# Claude Code
claude plugin uninstall vikhyath-ai-engineering-os@vikhyath-marketplace
claude plugin marketplace remove vikhyath-marketplace

# Antigravity
rm -rf ~/.gemini/config/plugins/vikhyath-ai-engineering-os
```

---

## 13. Troubleshooting

### Built-in Diagnostic Tooling

The repository includes diagnostic and validation scripts:

```bash
# Run structural diagnostics and manifest checks
./scripts/doctor

# Run offline validation tests
./scripts/validate

# Verify all pinned commit SHAs against live GitHub repositories
./scripts/validate --online

# Run Python unit tests
python3 -m unittest discover -s tests -p "test_*.py"
```

### Common Issues and Resolutions

1. **Plugin Not Recognized After Installation**:
   - Verify that your host agent CLI is up to date.
   - For Antigravity, ensure the clone is located at `~/.gemini/config/plugins/vikhyath-ai-engineering-os` and contains `plugin.json`.
2. **Missing External Dependency**:
   - If a task activates `Graphify`, ensure `graphify-ai` is installed in your Python environment (`pip install graphify-ai`).
3. **Overriding Default Routing**:
   - To force or suppress a specific capability, state it directly in your prompt:
     `"Use Vikhyath OS and perform a Ponytail simplicity review on src/engine/"`
4. **Reporting a Bug**:
   - Run `./scripts/doctor` and include the terminal output in your [Bug Report](.github/ISSUE_TEMPLATE/bug_report.md).

---

## 14. Development & Contribution Instructions

We welcome contributions! Please review our [Contributing Guide](CONTRIBUTING.md) and [Code of Conduct](CODE_OF_CONDUCT.md).

### Local Setup & Testing

```bash
# Clone the repository
git clone https://github.com/Vikhyath-thelazycoder/vikhyath-ai-engineering-os.git
cd vikhyath-ai-engineering-os

# Install test dependencies
pip install pyyaml

# Run test suite
python3 -m unittest discover -s tests -p "test_*.py"

# Run doctor and validation
./scripts/doctor
./scripts/validate
```

### Repository Structure

```text
vikhyath-ai-engineering-os/
├── .agents/                    # Antigravity skill adapter and marketplace
│   ├── plugins/marketplace.json
│   └── skills/vikhyath-os/SKILL.md
├── .claude-plugin/             # Claude Code packaging & marketplace
│   ├── marketplace.json
│   └── plugin.json
├── .codex-plugin/              # Codex plugin manifest
│   └── plugin.json
├── .github/                    # CI workflows, issue & PR templates
│   ├── ISSUE_TEMPLATE/
│   ├── pull_request_template.md
│   └── workflows/ci.yml
├── agents/                     # Specialized agent persona definitions
├── config/                     # Core orchestration schemas
│   ├── capabilities.yaml       # Pinned capability registry
│   ├── priorities.yaml         # 8-level conflict resolution hierarchy
│   └── routing.yaml            # Task classification and routing rules
├── integrations/               # Metadata files for each external capability
├── scripts/                    # Diagnostic and validation tooling
│   ├── benchmark
│   ├── doctor
│   └── validate
├── skills/                     # Portably structured skill definitions
├── tests/                      # Python unit test suite
│   ├── manifests/
│   ├── routing/
│   ├── security/
│   └── validation/
├── workflows/                  # Standard engineering workflow guides
├── plugin.json                 # Portable root manifest (Agent Plugins 1.0.0)
├── VERSION                     # Release version string (1.0.1)
├── CHANGELOG.md                # Release notes and history
├── CONTRIBUTING.md             # Contribution guidelines
├── SECURITY.md                 # Security policy and disclosure
├── CODE_OF_CONDUCT.md          # Contributor covenant
└── README.md                   # Project documentation
```

---

## 15. Security Model

Vikhyath AI Engineering OS maintains a strict security posture:

- **Cryptographic Immutability**: All external capabilities are pinned to immutable 40-character hexadecimal Git commit SHAs, preventing upstream supply chain attacks.
- **Zero Daemons / Zero Network Sockets**: The plugin contains no daemon processes, listening sockets, or background network activity.
- **No Secret Storage**: No API tokens, keys, credentials, or environment files are stored or managed by this repository.
- **Host Sandbox Conformance**: All file and command actions are mediated exclusively through the host agent's native permission model.

See [SECURITY.md](SECURITY.md) for full details and vulnerability reporting instructions.

---

## 16. No-MCP Statement

> **Vikhyath AI Engineering OS is strictly and intentionally Model Context Protocol (MCP) FREE.**

- **Zero MCP Servers**: This repository does not define, launch, or configure any MCP servers.
- **No `.mcp.json`**: There is no `.mcp.json` or `mcpServers` configuration present.
- **No MCP Runtime Dependency**: The plugin operates entirely through standard agent plugin manifests, markdown skill instructions, and deterministic YAML routing rules.
- **Guaranteed Absence**: Automated CI checks and unit tests continuously enforce that no MCP references or configurations are introduced.

---

## 17. License

Distributed under the **MIT License**. See [LICENSE](LICENSE) for the full license text.

---

## 18. Project Status & Version

- **Current Release**: `1.0.1`
- **Release Date**: September 2026
- **Status**: Stable Public Open-Source Release
- **Changelog**: See [CHANGELOG.md](CHANGELOG.md) for version history.
