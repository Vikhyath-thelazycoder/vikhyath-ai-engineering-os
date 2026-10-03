# 12 — Security Audit of Third-Party Source (Phase 1, spec §43)

All upstream source is treated as untrusted until inspected. This document lists the executable and side-effecting mechanisms found. P2's extraction matrix must place each one in EXCLUDE, or in ADAPT with the control stated here.

| ID | Repo | Mechanism | Risk | Required control / decision |
|---|---|---|---|---|
| SEC-01 | ECC | 24 hook handlers default ON (`hooks_enabled: true`) on every tool call, Stop, SessionStart, PreCompact | Always-on code execution in the user's session; capture of all tool use (`pre:observe:continuous-learning`) | EXCLUDE as a set. Re-implement only config-protection, Stop format/typecheck, cost tracking and pre-compact state save as **opt-in OS hooks**. |
| SEC-02 | ECC | `.mcp.json` → `npx -y chrome-devtools-mcp@1.10.1`; `ecc-memory-mcp` | MCP (§2.1); remote package execution via npx | EXCLUDE |
| SEC-03 | ECC | `ecc2` background daemon (Rust), `src/llm` provider client | Daemon (§2.5); outbound LLM calls | EXCLUDE |
| SEC-04 | Ponytail | SessionStart/SubagentStart/UserPromptSubmit hooks; writes `~/.claude/.ponytail-active`, `~/.config/ponytail/` | Always-on prompt injection of a ruleset; home-dir writes | EXCLUDE hooks; simplicity guidance loads only via routing |
| SEC-05 | Ponytail, UI/UX Pro Max, Graphify, OpenDesign, Agency, Beacon | MCP servers/configs | §2.1 | EXCLUDE |
| SEC-06 | gstack | `gstack-telemetry-sync` → Supabase; `gstack-analytics`; `gstack-update-check`; preamble running `~/.claude/skills/gstack/bin/gstack-skill-start` | Silent network egress; silent updates (§41, §44) | EXCLUDE (preamble removed by adapting from `.tmpl`) |
| SEC-07 | gstack | Aside real-browser driving, persistent Chromium daemon, `setup-browser-cookies` (imports real browser cookies), `/pair-agent` remote tunnel | Session/cookie exposure; remote control of a signed-in browser; always-on browser | EXCLUDE. Browser use follows §23A (lazy, headless, bounded, terminated). |
| SEC-08 | Graphify | `hook install` (post-commit/post-checkout + **detached background rebuild**, git merge driver); `install` writes rule blocks into project `CLAUDE.md`/`AGENTS.md` | Persistent repo mutation; background processes | EXCLUDE. OS calls `graphify update` explicitly; `GRAPHIFY_OUT` points to OS state. |
| SEC-09 | Graphify | Optional LLM semantic extraction sends file content to Anthropic/OpenAI/Gemini/etc. | Source code leaves the machine | Disabled by default; AST-only mode. Enabling requires explicit user opt-in per project. |
| SEC-10 | Unlazy | `CHECK:` gate commands run shell commands; approvals in `~/.unlazy/approved`; hook installer edits `.claude/settings*.json` | Arbitrary command execution from ledgers | Keep Unlazy's own approval binding (already treats ledgers as untrusted). Adapter registers the Stop hook centrally, never in the project. |
| SEC-11 | BeyondSEO | `publishing.py`: FTP/FTPS/SFTP **writes to live websites**; connection JSON with credentials | Destructive remote changes; credential handling | Explicit per-task authorization gate; credentials never in state, logs or provenance (§78). Not part of default SEO audit routing. |
| SEC-12 | BeyondSEO | Crawler fetches arbitrary URLs; `browser-setup` installs Chromium | Network egress; SSRF-like targeting of internal hosts; scraped content as prompt injection (§77) | Network only for SEO tasks; scraped content stored as evidence **data**, never instructions; Chromium only when explicitly selected. |
| SEC-13 | Brag | `npx hyperframes …` (downloads and executes an npm package at runtime) | Unpinned remote code execution | Pin the Hyperframes version or default to `/brag-slim` (decided in P2). |
| SEC-14 | Agency, Addy, UI/UX Pro Max, ECC | Installer scripts (`install.sh`, `install-apply.js`, `cli` update/uninstall) writing into host config dirs | Uncontrolled host mutation | EXCLUDE all upstream installers; only the OS's own install flow (§34) registers anything. |
| SEC-15 | Agent Beacon | Cloud-preselected setup, endpoint agent, forwarding | Data egress; daemon | EXCLUDE. Event schema and detection rules used as data only. |
| SEC-16 | All | Upstream skills contain imperative instructions (e.g. "Treat the skill file as executable instructions") | Instruction conflicts with the OS's own rules | ADAPT step strips host- and vendor-specific directives; the OS conflict hierarchy applies. |

Positive findings: Unlazy (untrusted-ledger model, approval binding), BeyondSEO (absence claims refused on partial captures; Chromium only on authorized setup) and Beacon rules (prompt-injection, credential-access, exfiltration detections with test cases) contain security controls worth preserving.
