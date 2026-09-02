# Contributing to Vikhyath AI Engineering OS

Thank you for your interest in contributing to **Vikhyath AI Engineering OS**! This project is a thin, portable orchestration layer that selectively routes AI coding tasks to specialized engineering capabilities from proven external repositories.

Before submitting contributions, please read this guide and our [Code of Conduct](CODE_OF_CONDUCT.md).

---

## Architecture Principles & Guardrails (Non-Negotiable)

The architecture of Vikhyath AI Engineering OS is locked to ensure stability, portability, and context efficiency:

1. **Thin Orchestration Layer**: Vikhyath OS routes tasks; it is not a monolithic framework, giant prompt, or always-on daemon.
2. **GitHub as Source of Truth**: External tools remain external dependencies. Never vendor, submodule, or copy third-party repository code into this repository.
3. **Progressive Capability Activation**: Only capabilities relevant to the immediate task are activated. Never load all capabilities simultaneously.
4. **Strict NO MCP**: No Model Context Protocol (MCP) servers, configs (`.mcp.json`), adapters, or dependencies are allowed.
5. **Deterministic Conflict Hierarchy**: Conflicting guidance is resolved using the 8-level priority hierarchy defined in `config/priorities.yaml`.
6. **Cryptographic Pinning**: All external capability references must be pinned to immutable 40-character hexadecimal Git commit SHAs.

---

## Getting Started

### Prerequisites

- **Git**
- **Python 3.9+**
- **PyYAML** (`pip install pyyaml`)
- A supported agent host: Codex, Antigravity, or Claude Code

### Setup

```bash
git clone https://github.com/Vikhyath-thelazycoder/vikhyath-ai-engineering-os.git
cd vikhyath-ai-engineering-os
pip install pyyaml
```

---

## Development & Validation Workflow

We provide a comprehensive validation and diagnostic suite. **All checks must pass before any pull request will be accepted.**

```bash
# 1. Run Python unit tests
python3 -m unittest discover -s tests -p "test_*.py"

# 2. Run structural & integrity diagnostics
chmod +x scripts/doctor scripts/validate scripts/benchmark
./scripts/doctor

# 3. Run validation suite (offline)
./scripts/validate

# 4. Run remote GitHub commit SHA verification (online)
./scripts/validate --online

# 5. Run context and capability benchmark
./scripts/benchmark
```

### What Each Tool Checks

| Tool | Purpose |
|---|---|
| `python3 -m unittest` | Executes unit tests covering manifests, routing rules, security constraints, and integration schemas. |
| `./scripts/doctor` | Verifies repository structure, manifest schemas (Agent Plugins 1.0.0), marketplace configs, version consistency, and absence of MCP / vendor directories. |
| `./scripts/validate` | Tests routing rule integrity, capability registry format, 40-character commit SHAs, and security guardrails. |
| `./scripts/validate --online` | Queries the GitHub API to confirm every pinned commit SHA exists in its remote repository. |
| `./scripts/benchmark` | Generates capability coverage matrix and context efficiency estimates. |

---

## Proposing New Capability Integrations

To propose integrating a new external capability:

1. Open an issue using the [Capability Proposal Template](.github/ISSUE_TEMPLATE/capability_proposal.md).
2. Ensure the capability meets these criteria:
   - **Proven Track Record**: Public, high-quality open-source repository with active maintenance.
   - **Non-Redundant Role**: Fills a distinct engineering role not already covered by an existing capability.
   - **Zero MCP Requirement**: The tool must not require MCP runtime configuration or servers.
   - **Permissive License**: MIT, Apache-2.0, or compatible open-source license.
   - **Pinned Commit SHA**: Must point to an exact 40-character hexadecimal Git commit SHA.
3. If approved, add:
   - An integration file: `integrations/<name>.yaml`
   - An entry in: `config/capabilities.yaml`
   - Updated routing signals in: `config/routing.yaml`
   - Unit tests validating the new metadata.

---

## Repository Structure

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
├── .github/                    # CI workflows, issue and PR templates
│   ├── ISSUE_TEMPLATE/
│   ├── pull_request_template.md
│   └── workflows/ci.yml
├── agents/                     # Specialized agent persona guidance
├── config/                     # Core orchestration schemas
│   ├── capabilities.yaml       # Pinned capability registry
│   ├── priorities.yaml         # 8-level conflict hierarchy
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
├── VERSION                     # Release version string
└── README.md                   # Project documentation
```

---

## Pull Request Guidelines

1. Fork the repository and create a descriptive branch from `main` (e.g., `feat/add-routing-signal`, `fix/manifest-schema`).
2. Make minimal, surgical changes adhering to existing design patterns.
3. Verify that `./scripts/doctor` and `./scripts/validate` pass with zero warnings or errors.
4. Ensure no MCP references or vendor files are introduced.
5. Fill out the [Pull Request Template](.github/pull_request_template.md) completely.
6. Submit your PR against `main`. All CI checks must pass.

---

## License

By contributing to Vikhyath AI Engineering OS, you agree that your contributions will be licensed under the project's [MIT License](LICENSE).
