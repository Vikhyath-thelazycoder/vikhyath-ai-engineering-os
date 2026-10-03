# 04 — Upstream Repository Audit (Phase 1)

| Field | Value |
|---|---|
| Date | 2026-10-03 |
| Inputs | Complete blobless snapshots in `.staging/upstream/` (D-003). Pins in [evidence/upstream-staging-snapshot.yaml](evidence/upstream-staging-snapshot.yaml). |
| Per-file evidence | Every tracked file of all 14 repos (26,588 files): git blob SHA-1, bytes, path → [evidence/upstream-file-hashes/](evidence/upstream-file-hashes/) |
| Indicator scans | Skills, agents, commands, hooks, manifests, MCP, network, telemetry, background, browser, shell exec, env, home writes, self-update, LLM API → [evidence/upstream-scan/](evidence/upstream-scan/) |
| Scanner | [`tools/audit/scan_upstream.py`](../../tools/audit/scan_upstream.py) (stdlib, re-runnable for P24 updates) |
| Method | Indicator scans flag candidates (keyword matches include false positives, e.g. `cron` in prose). Every executable surface, manifest, hook, installer and skill system was then **read by hand**; runtimes were **executed** where they are integration candidates. |

Preliminary integration types use the spec §38 vocabulary: **COPY · ADAPT · WRAP · REFERENCE · PRESERVE (subsystem) · EXCLUDE**. Final per-file decisions and dependency closure (D-006) are set in P2's extraction matrix.

## Summary

| Repo | Pin (HEAD) | Files | What it really is | Runtime | MCP | Always-on / background | Prelim. integration | Target domain(s) |
|---|---|---|---|---|---|---|---|---|
| ECC | `ef648e0` | 4,212 | Multi-harness plugin: 293 skills, 68 agents, 94 commands, 22 rule packs, 24 hook handlers, plus an alpha Rust daemon and an LLM client | Node (hooks), Rust (ecc2), Python (src/llm) | **Yes**: `.mcp.json` (chrome-devtools), `ecc-memory-mcp` bin, MCP health hooks | **Yes**: hooks default ON across every tool call/Stop/SessionStart; `ecc2` daemon | ADAPT (selected skills/agents/rules), EXCLUDE the rest | engineering, testing, codebase (patterns), design (some) |
| Addy | `a06bc63` | 211 | 25 production-engineering skills with per-skill and shared references, 4 agents, 9 commands | None required (bash hooks optional, unwired) | Skill text only (`browser-testing-with-devtools` uses DevTools MCP) | No (session-start hook deliberately not wired) | COPY/ADAPT skills + shared `references/` | engineering, testing |
| Agency | `d3f71c4` | 381 | ~300 persona prompts by division + `divisions.json`, `tools.json` | None (install scripts only) | `integrations/mcp-memory` | No | ADAPT selected personas into domain roles | engineering, design, testing, security, seo/media (few) |
| gstack | `74512c2` | 2,677 | Lifecycle workflow suite (63 skills) generated from `.tmpl`; Bun browser daemon; telemetry; self-update | Bun/TS, compiled binaries, Chromium | Mentions only (24 files) | **Yes**: persistent headless browser daemon; telemetry sync; update check | ADAPT methodology from `.tmpl` + companions; EXCLUDE runtime | engineering (plan/review/release/investigate), testing (QA method), design (review method) |
| Karpathy | `2c60614` | 9 | One principles skill + host wrappers | None | No | No | COPY (skill) | engineering (principles) |
| Unlazy | `1667149` | 37 | Completion-discipline skill **with executable gate checker**, dispatch tooling, Stop hook | Node ≥16, zero deps | No | Optional Stop hook | PRESERVE (subsystem) | engineering/completion, testing |
| Ponytail | `c982cd4` | 169 | 6 simplicity skills + hooks for ~10 hosts + MCP server + benchmarks | Node (hooks) | **Yes**: `ponytail-mcp/` | **Yes**: SessionStart/SubagentStart/UserPromptSubmit inject ruleset every session | ADAPT skills; EXCLUDE hooks/MCP | engineering/simplicity |
| Graphify | `0b60d47` (branch `v8`) | 956 | Tree-sitter code knowledge graph CLI: query/path/explain/affected; optional LLM semantic extraction | Python ≥3.10, ~30 tree-sitter wheels (151 MB venv) | **Yes**: optional `mcp` extra, `graphify-mcp` entrypoint | Optional: git post-commit hooks with detached rebuild, `watch` daemon, writes rules into project CLAUDE.md/AGENTS.md | PRESERVE (isolated runtime); EXCLUDE MCP/hooks/install | codebase |
| OpenDesign | `53231d4` | 12,940 | Full design-agent product (web app, daemon, cloud) with design-system/template/skill libraries | Node/pnpm monorepo, daemon | Yes (1 file + 200 mentions) | **Yes** (`apps/daemon`) | ADAPT `craft/` + selected skills; REFERENCE-index design systems; EXCLUDE apps/daemon/cloud | design |
| Taste | `ce26fc2` | 66 | 13 anti-slop design skills; main skill 87 KB | None | No | No | ADAPT (split into sections) | design (+ completion: `output-skill`) |
| UI/UX Pro Max | `09170ee` | 682 | Design-intelligence skill backed by a **stdlib Python search engine over CSV datasets**; CLI installer; demo stack | Python 3 stdlib | **Yes**: `stack/.mcp.json` (playwright, chrome-devtools, shadcn) | No | PRESERVE (engine + data) + ADAPT skills | design |
| Brag | `cb89b9f` | 368 | Launch-video skills (`brag`, `brag-slim`) with 16 MB assets, uv-managed Python script | Python (uv), Hyperframes via `npx`, browser for render | No | No | PRESERVE (skill subsystem) | media |
| Agent Beacon | `5937da1` | 1,659 | Go endpoint agent capturing sessions across 20+ harnesses; cloud-first setup; OTel collector; 77 YAML detection rules | Go binaries, Homebrew, browser extension | Yes (72 files) | **Yes**: endpoint agent, heartbeat, forwarding | REFERENCE (event schema, hook taxonomy); ADAPT detection rules as data | observability, security |
| BeyondSEO | `c160b9d` | 221 | Installable Python package `beyondseo` 2.9.1: crawler, evidence, findings, reports, research, publishing + 134 playbooks/templates | Python ≥3.10; core deps bs4 + colorama; extras: playwright, reportlab, paramiko | Test mention only | Bounded foreground `watch` only | PRESERVE (isolated runtime) + ADAPT skill/playbooks | seo |

Pin decision: **pin every repo to the staged HEAD above** (D-008). All 9 v1.0.1 pins are ancestors of these HEADs.

---

## 1. ECC — `affaan-m/ECC` @ `ef648e01899ba3e8dc6371642deaaf64b4477775`

| Audit point | Finding (evidence) |
|---|---|
| Structure | `docs/` 1,520 (518 SKILL.md are **translations**: ja-JP 521 files, zh-CN 416, tr 142, es 142, …), `skills/` 585 files / 293 skills (5.5 MB), `tests/` 364, `scripts/` 320, `docker/` 213 (204 `context-profiles`), `pi/` 193, `.kiro/` 153, `rules/` 122 (22 packs: common, web, python, typescript, react, golang, rust, …), `commands/` 94, `.agents/` 89, `.opencode/` 81, `.cursor/` 69, `agents/` 68, `ecc2/` 21 (Rust), `src/llm` 20 (Python). |
| Canonical vs. copies | Canonical: `skills/`, `agents/`, `commands/`, `rules/`, `hooks/`, `scripts/hooks`. Host directories (`.kiro`, `.cursor`, `.agents`, `.opencode`, `.codex`, `.trae`, `.codebuddy`, `pi/`) are ports/copies; 258 groups of byte-identical files inside the repo. |
| Plugin manifest | `.claude-plugin/plugin.json` v2.2.3: `mcpServers: {}`, `userConfig.hooks_enabled` **default true**, `hook_profile` default `standard`. |
| MCP | **Root `.mcp.json` declares `chrome-devtools` (`npx -y chrome-devtools-mcp@1.10.1`).** `bin.ecc-memory-mcp`; hooks `pre:mcp-health-check`, `post:mcp-health-check`; `skills/mcp-server-patterns`, `skills/codehealth-mcp`. All EXCLUDE (§2.1). |
| Hooks (24) | PreToolUse: Bash dispatcher (quality/tmux/push/**GateGuard**), doc-file warning, suggest-compact, **continuous-learning capture of every tool use**, governance capture (opt-in env), **config-protection**, MCP health, **GateGuard edit/write fact-forcing**. PreCompact: state save. SessionStart: load previous context, Plan Canvas. PostToolUse: sync + async dispatchers. Stop ×7: Plan Canvas, **format+typecheck batch**, console.log check, session persistence, pattern extraction, **cost tracker**, desktop notify. SessionEnd marker. |
| Hook verdict | EXCLUDE always-on capture/friction: GateGuard, continuous-learning, desktop-notify, MCP health, Plan Canvas. ADAPT as **optional, OS-controlled** behaviors: config-protection (security), Stop-time format/typecheck (verification), cost tracker (observability token metrics), pre-compact state save (project state). |
| Executables | `scripts/ecc.js` CLI and installers (`install-apply.js`), `control-pane.js`, `plan-canvas.js` (browser UI). `ecc2/`: Rust **background daemon** + TUI dashboard + SQLite session store (alpha). `src/llm`: multi-provider LLM client. All EXCLUDE from runtime (daemon rule §2.5; OS owns its dashboard §31). Concepts from `ecc2/src/session` and `observability` are REFERENCE for P18. |
| Dependencies | npm `ecc-universal` 2.2.3: `@iarna/toml`, `ajv`, `js-yaml`, `sql.js`. |
| Network / telemetry | 67 network-indicator files, 31 telemetry; skill-health telemetry is local (`post:skill:track`). No unconditional remote telemetry endpoint found in hooks; full trace deferred to P3 security audit for any file selected in P2. |
| Home writes | 144 files reference `~/.claude` or `$HOME` (session data in `~/.claude/session-data/`, instincts, cost logs). |
| Skill catalogue (293) | Relevant clusters: core engineering (tdd-workflow, verification-loop, security-review, security-scan, api-design, backend-patterns, frontend-patterns, coding-standards, error-handling, database-migrations, deployment-patterns, docker-patterns, git-workflow, architecture-decision-records, hexagonal-architecture, contract-first, search-first, iterative-retrieval, production-audit, delivery-gate); codebase (codebase-onboarding, code-tour, repo-scan, workspace-surface-audit); context/token (context-budget, content-hash-cache-pattern, strategic-compact, token-budget-advisor, cost-tracking); testing (e2e-testing, browser-qa, ai-regression-testing, click-path-audit, eval-harness, benchmark, benchmark-methodology); design (design-system, frontend-design-direction, frontend-a11y, accessibility, taste, taste-application, make-interfaces-feel-better, motion-*, liquid-glass-design); SEO (`seo`); media (video-editing, remotion-video-creation, manim-video, ui-demo); **language/framework packs** (django-*, springboot-*, laravel-*, quarkus-*, golang-*, kotlin-*, rust-*, swift*, python-*, react-*, vue-*, nextjs, nuxt4, nestjs, fastapi, prisma, postgres, redis, mysql, …). Out of domain: healthcare-*, logistics/customs/energy/inventory, homelab-*, network-*, trading/defi/evm, investor-*, email/messages ops, scientific-*, ito-*. |
| Agents (68) | Reviewers per language, build resolvers per language, architect, planner, code-explorer, code-architect, tdd-guide, security-reviewer, a11y-architect, performance-optimizer, refactor-cleaner, silent-failure-hunter, e2e-runner, seo-specialist, … |
| Tests | 364 test files (Node). Not executed in P1 (ECC is a content source, not a runtime candidate). |
| License | MIT, © 2026 Affaan Mustafa. |
| UNKNOWN | Exact closure of each candidate skill (cross-links to `rules/`, `scripts/`, other skills) → traced in P2. |

## 2. Addy Agent Skills — `addyosmani/agent-skills` @ `a06bc63b3f8b829c14b0bbf53d99fefc39d58092`

| Audit point | Finding |
|---|---|
| Content | 25 skills (8–21 KB each): spec-, planning-, incremental-, test-driven-, source-, constraint-, doubt-driven development; api-and-interface-design, security-and-hardening, performance-optimization, frontend-ui-engineering, browser-testing-with-devtools, ci-cd-and-automation, code-review-and-quality, code-simplification, debugging-and-error-recovery, deprecation-and-migration, documentation-and-adrs, git-workflow-and-versioning, observability-and-instrumentation, shipping-and-launch, context-engineering, idea-refine, interview-me, using-agent-skills. 4 agents: code-reviewer, security-auditor, test-engineer, web-performance-auditor. |
| Progressive disclosure | Already built for it: SKILL.md + per-skill `references/` (hardening-patterns, optimization-patterns, floor-guard) loaded "when you reach that code, not before". |
| **Dependency closure** | Skills link to the **shared** top-level `references/` (security-checklist ×8, performance-checklist ×6, definition-of-done ×4, orchestration-patterns ×2, accessibility-checklist ×2, testing-patterns, observability-checklist). These 7 files must be bundled with the skills (D-006). `idea-refine` ships `scripts/idea-refine.sh` + 3 docs. |
| Hooks | `hooks/session-start.sh` (injects meta-skill; **deliberately not wired** on Claude/Codex), `sdd-cache` WebFetch cache, `simplify-ignore`. Optional. |
| MCP | `browser-testing-with-devtools` instructs use of Chrome DevTools MCP → ADAPT to the non-MCP local-first verification ladder (§23A) or EXCLUDE. |
| Evals | `evals/cases/*.json` + fixtures per skill — reusable as acceptance tests for adapted skills in P25. |
| Runtime | None required. `jq` only for optional hook. |
| License | MIT, © 2025 Addy Osmani. |

## 3. Agency Agents — `msitarzewski/agency-agents` @ `d3f71c4bb8922d3eea7576237a870dd59b3cdd52`

| Audit point | Finding |
|---|---|
| Content | ~300 persona files across divisions: engineering 65, specialized 59, marketing 37, game-development 21, strategy 17, gis 13, security 12, design 10, testing 9, sales 9, project-management 7, paid-media 7, support 6, spatial-computing 6, product 6, academic 6, finance 5, healthcare 3. Frontmatter: name, description, color, emoji, vibe. Self-contained (no cross-file links observed). |
| Metadata | `divisions.json` (division → label/icon/color; CI-enforced), `tools.json` (per-host install contract: detect dirs, dest templates, render format) — **useful evidence for P3 host adapters (Cursor, Antigravity paths)**. |
| Executables | `scripts/install.sh`, `convert.sh` (render per host), lint/check scripts. EXCLUDE from runtime. |
| MCP | `integrations/mcp-memory/setup.sh` → EXCLUDE. |
| Relevant personas | design (all 10), testing (all 9), security (appsec, architect, secrets, ai-generated-code auditor, pentester, incident responder, …), engineering subset (backend/frontend architect, api-platform, code-reviewer, codebase-onboarding, database-*, devops, identity-access, payments-billing, privacy, platform, minimal-change, …), product (6), project-management (project-shepherd, senior PM), marketing (seo-specialist, content-creator, video-optimization), specialized (codebase-archaeologist, workflow-architect, document-generator). Out of scope: game-dev, gis, academic, finance, healthcare, sales, paid-media, most specialized. |
| License | MIT, © 2025 AgentLand Contributors. |

## 4. gstack — `garrytan/gstack` @ `74512c20a7aca72e722d46bcc6b3954c1677d9ee`

| Audit point | Finding |
|---|---|
| Content | 63 skills: office-hours, spec, autoplan, plan-ceo/eng/design/devex-review, review, investigate, qa, qa-only, cso (security), ship, land-and-deploy, canary, retro, document-generate/release, design-consultation/-review/-html/-shotgun, health, test-audit, benchmark, careful/guard/freeze, context-save/restore, learn, iOS suite, browser suite (browse, scrape, skillify, pair-agent, open-gstack-browser, setup-browser-cookies), gbrain suite. |
| **Generation model** | Each `SKILL.md` is **AUTO-GENERATED** from `SKILL.md.tmpl` by `bun run gen:skill-docs` via `scripts/resolvers/*.ts`. Placeholder usage across templates: `{{SECTION…}}` 55, `{{PREAMBLE}}` 50, `{{OUTSIDE_LABEL}}` 27, `{{SECTION_INDEX}}` 21, `{{LEARNINGS_LOG}}` 15, `{{BASE_BRANCH_DETECT}}` 15, `{{GBRAIN_*}}`, `{{ASIDE_*}}`, `{{BROWSE_FALLBACK}}`, `{{UX_PRINCIPLES}}`, `{{TEST_VALUE_BAR}}`, `{{SAFE_GIT}}`, … |
| **Token finding** | Generated skills are 2–10× their templates: review 23.0 KB → 74.9 KB; design-review 13.7 KB → **132.1 KB**; office-hours 16.6 → 86.6 KB; ship 32.7 → 79.0 KB (+249 KB companions). The growth is mostly the shared preamble and inlined blocks. **ADAPT from `.tmpl` + companions with an OS-owned resolver; never bundle generated SKILL.md.** |
| Preamble | Runs `~/.claude/skills/gstack/bin/gstack-skill-start` (session/telemetry/onboarding/consent blocks), Conductor/Codex branching, `~/.gstack` writes. EXCLUDE. |
| Companions (value) | `review/{checklist.md, design-checklist.md, specialists/, sections/}`, `qa/references/issue-taxonomy.md`, `cso/sections/audit-phases.md`, `ship/sections/*`, `plan-eng-review/sections/*`, `office-hours/sections/*`, `spec/sections/*`. These carry the methodology. |
| **Browser** | `BROWSER.md`: drives the user's **real signed-in browser (Aside) first**, then a **persistent headless Chromium daemon** (`browse/`, compiled `$B`, ~70 commands), cookie import from the real browser, `/pair-agent` tunnel. States it "never substitutes curl or unit tests for the browser step". **Direct conflict with §23A** (local scripted verification first). EXCLUDE browser runtime, cookie import and pair-agent; QA *methodology* (issue taxonomy, regression thinking, acceptance) ADAPT into the local-first ladder. |
| Telemetry / update | `bin/gstack-telemetry-log`, `gstack-telemetry-sync` (sends to **Supabase**, consent-tiered, receipt-hashed), `gstack-analytics`, `gstack-update-check`, `gstack-upgrade` skill. EXCLUDE (§44, §41). |
| Runtime | Bun, TypeScript, compiled binaries, Chromium. |
| Tests | 1,442 test files (Bun). Not executed (content source). |
| License | MIT, © 2026 Garry Tan; `NOTICE.md` lists Apache-2.0-derived files (e.g. `lib/design-catalog.ts` from *impeccable*); `licenses/Apache-2.0.txt`. |

## 5. Karpathy Skills — `multica-ai/andrej-karpathy-skills` @ `2c606141936f1eeef17fa3043a72095b4765b9c2`

One skill (`skills/karpathy-guidelines/SKILL.md`, ~3 KB): Think Before Coding · Simplicity First · Surgical Changes · Goal-Driven Execution. Host wrappers: `.claude-plugin`, `.cursor/rules/*.mdc`, CLAUDE.md, CURSOR.md, EXAMPLES.md. No code, no network, no hooks. License: MIT declared in metadata; **no LICENSE text** (L-1, non-blocking per D-002). Integration: COPY the skill as engineering principles guidance.

## 6. Unlazy — `Leonxlnx/unlazy` @ `16671491f6679ad9378f52604d3bc2415b4120c7`

| Audit point | Finding |
|---|---|
| Content | `SKILL.md` (10.5 KB) + `references/` (gates, method, orchestration, dispatch, parallel, token-economy; 42 KB) + `templates/` (PLAN, gates-leaf, gates-node). |
| **Executable discipline** | `scripts/gate-check.mjs` (parse/approve/run/re-verify `CHECK:`/`EXPECT:` gates with definition digests and output fingerprints), `dispatch-check.mjs`, `gate-lint.mjs`, `stop-hook.mjs` (Claude Code Stop hook; structural backstop, never executes checks), `lib/` (gates, dispatch, process-tree, regex-worker, check-supervisor). Zero dependencies, Node ≥16. |
| Security design | Treats inherited ledgers/commands as untrusted; explicit approval bound to command, cwd, shell, PATH, platform; approvals stored in `~/.unlazy/approved`. |
| Conflicts | `install-hooks.mjs` defaults to the **project's** `.claude/settings.local.json` (`--shared` → `.claude/settings.json`, `--global` → `~/.claude/settings.json`). Project-local install conflicts with §2.3. The adapter must register the Stop hook centrally. |
| **Closure** | SKILL.md names `templates/`, `references/`, `scripts/`, `SECURITY.md` by relative path; tests assert "every local resource the skill names exists". → PRESERVE whole subsystem (minus `research/`, `.github/`). |
| Tests | **Executed: `npm test` exit 0, 188 checks ok, self-check 15/15** (Node 22.14.0, 39.7 s). |
| License | MIT, © 2026 Leonxlnx. |

## 7. Ponytail — `DietrichGebert/ponytail` @ `c982cd411abb53323c4baa1baa3c2f020b8d0b08`

| Audit point | Finding |
|---|---|
| Content | 6 skills (17.7 KB total): ponytail (lite/full/ultra), -audit, -debt, -gain, -help, -review. Ruleset source in `hooks/ponytail-instructions.js`. 11 worked examples. |
| Hooks | `claude-codex-hooks.json`: **SessionStart (startup/resume/clear/compact), SubagentStart, UserPromptSubmit** → inject ruleset every session; writes `$CLAUDE_CONFIG_DIR/.ponytail-active`, `~/.config/ponytail/config.json`, statusline nudges. Default mode "full". **Always-on**: conflicts with §2.5 and v1.0.1 default-off. EXCLUDE. |
| MCP | `ponytail-mcp/` server → EXCLUDE. |
| Ports | 10+ host directories (.cursor, .windsurf, .kiro, .qoder, .clinerules, .opencode, .openclaw, .devin, .grok, gemini-extension) → EXCLUDE (adapters generate their own). |
| Benchmarks | promptfoo configs calling GPT/Gemini/Claude (all telemetry/network hits are here, not runtime) → EXCLUDE from runtime; REFERENCE for P25 methodology. |
| License | MIT, © 2026 DietrichGebert. |

## 8. Graphify — `Graphify-Labs/graphify` @ `0b60d47e6cd9338c51143f39f35b6c45c8453385` (branch `v8`)

| Audit point | Finding |
|---|---|
| Identity | PyPI name **`graphifyy`** 0.9.74. v1.0.1's `integrations/graphify.yaml` says `pip install graphify-ai` → **incorrect package name** (finding G-1). |
| Engine | `graphify/` Python package: extract (tree-sitter, ~30 languages), build, cluster (communities), analyze, `affected.py` (reverse impact traversal), query (BFS), path, explain, report, wiki, exporters, content-hash AST cache. |
| CLI | `update <path>` (AST only, **no LLM**), `query "<q>"`, `path A B`, `explain X`, `affected X`, plus `install`, `hook install`, `watch`, `serve` (MCP). |
| **Executed** | Isolated venv (Python 3.14.7): `pip install .` **15 s, 151 MB**. `graphify update .` on a 2-dir fixture: **1.5 s → 50 nodes, 56 edges, 11 communities**. `graphify query "how is MCP checked"` returned a **6-node scoped subgraph with file:line locations**. Cache: `graphify-out/cache/ast/v0.9.74-s4/<sha256>.json`. |
| Output location | Default `graphify-out/` in the project; **`GRAPHIFY_OUT` env accepts an absolute path** → per-project graph can live in OS-managed state outside the project (resolves §2.3). |
| Side effects to EXCLUDE | `graphify install` writes "always_on" rule blocks into project `CLAUDE.md`/`AGENTS.md`/`.cursor`/Antigravity rules; `hook install` adds **post-commit/post-checkout git hooks with a detached background rebuild** and registers a git merge driver; `watch` (watchdog observer); `serve`/`graphify-mcp`; `mcp_ingest.py`. |
| LLM | Optional semantic extraction (`llm.py`: Anthropic, OpenAI, Gemini, Ollama, Bedrock, Kimi extras). Not needed for code graphs. |
| Extras | Huge optional matrix (neo4j, postgres, video/whisper, office, pdf, leiden, …). Core install needs only networkx, numpy, rapidfuzz, tree-sitter grammars. |
| Skills | `graphify/skills/<host>/` per-host skill copies + `references/` → ADAPT one canonical codebase skill. |
| Tests | 121 fixture dirs + many test files. Not executed in P1 (smoke-tested instead); full suite scheduled for P12. |
| License | Apache-2.0 (+ `LICENSE-MIT` for pre-relicensing portions, `NOTICE`). |

## 9. OpenDesign — `nexu-io/open-design` @ `53231d40b778d88eba23f35547bf99485d3ae9fc`

| Audit point | Finding |
|---|---|
| What it is | Commercial-backed design-agent workspace: `apps/` 4,064 (web app + **`apps/daemon`**), `packages/` 450, `plugins/` 1,829 (70 MB; `_official` 232 skills), `design-systems/` 4,015 (38 MB, **154 brand systems**), `design-templates/` 747 (38 MB), `skills/` 358 files, `prompt-templates/` 107, `craft/` 13, `e2e/` 256, `figma-plugin`, `deploy`, cloud pricing in README. |
| **High-value core** | `craft/` (136 KB): `anti-ai-slop.md`, `accessibility-baseline.md`, `color.md`, `typography.md`, `typography-hierarchy*.md`, `laws-of-ux.md`, `state-coverage.md`, `form-validation.md`, `animation-discipline.md`, `rtl-and-bidi.md`. Maps directly onto spec §8 and §27. |
| Design systems | Each system: `DESIGN.md` + **17 translated `DESIGN-*.md`**, `design-tokens.json`, `tokens.css`, `tailwind-v4.css`, components manifest, preview. Bundle `DESIGN.md` + tokens only, as an indexed Level-3 library; EXCLUDE translations and previews. |
| Duplication | 495 groups of byte-identical files inside the repo. `skills/brutalist-skill`, `skills/brandkit` share names with Taste but are **not byte-identical** (only 2 files identical across the two repos) → diverged versions; P2 chooses one. |
| Runtime | Node/pnpm monorepo, daemon, Vercel config. EXCLUDE runtime. |
| MCP | 1 MCP config file + 200 mentions → EXCLUDE. |
| License | Apache-2.0. |

## 10. Taste Skill — `Leonxlnx/taste-skill` @ `ce26fc25c0e5e8cab638f883de62d9a86ee5e45b`

| Audit point | Finding |
|---|---|
| Content | 13 skills: `taste-skill` (name `design-taste-frontend`, **87 KB ≈ 22k tokens**), taste-skill-v1 (21 KB), redesign, soft, minimalist, brutalist, stitch (+DESIGN.md), brandkit, output-skill, gpt-tasteskill, image-to-code, imagegen-frontend-web/mobile (36–40 KB). |
| Anti-slop criteria | `taste-skill` §0 brief inference + "Design Read", §1 three dials (variance/motion/density) with inference tables, §4 engineering directives, **§9 AI Tells (forbidden patterns: visual/CSS, typography, layout, content "Jane Doe" effect, external resources, production-test tells)** → inspectable design-review criteria (§27). |
| Token handling | Must be split into sections for Level-2/3 loading (never loaded whole). |
| Host dependence | image-to-code / imagegen-* require an image-generation tool (Codex-oriented) → host-conditional. |
| Executables | `skill.sh` (prints path), `scripts/*.mjs` (README asset processing) → EXCLUDE. `research/laziness/` → REFERENCE for completion domain. |
| License | MIT, © 2026 Leonxlnx. |

## 11. UI/UX Pro Max — `nextlevelbuilder/ui-ux-pro-max-skill` @ `09170eec67eefd46a7ae85de61b40c194020f997`

| Audit point | Finding |
|---|---|
| Engine | `src/ui-ux-pro-max/`: `scripts/search.py`, `core.py`, `design_system.py`, `reasoning_contract.py` (stdlib only) over `data/*.csv` + `data/stacks/` (22 stacks) + templates. `--design-system`, `--domain`, `--stack`, dial flags (`--variance/--motion/--density`), `--persist` to a project `design-system/` folder. |
| **Executed** | `python3 -m unittest` in `scripts/`: **164 tests OK (3.6 s)**. Sample `search.py "fintech dashboard trustworthy" --design-system` produced a full pattern/style/color/type recommendation offline. |
| Skills | `.claude/skills/`: ui-ux-pro-max (16 KB), design (14 KB), ui-styling (11 KB, has Python scripts + requirements), design-system, banner-design, brand, slides. `cli/assets/skills/` is a **duplicate copy** (192 identical groups). 1 symlink (`gallery/data/styles.csv` → src). |
| Executables | `cli/` (Bun installer with `update`/`uninstall`), `stack/scripts/setup.sh`, `scripts/*` validators. EXCLUDE installer. |
| MCP | **`stack/.mcp.json`: playwright, chrome-devtools, shadcn MCP servers** → EXCLUDE (also the reason the v1.0.1 MCP test failed on staging, fixed in P0). |
| Persist path | `--persist --output-dir <project-root>` writes design-system files into the project → acceptable only as genuine project-owned `DESIGN.md` state (§2.3); P2 decides the target path. |
| License | MIT, © 2024 Next Level Builder. |

## 12. Brag — `latent-spaces/brag` @ `cb89b9f44309b0bf4e3cb89e685fadf80c7999ed`

| Audit point | Finding |
|---|---|
| Content | `skills/brag/` (SKILL.md 9 KB, `slim.md`, `references/` step-1…4 + audio + tones, `scripts/analyze_music_cues.py` with `pyproject.toml` + `uv.lock`, **`assets/` 278 files / 16 MB**), `skills/brag-slim/SKILL.md` (7.8 KB, no bundled assets). 5 example projects; docs site. |
| Runtime | `/brag` requires **Hyperframes** (`npx hyperframes check`/render → network on first use + headless browser for render), Python via uv for music cues. `/brag-slim` builds everything with "the tools already on the machine". |
| **Closure gap** | `/brag` instructs reading external skills `hyperframes-core/-animation/-creative/-keyframes/-cli`, **not in this repo** (G-2). Bundling `/brag` complete requires sourcing those, or routing to `/brag-slim` by default. Decided in P2. |
| Model-specific dispatch | `/brag` switches to `/brag-slim` automatically on "Opus 5.5". |
| MCP / telemetry / background | None. |
| License | MIT, © 2026 Shunit Haviv Hakimi. |

## 13. Agent Beacon — `Asymptote-Labs/agent-beacon` @ `5937da1cd812660d256c367374b9752316f51cbc`

| Audit point | Finding |
|---|---|
| What it is | Go endpoint agent (853 `.go` files): `cli/beacon` (741), `cli/beacon-hooks` (116; per-harness hook parsers: session_start, pre_tool, post_tool, prompt_submit, permission_request, stop, subagent, compaction, cursor_event, codex_session_context, kiro, qwen, …), `pkg/asymptoteobserve`, OTel `collector-builder`, browser extension, macOS/Linux packaging, sandbox scenarios. |
| Setup posture | README: interactive setup **signs in through beacon.sh and preselects Beacon Cloud**; Local is an explicit opt-out. EXCLUDE all forwarding/cloud. |
| **Event schema** | Versioned JSONL (`schema_version: 1.0`): `event.{kind,action,category,id,fidelity}`, `harness.{name,version,collection_method}`, `session.{id,working_directory}`, `tool.{name,command,path}`, `gen_ai.usage.{input_tokens,output_tokens,cache_read}`, `severity`. Good REFERENCE model for P18 events (ECS-style, token usage included). |
| **Detection rules** | `rules/` 77 files in 10 categories (risky-command, prompt-injection, context-exfiltration, credential-access, sensitive-edit, approval-abuse, agent-control, external-access, resource-consumption, source-control). YAML with `match` (CEL expressions over events), `severity`, OWASP-LLM taxonomy, **embedded positive/negative test cases**. ADAPT as data; the OS needs its own evaluator (CEL subset). |
| Background | Endpoint agent, inventory heartbeat, forwarding → EXCLUDE (§2.5). |
| License | MIT, © 2026 Asymptote Labs. |

## 14. BeyondSEO — `beyondtahir/beyondseo` @ `c160b9d7ba3f8a8c9a11fd042ea218e61183d43b`

| Audit point | Finding |
|---|---|
| Package | `pyproject.toml`: `beyondseo` 2.9.1, Python ≥3.10, **core deps `beautifulsoup4`, `colorama` only**; extras `browser` (playwright), `reports` (reportlab), `sftp` (paramiko), `dev`, `hosting-test`; entry point `beyondseo`. |
| Engine (`src/beyondseo`, 385 KB) | engine (crawler), network, extract, evidence, findings, onsite, content, discovery, research, deep_research, reputation, backlinks, reports, review/compare, monitor (bounded `watch`), projects, publishing (FTP/SFTP site edits), render (Playwright), diagnostics, doctor, cli. |
| Knowledge | `SKILL.md` (17 KB), `playbooks/` (core, audit ×11, aeo-geo ×11, keyword-research ×8, competitor-research ×7, local-seo ×7, backlink-system ×14, strategy ×10, reputation, entity-seo, integrations ×6, templates ×14, examples), `references/` (audit-delivery, capabilities, crawler, measurement-boundaries, reputation), `docs/` (architecture, permissions, browser, website-work, lovable, …). |
| Layer mapping | Knowledge = playbooks/core + references; Workflows = playbooks/audit, strategy, research; Execution = CLI/engine; Evidence = `evidence.py` (`capture_quality`: usable / **absence_supported** / limits; positive observations survive partial captures, absence claims don't); Reporting = reports.py, templates; Website intelligence = crawl/discovery; Verification = `review compare` snapshots. |
| Evidence vs. spec | BeyondSEO already refuses absence claims on failed/partial captures (matches §28.2 "page could not be inspected"). It does **not** use the FACT/OBSERVATION/INFERENCE/HYPOTHESIS/UNKNOWN labels → mapping layer needed (P16). |
| Background | `monitor.watch`: 1–10,000 cycles, ≥60 s interval, foreground, fresh evidence folder per run. No daemon. |
| Browser policy | `render.py`/`browser-setup` install Chromium **only when setup is authorized**; doctor reports `playwright: null, chromium: not installed` by default → aligns with §28 browser-last. |
| Risky surface | `publishing.py` (16.7 KB): authenticated FTP/FTPS/SFTP edits to live sites ("authorised website work"); `examples/*-connection.json`. Requires an explicit authorization gate in P16. |
| **Executed** | Isolated venv, `pip install -e .`: CLI works (22 subcommands). Test suite: **250 run, 232 pass, 9 skipped, 9 fail/error**. Failures are in `test_browser_features` (6) and `test_trial_regressions` (2), which exercise rendering with the optional `browser` extra **not installed**, plus `test_doctor_preserves_execution_error` (1, cause UNKNOWN). |
| UNKNOWN | Whether all 9 failures disappear with `.[browser]` + Chromium installed. **How to verify:** P3 installs the extra in the isolated SEO venv and reruns. **Impact:** determines whether rendering is a supported fallback. |
| License | MIT, © 2026 Muhammad Tahir Ashraf (Beyond Tahir); `THIRD_PARTY_NOTICES.md`. |

---

## Cross-repo findings

| ID | Finding |
|---|---|
| X-1 | **MCP is present in 7 of 14 repos**: ECC, Ponytail, Graphify, UI/UX Pro Max, OpenDesign, Agent Beacon, Agency (plus mentions in Addy, gstack). Every one is separable from the non-MCP functionality. |
| X-2 | **Always-on behavior** ships by default in ECC hooks, Ponytail hooks, gstack (browser daemon, telemetry), Graphify (git hooks/watch when installed), OpenDesign (daemon), Beacon (endpoint agent). None of it may enter the OS runtime (§2.5). |
| X-3 | **Project-local writes** at install time: Unlazy (`.claude/settings.local.json`), Graphify (`CLAUDE.md`/`AGENTS.md`, `graphify-out/`, `.git/hooks`), UI/UX Pro Max (`design-system/` via `--persist`). Each needs an OS-controlled alternative (§2.3). |
| X-4 | **Executable runtimes worth preserving** and verified locally: Unlazy (188/188), UI/UX Pro Max engine (164/164), Graphify core (smoke OK), BeyondSEO (232/250, browser-extra failures). |
| X-5 | **Token hazards**: gstack generated skills up to 132 KB; Taste main skill 87 KB; OpenDesign libraries 38 MB each. Section-level loading is mandatory. |
| X-6 | **Host-port duplication**: most repos ship 5–15 per-host copies of the same content. The OS bundles one canonical copy; adapters render per-host forms (spec §2.2). |
| X-7 | **Closure gaps**: Brag `/brag` → external Hyperframes skills (G-2); Addy skills → shared `references/`; Unlazy → `scripts/lib`, templates; gstack → resolvers. |
| G-1 | v1.0.1 Graphify install command names the wrong package (`graphify-ai`; actual `graphifyy`). |
