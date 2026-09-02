# Changelog

All notable changes to the Vikhyath AI Engineering OS will be documented in this file.

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
- 9 integration metadata files with verified versions and commit SHAs
- Routing configuration with task classification rules
- Priority and conflict resolution configuration
- Doctor/validation script
- Validation test script
- Benchmark script
- AGENTS.md for Codex/Antigravity discovery
- CLAUDE.md for Claude Code discovery
- Comprehensive README with installation, usage, and architecture documentation
- MIT license

### Architecture Decisions
- Plugin-only architecture (no daemon, no background service)
- No MCP — explicitly excluded per user decision
- No upstream repository copies — external dependencies remain external
- No giant always-loaded prompt — progressive/on-demand activation
- No always-on swarm — selective capability activation
- Version-pinned external dependencies using verified commit SHAs
