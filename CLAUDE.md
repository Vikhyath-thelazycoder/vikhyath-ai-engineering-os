# Vikhyath AI Engineering OS — Claude Code Instructions

This is the Vikhyath AI Engineering OS plugin for Claude Code.

## Architecture Guidelines

1. **Progressive Activation**: Do NOT load all skills. Classify the user task first, then activate/route only to relevant capabilities.
2. **NO MCP**: This plugin does not use MCP. Do not suggest or enable MCP servers.
3. **Route to Capabilities**: Use the routing matrix in `config/routing.yaml` to determine which external capabilities apply.
4. **Context Efficiency**: Minimize token usage by reading skill content on demand.

## Marketplace & Installation

Claude Code marketplace metadata is defined in `.claude-plugin/marketplace.json`.

```bash
# Add marketplace
claude plugin marketplace add Vikhyath-thelazycoder/vikhyath-ai-engineering-os

# Install plugin
claude plugin install vikhyath-ai-engineering-os@vikhyath-marketplace
```

## Routing Quick Reference

- **Engineering tasks** → ECC
- **Codebase intelligence** → Graphify
- **Production engineering** → Addy Agent Skills
- **Specialist perspectives** → Agency Agents (selective)
- **Product/release review** → gstack
- **Completion discipline** → Unlazy (substantial tasks)
- **Simplicity review** → Ponytail (explicit request only; default OFF)
- **Design tasks** → OpenDesign
- **Principles** → Karpathy Skills (reference only)

See `config/capabilities.yaml` for the full capability registry and `config/priorities.yaml` for conflict resolution.
