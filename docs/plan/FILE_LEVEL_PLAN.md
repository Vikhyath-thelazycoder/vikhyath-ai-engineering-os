# File-Level Implementation Plan — P4…P27 (spec §63, §84)

Companion to [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md). Produced at the P3 gate from audit docs 01–21.

Conventions:
- **Action:** CREATE · MODIFY · REFACTOR · REPLACE · REMOVE · GENERATE (output of an OS command).
- **Rollback:** every phase is one or more commits on `feat/v2-os-transformation`; phase rollback = `git revert <phase commits>`. Machine-local changes are rolled back by deleting `$VIKHYATH_HOME/<path>`, noted where relevant.
- **Execution order inside M3 is P8 → P9 → P10 → P11 → P18.** The event log exists before the domain phases (M4) that emit events.

---

## M2 · P4 — Core runtime & CLI foundation

| File | Action | Purpose | Deps | Inputs → Outputs | Test |
|---|---|---|---|---|---|
| `pyproject.toml` | CREATE | Package `vikhyath`, `requires-python >=3.10`, dependency `PyYAML>=6`, dynamic version from `VERSION`, console script `vikhyath = vikhyath.cli:main`, package data | — | VERSION → installable package | `pip install -e .` in a fresh venv; `vikhyath --version` == `VERSION` |
| `vikhyath/__init__.py`, `vikhyath/__main__.py` | CREATE | Version export; `python -m vikhyath` | pyproject | — | `python -m vikhyath --version` |
| `vikhyath/paths.py` | CREATE | `repo_root()`, `vikhyath_home()` (`$VIKHYATH_HOME` or `~/.vikhyath`), bundle pointer resolution | — | env → paths | `tests/unit/test_paths.py` (env override, defaults) |
| `vikhyath/cli.py` | CREATE | argparse with every subcommand from doc 20 §2; P4 implements `--version`, `doctor`, `validate`, `benchmark --baseline`; others exit 2 with "available in P<n>" | paths | argv → JSON/text, exit code | `tests/unit/test_cli.py` |
| `vikhyath/diagnostics/doctor.py`, `validate.py` | CREATE | Port all checks from `scripts/doctor` (50) and `scripts/validate` (27) to Python; add PyYAML/Python-version checks; `--offline`/`--online` kept | cli | repo → report + exit code | Same pass counts as v1.0.1 on the unchanged repo; `tests/unit/test_diagnostics.py` |
| `vikhyath/diagnostics/benchmark.py` | CREATE | `--baseline`: measure always-loaded description bytes of installed plugins (doc 13 method); replaces hard-coded output (B-1); labels estimates | cli | plugin dirs → table | Fixture plugin dir with known bytes → exact numbers |
| `scripts/doctor`, `scripts/validate`, `scripts/benchmark` | MODIFY | Thin wrappers: `exec python3 -m vikhyath <cmd> "$@"`, with a clear message if the package is not installed (§69 compatibility) | cli | — | CI runs the wrappers |
| `tests/manifests/test_manifests.py` | MODIFY | Read the expected version from `VERSION` (MR-04) | — | — | Suite passes |
| `tests/unit/__init__.py`, `test_cli.py`, `test_paths.py`, `test_diagnostics.py` | CREATE | Unit coverage for P4 code | — | — | `python -m unittest discover -s tests` |
| `.github/workflows/ci.yml` | MODIFY | `pip install -e .` instead of bare PyYAML; run unittest + `vikhyath doctor` + `vikhyath validate` | pyproject | — | CI green |

**As built (COMPLETED, `dcdfd52`):** as planned; doctor = 52 checks (50 legacy + 2 environment).

**Acceptance:** fresh-venv install works; all old + new tests pass; doctor/validate counts match v1.0.1; `vikhyath benchmark --baseline` reproduces doc 13's measured numbers on this machine. **Evidence:** `docs/evidence/P4/` run logs.

## M2 · P5 — Provenance & third-party notices

| File | Action | Purpose | Deps | Inputs → Outputs | Test |
|---|---|---|---|---|---|
| `vikhyath/bundle/rules.py` | CREATE | Shared rule engine (glob→regex, first-match classify, reason codes) extracted from `tools/audit/extraction_matrix.py` | P4 | rules yaml → decisions | Same per-file decisions as the P2 matrix (diff = 0) |
| `tools/audit/extraction_matrix.py` | MODIFY | Import `vikhyath.bundle.rules` (one engine) | rules.py | — | Matrix output byte-identical to P2 |
| `vikhyath/bundle/provenance.py` | CREATE | §36 record type, writer, validator (required fields, hash formats, license present) | rules.py | matrix + hashes → `provenance.json` | `tests/bundle/test_provenance.py` |
| `vikhyath/bundle/notices.py` | CREATE | Collect upstream LICENSE/NOTICE files per bundled repo (D-002); generate the summary | provenance | staging → notices dir + summary | 14 repos covered; Karpathy recorded as "MIT declared, no text" |
| `THIRD_PARTY_NOTICES.md` | GENERATE | Human-readable attribution summary | notices.py | — | Structural test: every bundled repo listed |

**As built (COMPLETED, `0d8553e`):** as planned. File count changed to 2,594 in P6 (rules updates).

**Acceptance:** a provenance record for all planned files (2,644 at P5; 2,594 after P6), with `original_hash` equal to the audited blob SHA-1; validator passes; notices complete.

## M2 · P6 — Upstream bundling (distribution: build at install, D-023)

**As built (COMPLETED, `2d08a91`):** `store.py` keeps hashing only (no blob store, **D-026**); `strip_directives.py`/`rewrite_paths.py`/`section_split.py` replaced by `transforms/rewrites.py` (4 targeted rewrites with drift detection) and `transforms/gstack.py` (template renderer, **D-027**); section indexing moves to P9 `context/sections.py`; added `closure.py` (shared tracer, rendered-sibling rule), `fetch.py` (sparse pinned fetch), `checks.py` (hard MCP config / soft debts); `tests/bundle/{test_build,test_transforms}.py`. Rows below are the original plan, kept for traceability.

| File | Action | Purpose | Deps | Inputs → Outputs | Test |
|---|---|---|---|---|---|
| `vikhyath/bundle/store.py` | CREATE | Content-addressed blob store (sha256), dedup (37 groups) | P5 | files → `blobs/` | Dedup count matches doc 08 |
| `vikhyath/bundle/transforms/strip_directives.py` | CREATE | Remove host/vendor directives (install steps, preambles, MCP tool calls, telemetry steps) via per-source patterns | store | text → text | Golden-file tests per source |
| `vikhyath/bundle/transforms/rewrite_paths.py` | CREATE | Rewrite `<skill-dir>/…`, `${CLAUDE_PLUGIN_ROOT}/…`, `~/.claude/skills/<x>/…` to bundle-relative ids | store | text → text | Golden files; closure re-check |
| `vikhyath/bundle/transforms/gstack_template.py` | CREATE | Render gstack `.tmpl`: resolve kept placeholders (`SECTION`, `SECTION_INDEX`, `BASE_BRANCH_DETECT`, `UX_PRINCIPLES`, `TEST_VALUE_BAR`, `SAFE_GIT`, …) from REFERENCE resolvers' semantics; drop `PREAMBLE`, `GBRAIN_*`, `ASIDE_*`, `BROWSE_*`, `OUTSIDE_*`, telemetry | store | `.tmpl` + sections → rendered md | Every rendered file has no `{{` left; size ≤ template + sections |
| `vikhyath/bundle/transforms/section_split.py` | CREATE | Split oversized files (Taste 87 KB, large playbooks) into addressable sections with a manifest | store | md → sections + manifest | Section bytes sum = source bytes |
| `vikhyath/bundle/checks.py` | CREATE | Closure (0 open), forbidden patterns (`mcp__`, `mcpServers`, `chrome-devtools-mcp`, Supabase/telemetry endpoints, `~/.claude/skills/gstack`), license presence, D-021 whitelist by hash | transforms | bundle → report | `tests/bundle/test_checks.py` (planted violations detected) |
| `vikhyath/bundle/build.py` | CREATE | Pipeline: verify staging hashes → decisions → transforms → store → `index.json` + `provenance.json` + notices → checks → runtime self-tests → `BUILD.json` | all above | pins + rules → `$VIKHYATH_HOME/bundles/<id>/` | `tests/bundle/test_build.py`: same inputs → same `bundle_id` |
| `vikhyath/cli.py` | MODIFY | `bundle build | verify | list` | build.py | — | CLI tests |
| `scripts/install` | CREATE | Central install: create `$VIKHYATH_HOME/core` venv, `pip install` the repo, then per Q-1 either fetch pins + `bundle build` (B) or copy the committed bundle (A) | build.py | — | Install into a temp `VIKHYATH_HOME` in CI |
| `tests/security/test_security.py` | MODIFY | Replace `test_no_vendor_directories` with `test_bundle_integrity` (D-001); extend the no-MCP walk to the built bundle (with the D-021 exception) | checks.py | — | Suite passes |
| `.github/workflows/ci.yml` | MODIFY | Replace "Verify NO Vendor Copies" with `vikhyath bundle verify` | — | — | CI green |
| `CONTRIBUTING.md`, `.github/pull_request_template.md` | MODIFY | Replace "never copy third-party code" with the extraction-rules/provenance process | — | — | Doc review |

**Acceptance:** reproducible bundle; 0 open closure gaps; 0 forbidden patterns; Unlazy (188) and UI/UX Pro Max (164) self-tests pass from the bundle.

## M2 · P7 — Capability registry

**As built (COMPLETED, `3eb2195`):** 62 `card.yaml` seeded from the domain model (0 field mismatches) and edited with priority, security_class, cache_strategy, activation_conditions, verification_requirements, related, fallback; `CARD.md` is **rendered** from each card by `vikhyath registry cards` and freshness-checked (not hand-written, D-028); added `capabilities/defaults.yaml` (domain order, host_compatibility) and `capabilities/<domain>/domain.yaml` (purpose, order); `vikhyath/bundle/rules.py` `load_capabilities()` replaces `load_domain_model()`/`known_capabilities()` for every bundle module and audit tool; `bundle build` writes `registry.yaml` into each bundle and refreshes it on reuse; CLI `vikhyath registry check|cards|build|list|show`; doctor/validate check the registry and the 14 upstream pins instead of `capabilities.yaml`/`integrations/`; `tests/validation/test_integrations.py` → `tests/structural/test_registry.py` (registry) + `tests/structural/test_repo_health.py` (its non-registry tests); conflict-hierarchy level 4 renamed `engineering-methodology` (`tests/routing/test_routing.py` updated); CI step `vikhyath registry check --no-bundle`; docs pointing at the retired files updated (README, CONTRIBUTING, SECURITY, AGENTS, CLAUDE, entry skills). Evidence: `docs/evidence/P7/run.md`.

| File | Action | Purpose | Deps | Inputs → Outputs | Test |
|---|---|---|---|---|---|
| `capabilities/<domain>/<sub>/card.yaml` ×62 | GENERATE then edit | Authoritative per-capability metadata (spec §13 fields that are not provenance-derived: triggers, context_level, priority, security_class, activation_conditions, verification_requirements, related, conflicts, fallback, enabled, web_qa_class) | P6 | `tools/audit/domain-model.yaml` → cards | `tests/structural/test_registry.py` |
| `capabilities/<domain>/<sub>/CARD.md` ×62 | CREATE | L1 summary ≤250 est. tokens | cards | — | Size test |
| `vikhyath/registry/schema.py`, `loader.py`, `generate.py` | CREATE | Merge cards + bundle provenance → `registry.yaml` per bundle (source repos/paths, commit, license, token_cost_estimate are generated) | P6 | cards + provenance → registry | Every §13 field present for all 62 |
| `tools/audit/domain-model.yaml` | REMOVE (after generation) | Single source of truth becomes `capabilities/**/card.yaml`; `extraction_matrix.py` reads the cards | registry | — | Matrix still passes |
| `config/capabilities.yaml`, `integrations/*.yaml` (9) | REMOVE | Superseded by registry + provenance (C-1) | registry | — | No references remain (grep test) |
| `config/priorities.yaml` | MODIFY | Keep `conflict_hierarchy`; replace repo-keyed priorities/defaults with domain-level defaults | registry | — | Routing tests (P8) |
| `tests/validation/test_integrations.py` | REPLACE | → `tests/structural/test_registry.py` | — | — | — |
| `tests/security/test_security.py` | MODIFY | Pinned-SHA check reads provenance instead of `capabilities.yaml` | — | — | — |

**Acceptance:** exactly one registry; no repo-name capability ids; web QA classes recorded (§23A.13).

## M3 · P8 — Routing engine

**As built (COMPLETED):** `config/routing.yaml` v2 (D-029: change types, roles, limits, project policy, 20 rules, 8 path globs); `vikhyath/routing/{classify,rules,select,fallback_bm25,router}.py`; `vikhyath route "<request>" [--paths] [--capability] [--new|--existing] [--stack] [--brief]` (JSON by default); `tests/routing/scenarios.yaml` (19 spec scenarios with expected + forbidden sets and a spec-name alias table) + `test_scenarios.py`; `tests/routing/test_routing.py` replaced by behaviour tests; `vikhyath validate` routing section validates config v2 + 5 smoke routes (the v1 repo-keyed check is gone); `seo/ai-search` card depends on `seo/evidence`; entry skill `skills/vikhyath-routing/SKILL.md` calls the CLI; CLAUDE.md/AGENTS.md/Antigravity skill point at `vikhyath route`. Evidence: `docs/evidence/P8/run.md`.

| File | Action | Purpose | Deps | Test |
|---|---|---|---|---|
| `config/routing.yaml` | REPLACE | v2 schema: change-type classifier (§54) + rules (keywords, regex, path globs, project phase, new/existing) → domain/subdomain; forbidden pairings | P7 | Schema test |
| `vikhyath/routing/classify.py`, `rules.py`, `select.py`, `fallback_bm25.py`, `router.py` | CREATE | §15 pipeline; conflicts via `priorities.yaml`; BM25 over CARD.md when no rule is confident; JSON result | P7 | Unit tests per module |
| `vikhyath/cli.py` | MODIFY | `route "<request>" [--paths] [--capability]` | router | CLI test |
| `tests/routing/scenarios.yaml`, `tests/routing/test_scenarios.py` | CREATE | Spec §14 examples, §23A.14 web-QA examples, §70 A–I: expected **and forbidden** capabilities | router | All pass |
| `tests/routing/test_routing.py` | REPLACE | Old YAML-shape tests → behavior tests | — | — |
| `skills/vikhyath-routing/SKILL.md` | REFACTOR | Thin entry: call `vikhyath route`, then `vikhyath context` | router | Description ≤ budget |

**Acceptance:** all scenarios pass; routing p95 < 100 ms (measured).

## M3 · P9 — Context engine

**As built (COMPLETED):** `config/budgets.yaml`; `vikhyath/context/{sections,budget,cache,loader,levels}.py` (D-030); `vikhyath/project/identity.py` pulled forward from P10 (cache keys need the project id); CLI `bootstrap` and `context` (`--route`, `--level 1|2`, `--file/--section` for L3, `--session`, `--no-cache`, `--json`); tests `tests/context/{fixtures,test_budgets,test_cache}.py`. Evidence: `docs/evidence/P9/run.md`.

| File | Action | Purpose | Test |
|---|---|---|---|
| `config/budgets.yaml` | CREATE | D-014 values, documented rationale | Schema test |
| `vikhyath/context/levels.py`, `budget.py`, `sections.py`, `cache.py`, `loader.py` | CREATE | L0–L3 assembly, section extraction, hash-keyed per-project cache, load log | `tests/context/test_budgets.py`, `test_cache.py` |
| `vikhyath/cli.py` | MODIFY | `bootstrap`, `context <cap> [--level]` | CLI tests |

**Acceptance:** L0 ≤1.5k est. tokens on fixtures; second identical load = cache hit with no file reread; L3 only with an explicit flag.

## M3 · P10 — Project state, plan index, decisions

**As built (COMPLETED):** all listed modules (identity was pulled into P9); `config/questions.yaml` (question bank, added); templates ×9; CLI `project init|status|questions|answer|relink`, `state`, `plan index|show|locate|add-task|set-status|reconcile`, `decide add|list|show`; bootstrap/route/context read the state; `tests/project/test_project.py` (one module instead of `tests/project/*`). D-031. Evidence: `docs/evidence/P10/run.md`.

| File | Action | Purpose | Test |
|---|---|---|---|
| `vikhyath/project/identity.py`, `state.py`, `plan_index.py`, `decisions.py`, `change.py`, `lifecycle.py`, `questions.py`, `reconcile.py` | CREATE | D-011 layout; §18–19, §49–56; completion states §25 | `tests/project/*` |
| `templates/project-docs/*.md` (PRD, TRD, ARCHITECTURE, SYSTEM_WORKFLOW, SECURITY, DESIGN, FEATURES, IMPLEMENTATION_PLAN, PROJECT_DECISIONS) | CREATE | §20 structures | Template lint |
| `vikhyath/cli.py` | MODIFY | `project init|status|relink`, `state`, `plan`, `decide` | CLI tests |

**Acceptance:** state read ≪ full docs (bytes measured); scenario "add Google Maps navigation to bookings" lands in the existing booking phase with no new mini-plan file (§21).

## M3 · P11 — Multi-project isolation

**As built (COMPLETED):** as planned, plus guard/lock/atomic in `project/{plan_index,decisions,reconcile,lifecycle}.py` and `context/cache.py` (not only `loader.py`/`state.py`); violation hooks for P18. D-032. Evidence: `docs/evidence/P11/run.md`.

| File | Action | Purpose | Test |
|---|---|---|---|
| `vikhyath/isolation/guard.py`, `locks.py`, `atomic.py` | CREATE | Path guard, per-project locks, atomic writes | `tests/isolation/test_multi_project.py`, `test_concurrency.py`, `test_cache_keys.py` |
| `vikhyath/context/loader.py`, `vikhyath/project/state.py` | MODIFY | Route every read/write through the guard and atomic writer | Same |

**Acceptance:** doc 14 tests pass.

## M3 · P18 — Observability (built before M4)

**As built (COMPLETED):** `vikhyath/events/{schema,redact,log,rules_cel}.py`; emission from CLI bootstrap/route/context, `ContextLoader.finish`, `project/{reconcile,decisions}` and the isolation guard; CLI `events list|observe|rules`; tests `tests/events/{test_events,test_rules}.py` + `tests/unit/test_redact.py`. The 4 observability cards already existed (P7), so no card was created. D-033. Evidence: `docs/evidence/P18/run.md`.

| File | Action | Purpose | Test |
|---|---|---|---|
| `vikhyath/events/schema.py`, `log.py`, `redact.py` | CREATE | Doc 15 envelope, per-project JSONL, redaction | `tests/unit/test_redact.py` (planted secrets) |
| `vikhyath/events/rules_cel.py` | CREATE | CEL-subset evaluator; loads adapted Beacon rules from the bundle | Each rule's embedded tests as unit tests |
| `capabilities/observability/*` | CREATE | 4 cards | Registry test |
| router/context/project modules | MODIFY | Emit lifecycle events | Event-sequence test for one routed request |

## M4 · P12 — Codebase (Graphify)

| File | Action | Purpose | Test |
|---|---|---|---|
| `vikhyath/runtimes/graphify.py` | CREATE | Install into `runtimes/graphify-<lock>`, set `GRAPHIFY_OUT=$VIKHYATH_HOME/projects/<id>/graph`, allow `update/query/path/explain/affected`, block `hook/install/watch/serve`, health check, §74 fallback | `tests/runtimes/test_graphify.py` (+ opt-in upstream pytest) |
| `vikhyath/routing/router.py` | MODIFY | Existing-project code changes → impact step (`affected`) → code-surface limit | `tests/context/test_code_surface.py` (≤12 files on fixture) |
| `capabilities/codebase/*` | CREATE | 3 cards + sections | Registry test |
| `skills/vikhyath-codebase/SKILL.md` | CREATE | Entry skill | Budget test |

## M4 · P13 — Engineering

| File | Action | Purpose | Test |
|---|---|---|---|
| `capabilities/engineering/*/sections.yaml`, `CARD.md` (17) | CREATE | Map L2/L3 sections into the bundle (layered review/security per doc 08) | Registry + size tests |
| `config/lifecycle.yaml` | CREATE | UNDERSTAND→PLAN→IMPLEMENT→TEST→VERIFY→RECONCILE; completion states | Lifecycle tests |
| `workflows/*.md` (5) | REMOVE | Superseded by `config/lifecycle.yaml` + capability sections | grep test |
| `vikhyath/runtimes/unlazy.py` | CREATE | Run `gate-check.mjs` from the bundle; opt-in central Stop-hook registration (never project-local) | Unlazy self-test (188) |
| `skills/vikhyath-engineering`, `-security`, `-review`, `-production` | REFACTOR | Thin entry skills (compat, MR-01) | Budget test |
| `agents/engineering-architect.md`, `security-reviewer.md`, `production-reviewer.md` | REFACTOR | Frontmatter (H-3); domain roles | Structural test |

**Acceptance:** scenarios A, B, C (routing + plan behavior); D-027: every unresolved gstack placeholder and adaptation debt in engineering/testing files replaced or removed (BUILD.json lists none for them).

## M4 · P14 — Design

| File | Action | Purpose | Test |
|---|---|---|---|
| `capabilities/design/*` (10) | CREATE | Cards + sections (Taste sections, OpenDesign craft, UI/UX Pro Max engine, design-systems index) | Registry tests |
| `vikhyath/runtimes/uiux.py` | CREATE | Invoke the bundled `search.py` (stdlib), `--persist` only to the project's `DESIGN.md`/design-system path | UI/UX self-test (164) |
| `vikhyath/project/decisions.py` | MODIFY | Design decision memory (§52) | Unit test |
| `skills/vikhyath-design/SKILL.md` | CREATE | Entry skill | Budget test |

**Acceptance:** scenario D activates design only; D-027 design debts (gstack design-review/consultation placeholders) cleared.

## M4 · P15 — Testing & local-first web verification

| File | Action | Purpose | Test |
|---|---|---|---|
| `config/webqa.yaml` | CREATE | Ladder order §23A.1 | Schema test |
| `vikhyath/verify/ladder.py`, `detect.py`, `evidence.py`, `browser.py`, `checks/{static,config,types,lint,build,unit,integration,http,state,security,a11y,dom,console,perf}.py` | CREATE | Run the cheapest sufficient checks; TESTED/NOT_TESTED/BLOCKED/BROWSER_ONLY/UNKNOWN (§23A.15); `BROWSER_FALLBACK_ACTIVATED` | `tests/webqa/*` with `tests/fixtures/webapp/` |
| `vikhyath/runtimes/playwright.py` | CREATE | Explicit install into `runtimes/playwright-browsers`, bounded sessions, always terminated | Process test (no browser left running) |
| `capabilities/testing/*` (8), `skills/vikhyath-testing/SKILL.md` | CREATE | Cards + entry | Registry/budget tests |

**Acceptance:** the spec's web-verification scenarios (checkout flow via deterministic checks; mobile-header overlap via bounded fallback; SEO without default browser) pass; no browser starts on the default path.

## M5 · P16 — SEO

| File | Action | Purpose | Test |
|---|---|---|---|
| `vikhyath/runtimes/seo.py` | CREATE | `runtimes/seo-<lock>` venv; extras on demand; doctor; start/stop | BeyondSEO suite: 232 pass core-only (browser tests not applicable); **250/250 with the browser extra** (P3 baseline) |
| `vikhyath/seo/evidence.py` | CREATE | FACT/OBSERVATION/INFERENCE/HYPOTHESIS/UNKNOWN over `capture_quality` (§28.2) | Unit tests incl. failed-capture → "could not be inspected" |
| `vikhyath/seo/authorization.py` | CREATE | Explicit per-task gate for `website-work` (SEC-11) | Test: blocked without authorization |
| `capabilities/seo/*` (16), `skills/vikhyath-seo/SKILL.md` | CREATE | Cards + entry | Scenarios E, F, I |

## M5 · P17 — Media

| File | Action | Purpose | Test |
|---|---|---|---|
| `vikhyath/runtimes/brag.py` | CREATE | `/brag-slim` default; full `/brag` only if Hyperframes is detected (Q-4); uv env for music cues | Dry run on a fixture project |
| `capabilities/media/*` (4), `skills/vikhyath-media/SKILL.md` | CREATE | Cards + entry | Scenario H (no backend capabilities) |

## M6 · P19–P22 — Host adapters

| File | Action | Purpose | Test |
|---|---|---|---|
| `vikhyath/adapters/base.py` | CREATE | One template set → host files; adapters contain no routing/state logic | `tests/hosts/test_no_logic.py` |
| `vikhyath/adapters/claude_code.py`, `hooks/hooks.json`, `.claude-plugin/plugin.json` (MODIFY) | CREATE/MODIFY | SessionStart → `vikhyath bootstrap`; optional Stop gate | `tests/hosts/test_claude_code.py`; RUNTIME_VERIFIED in this host |
| `vikhyath/adapters/codex.py`, `.codex-plugin/plugin.json` (MODIFY), `.agents/plugins/marketplace.json` | CREATE/MODIFY | Codex packaging + hooks; README command corrected (H-4) | Schema tests; runtime per Q-3 |
| `vikhyath/adapters/cursor.py` | CREATE | `vikhyath adapters install --host cursor` → `~/.cursor/skills/vikhyath*/` (+ optional hooks) | File tests; runtime per Q-3 |
| `vikhyath/adapters/antigravity.py`, `.agents/skills/vikhyath-os/SKILL.md` (REPLACE, generated) | CREATE | `agy` plugin layout / `~/.gemini/config/skills/` | `agy plugin validate` if available; else NOT VERIFIED |

## M7 · P23 — Dashboard

| File | Action | Purpose | Test |
|---|---|---|---|
| `vikhyath/dashboard/server.py`, `api.py`, `lifecycle.py`, `static/index.html` | CREATE | Doc 15 design | `tests/dashboard/*` (start, idle exit, fixture data) |

## M7 · P24 — Update & rollback

| File | Action | Purpose | Test |
|---|---|---|---|
| `vikhyath/update/update.py`, `rollback.py`, `gc.py` | CREATE | Doc 16 design | `tests/update/*` (broken update, forced rollback, interrupted build) |

## M7 · P25 — Diagnostics & measured benchmarks

**Carried in from P18 (D-033):** pass all diagnostics output (doctor, validate, benchmark) through `vikhyath.events.redact` (spec §78 "redact sensitive values from diagnostics").

| File | Action | Purpose | Test |
|---|---|---|---|
| `vikhyath/diagnostics/doctor.py` | MODIFY | All §59 checks; detect separately installed upstream plugins and report their measured cost (MR-02/03) | Fixture-based tests |
| `vikhyath/diagnostics/benchmark.py` | MODIFY | OLD vs NEW per scenario (§92), performance (§93) | Reproducible run |
| `docs/benchmarks/RESULTS.md` | GENERATE | Measured results with estimate labels | — |

## M7 · P26 — Documentation & migration

| File | Action |
|---|---|
| `docs/architecture/{TARGET_ARCHITECTURE,CAPABILITY_MODEL,DOMAIN_MODEL,ROUTING_ARCHITECTURE,CONTEXT_ENGINE,PROJECT_STATE,MULTI_PROJECT_ISOLATION,UPSTREAM_BUNDLING,PROVENANCE_SYSTEM,HOST_ADAPTERS,DASHBOARD_ARCHITECTURE,OBSERVABILITY,SECURITY_MODEL,UPDATE_ROLLBACK,SEO_ARCHITECTURE,TESTING_ARCHITECTURE}.md` | CREATE (§81, §82) |
| `docs/migration/V1_TO_V2.md` | CREATE (§69 command mapping, MR-01/02) |
| `README.md`, `CLAUDE.md`, `AGENTS.md`, `CONTRIBUTING.md`, `SECURITY.md`, `CHANGELOG.md` | MODIFY (remove "zero vendoring", "Runtime Tested" claims; describe the actual architecture) |

## M7 · P27 — Integration, offline, hosts, final report

| File | Action |
|---|---|
| `tests/integration/test_scenarios_e2e.py` | CREATE (§70 A–I end-to-end through CLI) |
| `tests/offline/test_offline.py` | CREATE (network blocked) |
| `docs/FINAL_IMPLEMENTATION_REPORT.md` | CREATE (§95 items 1–43, §91 matrix) |
