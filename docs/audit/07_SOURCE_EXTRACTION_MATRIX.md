# 07 — Source Extraction Matrix (Phase 2, spec §38–39)

## Machine-readable source of truth

| Artifact | Role |
|---|---|
| [`tools/audit/extraction-rules.yaml`](../../tools/audit/extraction-rules.yaml) | Ordered glob rules per repo → decision, capability, reason code. **The P6 bundler consumes this same file**, so the plan and the build cannot drift. |
| [`tools/audit/domain-model.yaml`](../../tools/audit/domain-model.yaml) | Domains/subdomains/capabilities; validated against the rules (no unknown capability, no empty capability). Seeds the P7 registry. |
| [`tools/audit/extraction_matrix.py`](../../tools/audit/extraction_matrix.py) | Applies rules to every file, traces dependency closure, exits non-zero on any error or open gap. |
| [evidence/extraction-matrix/](evidence/extraction-matrix/) | **One row per upstream file (26,588 rows)**: decision, reason, capability, bytes, path. |
| [evidence/closure-gaps.tsv](evidence/closure-gaps.tsv) | Every reference from a bundled file to a non-bundled file, with OPEN/ACCEPTED status. |
| [evidence/extraction-summary.json](evidence/extraction-summary.json) | Per-repo × decision and per-capability totals. |

## Result (run 2026-10-03, exit 0)

| Decision | Files | Size |
|---|---:|---:|
| ADAPT | 974 | 12.6 MB |
| COPY | 644 | 7.7 MB |
| PRESERVE | 1,027 | 30.4 MB |
| **Bundled total** | **2,645** | **50.7 MB** |
| REFERENCE (staging only; design input) | 686 | 24.1 MB |
| EXCLUDE | 21,257 | 508.7 MB |

| Repo | ADAPT | COPY | PRESERVE | REFERENCE | EXCLUDE |
|---|---:|---:|---:|---:|---:|
| addy | 34 | 9 | — | 112 | 56 |
| agency | 76 | 1 | — | 2 | 302 |
| beacon | 77 | 1 | — | 75 | 1,506 |
| beyondseo | 1 | 140 | 58 | 2 | 20 |
| brag | — | 1 | 290 | 21 | 56 |
| ecc | 391 | 1 | 18 | 272 | 3,530 |
| graphify | 8 | 3 | 537 | 37 | 371 |
| gstack | 130 | 3 | — | 108 | 2,436 |
| karpathy | — | 2 | — | 1 | 6 |
| opendesign | 49 | 467 | — | 6 | 12,418 |
| ponytail | 5 | 13 | — | 36 | 115 |
| taste | 12 | 1 | — | 13 | 40 |
| uiuxpromax | 190 | 1 | 95 | — | 396 |
| unlazy | 1 | 1 | 29 | 1 | 5 |

## Exclusions by reason

| Reason | Files | Size | Examples |
|---|---:|---:|---|
| PRODUCT_RUNTIME | 13,413 | 307.5 MB | OpenDesign apps/daemon/packages/plugins, Beacon Go agent, UI/UX Pro Max gallery/stack |
| OUT_OF_DOMAIN | 3,498 | 85.4 MB | ECC healthcare/logistics/homelab/trading skills, gstack iOS/gbrain suites, Agency game-dev/GIS/finance |
| DOC_ASSET | 204 | 61.0 MB | README imagery, Taste/Brag docs sites |
| TRANSLATION | 1,780 | 16.5 MB | ECC `docs/<locale>/`, OpenDesign `DESIGN-<lang>.md` ×17 per system |
| UPSTREAM_DEV | 267 | 11.2 MB | Graphify `worked/`, tests of excluded tooling |
| HOST_PORT | 949 | 6.4 MB | `.kiro/`, `.cursor/`, `.opencode/`, `pi/`, per-host skill copies |
| ALWAYS_ON | 389 | 5.8 MB | gstack `browse/` daemon, Ponytail hooks, ECC `ecc2/` daemon |
| INSTALLER | 307 | 5.2 MB | Agency `scripts/`, UI/UX Pro Max `cli/`, BeyondSEO `install_skill.py` |
| DUPLICATE | 98 | 3.9 MB | OpenDesign vendored copies of Taste/UI-UX-Pro-Max skills |
| GENERATED | 63 | 2.5 MB | gstack generated `SKILL.md` (bundled from `.tmpl` instead) |
| REPO_META | 117 | 2.1 MB | CI, issue templates |
| PAID_API | 119 | 1.0 MB | OpenDesign `fal-*`/`venice-*`/`sora`, ECC `taste-application`/`taste-distillation` (fal.ai) |
| MCP | 27 | 0.2 MB | ECC `.mcp.json`, Ponytail `ponytail-mcp/`, Graphify `serve.py`, UI/UX Pro Max `stack/.mcp.json` |
| TELEMETRY | 12 | 0.1 MB | gstack `gstack-telemetry-*`, `gstack-analytics`, `supabase/` |
| HOST_SPECIFIC_TOOL | 8 | <0.1 MB | OpenDesign `figma-*` |
| SUPERSEDED | 6 | <0.1 MB | Addy `using-agent-skills` (OS router replaces it), ECC `seo` (BeyondSEO is canonical) |

## Dependency closure (D-006)

The trace scans every bundled text file for markdown links, `<skill-dir>/` paths, `./`/`../` paths, `references/…`/`scripts/…`/`templates/…`-style paths, JS/TS `import`/`require`, and Python relative imports. Each reference is resolved inside the same repo; a bundled file referencing a non-bundled file is a gap.

**Result: 37 references to non-bundled files, 0 open.** Fixes made during P2 (each added to the bundle):

| Repo | Added for closure | Needed by |
|---|---|---|
| graphify | `graphify/mcp_ingest.py` | Unconditional import in `extract.py`. **Documented exception to the MCP exclusion**: it parses MCP config files as graph *data*; it is not a server, client, config or runtime. |
| ecc | `scripts/eval-harness.js`, `scripts/lib/eval-harness/*` (8), `docs/architecture/eval-harness-frameworks.md` | `skills/eval-harness` |
| ecc | `scripts/setup-package-manager.js`, `scripts/lib/{package-manager,utils,agent-data-home,path-safety}.js` | `skills/tdd-workflow` (full transitive `require` closure: 15 files computed) |
| ecc | `scripts/codemaps/generate.ts` | `agents/doc-updater` |
| uiuxpromax | `scripts/evaluate-relevance.py`, `scripts/relevance_metrics.py` | Engine relevance tests |
| addy | `docs/agents.md` | All 4 agents |
| unlazy | `research/validation-protocol.md`; `scripts/install-hooks.mjs` kept **inert** | `references/method.md`, `token-economy.md`; upstream self-check test |
| beyondseo | `SECURITY.md` | docs |

Changed to **ADAPT** so that the bundled instruction no longer points at an excluded mechanism: Unlazy `SKILL.md` (hook install → OS central registration), BeyondSEO `SKILL.md` (host installation → OS routing), ECC `rules/README.md` (install.sh → stack-pack activation).

Changed to **REFERENCE** (consumed at bundle-build time, never at runtime): gstack `scripts/resolvers/**` (the OS template renderer resolves kept placeholders such as `{{BASE_BRANCH_DETECT}}`, `{{SECTION_INDEX}}`, `{{UX_PRINCIPLES}}`, `{{TEST_VALUE_BAR}}` and drops `{{PREAMBLE}}`, `{{GBRAIN_*}}`, `{{ASIDE_*}}`, `{{BROWSE_*}}`), gstack `lib/cso/**`.

The 37 accepted references are listed with reasons in `extraction-rules.yaml → accepted_gaps` (doc/index mentions, template self-references, references removed by an ADAPT rewrite).

## Complete-subsystem decisions (spec §39), proven by dependency evidence

| Subsystem | Evidence that it must stay intact |
|---|---|
| Unlazy | SKILL.md names `templates/`, `references/`, `scripts/` by relative path; its tests assert "every local resource the skill names exists"; `gate-check.mjs` imports `lib/*`. 188/188 tests pass. |
| Graphify | Python package with internal imports (`extract.py` → `mcp_ingest`, extractors, cache); CLI verified end-to-end. Disabling `hook`/`install`/`watch`/`serve` happens in the OS wrapper, not by deleting modules. |
| BeyondSEO runtime | Installable package (`src/beyondseo`, entry point `beyondseo`); SKILL.md calls `scripts/run.py doctor`; 232/250 tests pass without the browser extra. |
| UI/UX Pro Max engine | `search.py` → `core.py`/`design_system.py` over `data/*.csv`; tests load root `scripts/`. 164/164 pass. |
| Brag | `/brag` SKILL.md reads `references/step-*.md`, `slim.md`, `assets/` (music/sfx/fonts) and runs `scripts/analyze_music_cues.py`. |

## Changes after review

| Change | Why |
|---|---|
| ECC `skills/taste`, `taste-application`, `taste-distillation`: ADAPT(design) → EXCLUDE | Description check showed they are music-video aesthetics; two require the paid fal.ai API (`FAL_KEY`). Name-based selection was wrong; every ECC pick was then verified against its `description:`. |
