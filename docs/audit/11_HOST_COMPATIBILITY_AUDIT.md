# 11 — Host Compatibility Audit (Phase 3)

Status vocabulary (spec §34): **FILES_PRESENT** (packaging exists) · **INSTALLED** (host has the plugin) · **RUNTIME_VERIFIED** (observed working inside the host). These are separate; one never implies another.

## Evidence gathered on this machine (2026-10-03)

| Host | CLI on PATH | User config dir | Where user-level skills/plugins live (observed) | v1.0.1 installed? |
|---|---|---|---|---|
| Claude Code | `claude` not on PATH (runs inside VS Code extension) | `~/.claude/` | `~/.claude/plugins/cache/<marketplace>/<plugin>/<version>/`, registry `installed_plugins.json` | **Yes**: `vikhyath-ai-engineering-os@vikhyath-marketplace` 1.0.1 (commit `d77834e`), alongside `ecc@ecc` 2.2.2 |
| Codex | not on PATH | `~/.codex/` (app data present) | `~/.codex/plugins/cache/` (only `openai-bundled`, `openai-curated-remote`, `openai-primary-runtime`), `~/.codex/skills/<name>/` | **No** |
| Cursor | not on PATH; no app in `/Applications` | `~/.cursor/` | `~/.cursor/skills/<name>/SKILL.md` (a `cardboard` skill is present) | **No** |
| Antigravity | `agy` not on PATH; no app in `/Applications` | `~/.gemini/antigravity/`, `~/.gemini/config/`, `~/Library/Application Support/Antigravity` | built-in skills at `~/.gemini/antigravity/builtin/skills/<name>/`; **`~/.gemini/config/plugins/` does not exist** | **No** |

## Host packaging contracts (from upstream evidence)

| Host | Plugin mechanism | Skill format | Hooks | Sources |
|---|---|---|---|---|
| Claude Code | Marketplace (`.claude-plugin/marketplace.json`) + plugin (`.claude-plugin/plugin.json`); auto-discovers `skills/`, `agents/`, `commands/`, `hooks/hooks.json`; `CLAUDE_PLUGIN_ROOT` env | `SKILL.md` with `name`/`description` frontmatter; descriptions are loaded at session start | SessionStart, UserPromptSubmit, PreToolUse, PostToolUse, Stop, SubagentStart, PreCompact, SessionEnd | ECC/Ponytail manifests and hooks; this session's installed plugins |
| Codex | `codex plugin marketplace add <repo>` + **`codex plugin add <name>@<marketplace>`** (CLI ≥0.122); `.codex-plugin/plugin.json` with `"skills": "./skills/"`; `.agents/plugins/marketplace.json` | Same `SKILL.md`; progressive disclosure (name+description first, body on selection) | Codex hooks exist (`hooks/codex-hooks.json` in ECC; Ponytail `claude-codex-hooks.json`) | Addy `docs/codex-setup.md`, ECC, Ponytail |
| Cursor | Project rules `.cursor/rules/*.mdc` (`alwaysApply`, `globs`); project skills `.cursor/skills/<name>/SKILL.md`; **user skills `~/.cursor/skills/`**; Cursor hooks (`hooks.json`) | `SKILL.md`; rules as `.mdc` | Cursor hooks (Ponytail `hooks/cursor-hooks.json`, `docs/cursor-hooks.md`) | Addy `docs/cursor-setup.md`, Agency `tools.json` (`cursor-mdc`), Ponytail |
| Antigravity | `agy plugin install <path|git>` → `~/.gemini/config/plugins/<name>/` (registers skills + agents); user skills `~/.gemini/config/skills/<slug>/SKILL.md`; project skills `.agents/skills/<slug>/SKILL.md`; rules with `trigger: always_on` frontmatter | `SKILL.md` | UNKNOWN (not documented in audited sources) | Addy `docs/antigravity-setup.md`, Agency `tools.json` (`skill-md`), Graphify `always_on/antigravity-rules.md` |

## Findings

| ID | Finding |
|---|---|
| H-1 | No Cursor adapter in v1.0.1 (confirmed). Cursor supports user-level skills at `~/.cursor/skills/`, so a **central install without project files is possible**. |
| H-2 | v1.0.1's "Antigravity: Runtime Tested" claim has no supporting state on this machine: `agy` absent, `~/.gemini/config/plugins/` absent, no Vikhyath files under `~/.gemini`. Status is at most FILES_PRESENT. |
| H-3 | v1.0.1 agents lack frontmatter → host shows no description (confirmed again: 3 agents, 66 bytes total of name text). |
| H-4 | v1.0.1 README uses `codex plugin install …`; current Codex documents `codex plugin add <name>@<marketplace>` (≥0.122). **UNKNOWN** which the user's Codex accepts → verify in P20. |
| H-5 | The Antigravity project-skill path `.agents/skills/` **is a project-local directory**; the user-level path `~/.gemini/config/skills/` (or the `agy` plugin dir) satisfies §2.3. v1.0.1's `.agents/skills/vikhyath-os/` lives in the plugin repo, which is correct only when the repo itself is the plugin. |
| H-6 | Every host supports `SKILL.md` with `name`/`description` and loads descriptions up front. **One canonical entry-skill set serves all four hosts**; adapters differ only in manifest/registration and hook wiring. |
| H-7 | Antigravity uses `mcp_config.json` for MCP. The OS writes nothing there (§2.1). |

## Verification plan per host (P19–P22)

| Host | FILES_PRESENT check | INSTALLED check | RUNTIME_VERIFIED check | Available here? |
|---|---|---|---|---|
| Claude Code | manifest schema tests | `installed_plugins.json` entry with expected version/commit | Entry skill visible in skill list + `vikhyath route` called from a session + SessionStart bootstrap present | Yes (this host) |
| Codex | `.codex-plugin/plugin.json`, marketplace JSON | `codex plugin list` | Skill invoked in a Codex session | **Needs Codex CLI** (Q-3) |
| Cursor | generated `~/.cursor/skills/vikhyath*/SKILL.md` | files present at user path | Skill selected in a Cursor chat | **Needs Cursor** (Q-3) |
| Antigravity | plugin dir layout validates (`agy plugin validate`) | `agy plugin list` | Skill selected in an `agy` session | **Needs `agy`** (Q-3) |

Without the host tools, P20–P22 can deliver FILES_PRESENT (and schema-validated packaging) but must report INSTALLED / RUNTIME_VERIFIED as **NOT VERIFIED**.
