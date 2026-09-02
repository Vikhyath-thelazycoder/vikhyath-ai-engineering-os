# Changelog

All notable changes to the Vikhyath AI Engineering OS will be documented in this file.

## [1.0.1] - 2026-09-02

### Added
- Root-level portable `plugin.json` adhering to the Agent Plugins 1.0.0 specification (`https://agent-plugins.org/schemas/1.0.0/plugin.schema.json`)
- Codex marketplace metadata in `.agents/plugins/marketplace.json` exposing root plugin source (`./`)
- Claude Code marketplace metadata in `.claude-plugin/marketplace.json` exposing root plugin source (`./`)
- GitHub Actions CI workflow in `.github/workflows/ci.yml` running unit tests, diagnostics, validation, and architecture audits on PRs and pushes
- Support for `--online` verification flag in `./scripts/validate` for remote GitHub commit SHA verification
- Expanded unit test suite (18 unit tests across manifests, routing, security, and integration schemas)

### Changed
- Updated `.claude-plugin/plugin.json` to minimal valid schema, removing non-standard relative skills path
- Updated installation documentation across README, CLAUDE.md, and integration files to current marketplace-based flows for Codex and Claude Code
- Enforced strict 40-character hexadecimal commit SHA format checking for all 9 capability registries
- Removed unverified/stale tag entries from `config/capabilities.yaml` and `integrations/ecc.yaml`
- Clarified benchmark claims to distinguish between verified measurements and architecture-level estimates
- Clarified routing model terminology from dynamic execution claims to intelligent capability instruction and routing

## [1.0.0] - 2026-09-02

### Added
- Initial release of Vikhyath AI Engineering OS
- Capability registry with 9 external capabilities (ECC, Graphify, Unlazy, Addy, Agency, gstack, OpenDesign, Ponytail, Karpathy)
- Progressive activation routing system
- Codex plugin manifest (`.codex-plugin/plugin.json`)
- Claude Code plugin manifest (`.claude-plugin/plugin.json`)
- Antigravity skill adapter (`.agents/skills/vikhyath-os/`)
- 5 core skills: routing, engineering, production, security, review
- 3 agent definitions: engineering-architect, security-reviewer, production-reviewer
- 5 workflow definitions: feature, bugfix, refactor, security-review, release
- 9 integration metadata files with pinned commit SHAs
- Routing configuration with task classification rules
- Priority and conflict resolution configuration (8-level hierarchy)
- Diagnostics, validation, and benchmark scripts
- MIT license
