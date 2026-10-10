# P19–P22 evidence — host adapters (2026-10-11)

- `vikhyath adapters render` → wrote `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, `.agents/plugins/marketplace.json`, `.agents/skills/vikhyath-os/SKILL.md`; `vikhyath adapters render --check` → "adapter files: current".
- `vikhyath adapters status` on this machine: claude-code FILES_PRESENT (`~/.claude/plugins/installed_plugins.json` lists `ecc@ecc`, `ui-ux-pro-max@ui-ux-pro-max-skill`, `open-design@open-design`; no vikhyath entry, marketplace cache present), codex FILES_PRESENT, cursor FILES_PRESENT, antigravity FILES_PRESENT. No host runtime record yet → none RUNTIME_VERIFIED (honest per §34/D-024).
- Tests (`tests/hosts/test_hosts.py`, temp user homes): Cursor install → 11 skills in `~/.cursor/skills/vikhyath-*` → INSTALLED → after `bootstrap --host cursor` record → RUNTIME_VERIFIED → uninstall removes 11; Antigravity install refuses to overwrite an unmanaged `vikhyath-routing` skill; Claude registry fixture → INSTALLED 1.0.1; `bin/vikhyath bootstrap --host claude-code` with no central install runs from the plugin source, prints the L0 with `cli:` and writes `hosts/claude-code.json` (bootstraps 1).
- Policy: all 11 entry skills and the generated Antigravity skill reference `config/verification.yaml`; no adapter output contains `mcpServers`, `mcp_config`, `chrome-devtools`, `take_screenshot`, `playwright` or extra hook events.
- `python -m unittest discover -s tests`: **228 OK, 3 skipped**; doctor 49/0; validate 22/0.

To reach RUNTIME_VERIFIED in Claude Code: install the plugin from this branch (e.g. `/plugin marketplace add <path or repo>` then install `vikhyath-ai-engineering-os@vikhyath-marketplace`), start a session, then `vikhyath adapters status --host claude-code`.
