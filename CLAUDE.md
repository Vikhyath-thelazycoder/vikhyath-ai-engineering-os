# Vikhyath AI Engineering OS — Claude Code Instructions

This is the Vikhyath AI Engineering OS plugin. Follow these rules:

1. **Progressive activation only** — Do not load all skills. Classify the task first, then activate only what's relevant.
2. **No MCP** — This plugin does not use MCP. Do not suggest or enable MCP servers.
3. **Route to capabilities** — Use the routing logic in `config/routing.yaml` to determine which external capabilities apply.
4. **Context efficiency** — Minimize token usage. Load skill content on-demand, not upfront.

## Quick Reference

- Engineering → ECC
- Codebase intelligence → Graphify
- Production engineering → Addy Agent Skills
- Specialist perspectives → Agency Agents
- Product/release → gstack
- Completion discipline → Unlazy (substantial tasks only)
- Simplicity review → Ponytail (explicit request only)
- Design → OpenDesign (design tasks only)
- Principles → Karpathy Skills (reference only)

See `config/capabilities.yaml` for the full capability registry.
