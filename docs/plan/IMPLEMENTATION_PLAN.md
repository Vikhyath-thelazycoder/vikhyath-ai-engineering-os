# Vikhyath AI Engineering OS v2 — Implementation Plan (living document)

| Field | Value |
|---|---|
| Branch | `feat/v2-os-transformation` (from `main` @ `d77834e`, v1.0.1) |
| Spec | Vikhyath AI Engineering OS Master Build Spec (Updated) |
| Total phases | **28 (P0–P27)** |
| Execution model | Phases are grouped into **8 milestones (M0–M7)** (D-007). Within a milestone, every phase is still tested, verified, committed and updated in this plan. Work stops for user review **only at the end of each milestone**. |
| Hard gate | Spec §64 gate **passed** at the end of M1 (D-025). File-level tasks for P4–P27 are in [FILE_LEVEL_PLAN.md](FILE_LEVEL_PLAN.md); deviations found while building are recorded there as "As built" notes and in the decisions log. |
| Decisions | [docs/audit/21_AUDIT_DECISIONS.md](../audit/21_AUDIT_DECISIONS.md) |

Status vocabulary (spec §25): NOT_STARTED · PLANNED · IN_PROGRESS · PARTIALLY_COMPLETE · BLOCKED · READY_FOR_VERIFICATION · VERIFIED · COMPLETED · INTENTIONALLY_DEFERRED

## Milestones (review stops)

| Milestone | Phases | Status |
|---|---|---|
| M0 Baseline | P0 | **COMPLETED** |
| M1 Audit & final plan | P1, P2, P3 (ends at the spec §64 hard gate) | **COMPLETED** (gate passed, D-025) |
| M2 Foundation & bundle | P4, P5, P6, P7 | **COMPLETED** (awaiting user review) |
| M3 The brain | P8, P9, P10, P11, P18 | NOT_STARTED |
| M4 Main domains | P12, P13, P14, P15 | NOT_STARTED |
| M5 Specialist domains | P16, P17 | NOT_STARTED |
| M6 Hosts | P19, P20, P21, P22 | NOT_STARTED |
| M7 Dashboard & ship | P23, P24, P25, P26, P27 | NOT_STARTED |

## Phase index

| Phase | Name | Stage | Depends on | Status |
|---|---|---|---|---|
| P0 | Current repository audit | Audit | — | **COMPLETED** |
| P1 | Upstream deep audit (14 repos) | Audit | P0 | **COMPLETED** |
| P2 | Capability, domain & extraction architecture | Audit | P1 | **COMPLETED** |
| P3 | Cross-cutting audits, target architecture, definitive file-level plan — **GATE** | Audit/Plan | P2 | **COMPLETED** |
| P4 | Core runtime & CLI foundation | Build: core | P3 | **COMPLETED** |
| P5 | Provenance & third-party notices | Build: supply | P4 | **COMPLETED** |
| P6 | Upstream bundling (staging → local bundle) | Build: supply | P5 | **COMPLETED** |
| P7 | Capability registry (single source of truth) | Build: core | P6 | **COMPLETED** |
| P8 | Routing engine | Build: core | P7 | NOT_STARTED |
| P9 | Context engine (levels, budget, cache) | Build: core | P8 | NOT_STARTED |
| P10 | Project state, plan index, decision memory | Build: core | P4 | NOT_STARTED |
| P11 | Multi-project isolation | Build: core | P10 | NOT_STARTED |
| P12 | Codebase domain (Graphify) | Build: domain | P9, P11 | NOT_STARTED |
| P13 | Engineering domain (+ lifecycle, completion discipline, project docs) | Build: domain | P12 | NOT_STARTED |
| P14 | Design domain | Build: domain | P9 | NOT_STARTED |
| P15 | Testing domain + local-first web verification | Build: domain | P13 | NOT_STARTED |
| P16 | SEO domain + isolated BeyondSEO runtime | Build: domain | P15 | NOT_STARTED |
| P17 | Media domain (Brag) | Build: domain | P9 | NOT_STARTED |
| P18 | Observability (event model, history) | Build: core | P10 | NOT_STARTED |
| P19 | Claude Code adapter | Build: hosts | P8–P11, P18 | NOT_STARTED |
| P20 | Codex adapter | Build: hosts | P19 | NOT_STARTED |
| P21 | Cursor adapter | Build: hosts | P19 | NOT_STARTED |
| P22 | Antigravity adapter | Build: hosts | P19 | NOT_STARTED |
| P23 | Dashboard | Build: UX | P18 | NOT_STARTED |
| P24 | Update & rollback | Build: supply | P6, P7 | NOT_STARTED |
| P25 | Diagnostics & measured benchmarks | Verify | P4–P24 | NOT_STARTED |
| P26 | Documentation & migration guide | Docs | P25 | NOT_STARTED |
| P27 | Full integration, offline & host validation, final report | Verify | all | NOT_STARTED |

Ordering rationale vs. spec §66 anchors (D-004):
- **P4 core foundation is new.** v1.0.1 has no runtime (finding E-1), and every engine needs a package, CLI and test harness to live in.
- **The spec's "upstream audit" is split into P1–P3**, so the §64 gate items (matrices, target architecture, file-level plan) each have a verifiable phase.
- **P10 depends only on P4**, so project state can proceed in parallel with the registry/routing work if desired.

---

## P0 — Current repository audit · COMPLETED (2026-10-03)

| Item | Detail |
|---|---|
| Objective | Establish the factual v1.0.1 baseline before any change (spec §1, §98 steps 1–2). |
| Inputs | Repo @ `d77834e`; user's uncommitted `.claude-plugin/marketplace.json`. |
| Changes | Created branch; `.gitignore` += `.staging/`; added `docs/audit/{00,01,02,03,21}*.md`, `docs/audit/evidence/{phase0-file-inventory.tsv,upstream-staging-snapshot.yaml}`, this plan. `tests/security/test_security.py`: MCP walk now skips gitignored `.staging/` (it failed on `.staging/upstream/uiuxpromax/stack/.mcp.json`, which is upstream audit input, not plugin content). **No runtime file modified.** |
| Also done | Complete upstream snapshots of all 14 repos staged in `.staging/upstream/` (spec §3 staging rule, §98 steps 3–4); HEAD SHAs recorded. free-for-dev excluded and not fetched. |
| Tests | Baseline: unittest 20/20, doctor 50/0, validate 27/0 (with PyYAML). Without PyYAML: fails (E-1). |
| Acceptance criteria | ✔ every tracked file inventoried with hash · ✔ current routing, capability model and host support traced to evidence · ✔ every file classified (provisional) · ✔ gap analysis maps every spec area to a phase · ✔ MCP and free-for-dev status verified · ✔ v1.0.1↔v2 conflicts recorded with decisions. |
| Verification | Evidence files above; commands recorded in 01 §6–8. |
| Rollback | `git switch main && git branch -D feat/v2-os-transformation`; `rm -rf .staging`. |
| Evidence | `docs/audit/01_CURRENT_REPOSITORY_AUDIT.md` §1–11. |

## P1 — Upstream deep audit · COMPLETED (2026-10-03)

| Item | Detail |
|---|---|
| Objective | Audit all 14 complete snapshots per spec §3 steps 1–20 (code, config, scripts, hooks, agents/skills/workflows, plugin manifests, tests, deps, install/update, runtime, host assumptions, license files, network, filesystem, telemetry/background behavior, **MCP presence**). |
| Inputs | `.staging/upstream/*` @ SHAs in `upstream-staging-snapshot.yaml`. |
| Changes | `docs/audit/04_UPSTREAM_REPOSITORY_AUDIT.md` (one section per repo); `10_PROVENANCE_LICENSE_AUDIT.md` (inventory only, non-blocking per D-002); `12_SECURITY_AUDIT.md` (third-party script/hook/network/telemetry findings); `evidence/upstream-file-hashes/<repo>.tsv` (path, bytes, sha256). Pin decision per repo recorded in 21. |
| Dependencies | P0. |
| Tests | Script check: every tracked file of every snapshot appears in its hash TSV; every repo section answers all 20 audit points (or UNKNOWN + why/how/impact per §88). |
| Acceptance criteria | 14/14 repos audited; every MCP surface located; every executable/install/hook mechanism listed with a risk note; pins chosen. |
| Rollback | Docs only; delete files. |
| Known so far | MCP surfaces already seen: ECC (installed plugin exposes chrome-devtools MCP), UI/UX Pro Max (`stack/.mcp.json`: playwright, chrome-devtools, shadcn). Must be excluded from extraction (§2.1). |
| Result | **Done.** 14/14 repos audited (`04_UPSTREAM_REPOSITORY_AUDIT.md`), license inventory (`10_…`), third-party security audit with 16 controls (`12_…`), scanner `tools/audit/scan_upstream.py`, per-file hashes for all 26,588 files (inventory check: 14/14 PASS). Runtimes executed: Unlazy 188/188 ok; UI/UX Pro Max 164/164 OK; Graphify install + update + query OK; BeyondSEO 232/250 (9 browser-extra failures, UNKNOWN to confirm in P3). Pins: D-008. |
| Note | Largest audit phase (≈26k upstream files; OpenDesign alone is 12,940). Hash inventories are generated; reading focuses on executable surfaces, manifests, skills/agents and runtimes. |

## P2 — Capability, domain & extraction architecture · COMPLETED (2026-10-03)

**Result:** 7 domains / 62 capabilities (`tools/audit/domain-model.yaml`); machine-readable extraction rules (`tools/audit/extraction-rules.yaml`) applied to all 26,588 upstream files → **2,644 bundled files (50.7 MB)** after P3's AgentShield exclusion: ADAPT 973, COPY 644, PRESERVE 1,027; REFERENCE 686; EXCLUDE 21,257, each with a reason code. Dependency closure: **0 open gaps** (37 accepted with reasons; 23 closure files added). 37 in-bundle duplicate groups → content-addressed storage in P6. Docs 05–09 written; 05/06 generated by `tools/audit/render_matrix_docs.py`. Review correction: ECC `taste*` skills reclassified (music-video + paid fal.ai).


Produces `05_CAPABILITY_MATRIX.md` (§61), `06_DOMAIN_MAPPING.md` (§5–12), `07_SOURCE_EXTRACTION_MATRIX.md` (COPY/ADAPT/WRAP/REFERENCE/PRESERVE/EXCLUDE per component, §38–39), `08_DUPLICATION_ANALYSIS.md` (§37), `09_DEPENDENCY_RUNTIME_MATRIX.md`. Acceptance: every capability has the §13 metadata draft; every domain/subdomain is justified by a source path (no empty domains); complete-subsystem claims (Graphify, BeyondSEO, Brag) are proven by dependency traces.

## P3 — Cross-cutting audits, target architecture, file-level plan · COMPLETED (2026-10-03, gate passed D-025) · **GATE**

**Result:** docs 11, 13–20 written; decisions D-009…D-022; **file-level plan for P4–P27 in [FILE_LEVEL_PLAN.md](FILE_LEVEL_PLAN.md)**. Measured OLD-MODEL baseline: ≈30.4k est. tokens always loaded (v1.0.1 ≈212 + ECC ≈30,170). Host evidence: Claude Code installed (v1.0.1 + ECC); Codex/Cursor/Antigravity dirs present but CLIs absent and v1.0.1 not installed in them; the Antigravity "Runtime Tested" claim is unsupported. UNKNOWNs resolved: BeyondSEO browser extra → 250/250 OK (557 MB browser); AgentShield → `security-scan` excluded. §64 checklist: audit ✔, upstream audit ✔, capability matrix ✔, domain mapping ✔, gap analysis ✔, target architecture ✔, implementation plan ✔ (file-level), migration order ✔ (D-022), test plan ✔ (doc 17). **Open: Q-1 (BLOCKING for P6 only), Q-2/Q-3 (IMPORTANT, defaults set).** Gate passes on user review.


Produces `11_HOST_COMPATIBILITY_AUDIT`, `13_TOKEN_CONTEXT_AUDIT` (measured OLD-MODEL baseline incl. installed upstream plugins), `14_MULTI_PROJECT_ISOLATION_AUDIT`, `15_DASHBOARD_OBSERVABILITY_AUDIT`, `16_UPDATE_ROLLBACK_AUDIT`, `17_TESTING_AUDIT`, `18_MIGRATION_RISKS`, `19_OPEN_QUESTIONS`, `20_TARGET_ARCHITECTURE_RECOMMENDATION`, `00_EXECUTIVE_SUMMARY` (final), and **rewrites P4–P27 below as file-level tasks** (FILE · ACTION · PURPOSE · DEPENDENCIES · INPUTS · OUTPUTS · TEST · ROLLBACK, spec §63) with a migration order and test plan. Acceptance: §64 checklist complete; no open BLOCKING question; user review.

---

## P4 — Core runtime & CLI foundation · COMPLETED (2026-10-03, commit `dcdfd52`)

| Item | Detail |
|---|---|
| Changes | `pyproject.toml` (package `vikhyath`, Python ≥3.10, PyYAML); `vikhyath/{__init__,__main__,paths,cli}.py`; `vikhyath/diagnostics/{doctor,validate,benchmark}.py`; `scripts/{doctor,validate,benchmark}` → compatibility wrappers; `tests/manifests` read `VERSION`; `tests/unit/*`; CI installs the package. |
| Tests | 32/32; doctor 52/0 (50 legacy + 2 environment); validate 27/0; no-PyYAML path prints an install hint instead of crashing (E-1 fixed). |
| Acceptance | ✔ fresh-venv install · ✔ counts match v1.0.1 · ✔ `benchmark --baseline` reproduces doc 13 (ECC 120,682 B ≈ 30,170 est. tokens; total 121,523 B ≈ 30,380). |
| Deviations | Benchmark counts description-less agents by file stem (as hosts display them): v1.0.1 = 841 B, not 850 B; doc 13 corrected. Planned commands not yet built exit 2 with "planned for P<n>". |
| Evidence | `docs/evidence/P4/run.md` |
| Rollback | `git revert dcdfd52` |

## P5 — Provenance & third-party notices · COMPLETED (2026-10-03, commit `0d8553e`)

| Item | Detail |
|---|---|
| Changes | `vikhyath/bundle/{rules,provenance,notices}.py`; `tools/audit/extraction_matrix.py` imports the shared engine; generated `third_party/licenses.json` + `THIRD_PARTY_NOTICES.md`; `tests/bundle/{test_rules,test_provenance}.py`. |
| Tests | 45/45. Matrix regenerated from scratch after the move: byte-identical. |
| Acceptance | ✔ one provenance record per planned file, all valid, `original_hash` = audited blob SHA-1 · ✔ 14 upstreams: 12 MIT, 2 Apache-2.0, Karpathy recorded as declared-MIT without license text. |
| Rollback | `git revert 0d8553e` |

## P6 — Upstream bundling & central install · COMPLETED (2026-10-03, commit `2d08a91`)

| Item | Detail |
|---|---|
| Changes | `vikhyath/bundle/{closure,checks,store,build,fetch}.py`, `vikhyath/bundle/transforms/{__init__,gstack,rewrites}.py`, `vikhyath bundle fetch|build|verify|list`, `scripts/install`; rules updates (gstack generated files → renderer inputs, Angular MCP doc and UI/UX tooling tests excluded); CONTRIBUTING + PR template + security test updated for D-023; `tests/bundle/{test_build,test_transforms}.py`. |
| Result | Known-good bundle **`c98667e034f7`**: 2,594 files (50.3 MB), 64 transformed, 0 errors (closure, MCP config, provenance). Bundled Unlazy and UI/UX Pro Max self-tests pass. **A fresh networked `scripts/install` reproduced the identical bundle id** (153 MB sparse download vs ~1.1 GB full clones; 1m54s). |
| Tests | 60/60. |
| Deviations | **D-026:** hardlinked blob store dropped (broke Unlazy's single-link tamper check; saved only ~1 MB): files are plain copies, integrity via provenance hashes. **D-027:** gstack renderer uses strong anchors only (a weak anchor had put ship's table into review); unresolved placeholders (15 files) and adaptation debts (8 MCP mentions, 52 gstack runtime paths) are listed in `BUILD.json` and owned by P13–P17. Planned `strip_directives`/`section_split` transforms replaced by targeted rewrites now and section indexing in P9. |
| Open | Nothing installed into the real `~/.vikhyath` yet (all builds in scratch homes). |
| Evidence | `docs/evidence/P6/run.md` |
| Rollback | `git revert 2d08a91`; delete `$VIKHYATH_HOME/bundles/<id>` |

## P7 — Capability registry · COMPLETED (2026-10-03)

| Item | Detail |
|---|---|
| Changes | `capabilities/<domain>/<sub>/{card.yaml,CARD.md}` ×62, `capabilities/<domain>/domain.yaml` ×7, `capabilities/defaults.yaml`; `vikhyath/registry/{schema,loader,generate}.py`; `vikhyath registry check|cards|build|list|show`; `bundle build` writes `<bundle>/registry.yaml`; `config/priorities.yaml` → conflict hierarchy (role names) + `domain_defaults`; doctor/validate/tests/CI/docs moved off the retired files. **Removed:** `config/capabilities.yaml`, `integrations/*.yaml` (9), `tools/audit/domain-model.yaml`, `tests/validation/`. |
| Result | One registry source (D-028). Generated registry has all 29 spec §13 fields for all 62 capabilities; provenance fields derived, never authored. Web QA classes: 7 CORE + browser-fallback FALLBACK (headless OPTIONAL / visible FALLBACK). Real bundle rebuilt: same id **`c98667e034f7`**, registry valid, self-tests pass. Docs 05/06 and the extraction matrix regenerate unchanged from the cards. |
| Tests | 79/79 (19 new registry tests incl. planted-violation checks); doctor 45/0 (was 52: 9 integration-file checks replaced by 3 registry checks, `config/capabilities.yaml` YAML check removed); validate 20/0 (registry + 14 pins instead of 9 integration files). |
| Acceptance | ✔ exactly one registry (retired files gone; grep test finds no references outside history docs) · ✔ no repo-name capability ids (validator + test) · ✔ web QA classes recorded (§23A.13) · ✔ schema-validated, every §13 field present. |
| Findings for later phases | Engineering's 17 cards total ≈2,341 est. tokens: above D-014's provisional L1 ≤2k/domain, so P9 must load routed cards (or an index), not whole domains. `config/routing.yaml` is still v1 repo-keyed (replaced in P8). `conflicts` empty by design (D-028). |
| Evidence | `docs/evidence/P7/run.md` |
| Rollback | `git revert <P7 commit>`; delete `$VIKHYATH_HOME/bundles/<id>/registry.yaml` (regenerated by the next build). |

## M2 review summary

M2 (P4–P7) delivered the foundation: the `vikhyath` core + CLI (P4), shared extraction rules + provenance + notices (P5), a reproducible local bundle with central install (P6), and the single capability registry generated into every bundle (P7). Bundle `c98667e034f7`: 2,594 files, 0 errors, reproducible from pins. **Next: M3 (P8 routing → P9 context → P10 state → P11 isolation → P18 observability)** after user review.

## P4–P27 — summary (file-level tasks: [FILE_LEVEL_PLAN.md](FILE_LEVEL_PLAN.md))

| Phase | Objective (outline) | Key acceptance criteria (outline) |
|---|---|---|
| P4 Core foundation | Python core package + `vikhyath` CLI; declared deps (fixes E-1); test harness; `scripts/{doctor,validate,benchmark}` become compatibility wrappers (§69). | Fresh venv: install + `vikhyath --version` + existing 20 tests pass (version assertions de-hardcoded). |
| P5 Provenance | Machine-readable provenance schema (§36), third-party notices tree (D-002), provenance validator. | Every bundled file traceable to repo+SHA+path+hash. |
| P6 Bundling | staging → extract → validate → bundle pipeline (§35); duplication control (§37); MCP stripping; known-good bundle snapshot. Replaces zero-vendor checks (D-001). | Bundle reproducible from pins; hashes match provenance; no MCP in bundle. |
| P7 Registry | One registry with full §13 metadata; retires `config/capabilities.yaml`, `integrations/*.yaml`, priority duplication (C-1). | Single source; schema-validated; web-QA classification CORE/OPTIONAL/FALLBACK recorded (§23A.13). |
| P8 Routing | Deterministic router per §15 (classification → domain → subdomain → capability set); semantic retrieval fallback only. | Spec routing examples (§14, §23A.14, §70) produce expected capability sets as tests. |
| P9 Context | Levels 0–3, budgets (§47), hash-keyed session cache (§17). | Measured bytes per level; cache hit skips reread. |
| P10 Project state | Compact `.vikhyath/` state, plan index (§49), decisions (§50–52), change classification (§54–56). | State read ≪ full docs; plan reconciliation test. |
| P11 Isolation | Structural per-project isolation (§2.4). | Concurrent A/B/C test: no cross-project reads. |
| P12 Codebase | Graphify integration as codebase-intelligence layer (§4.8, §23); failure fallback (§74). | Affected-file query narrows code surface on a fixture repo. |
| P13 Engineering | Engineering capabilities from ECC/Addy/Agency/gstack/Karpathy/Unlazy/Ponytail; lifecycle UNDERSTAND→RECONCILE; completion states; project doc templates; requirements question engine (§53). | Scenarios A, B, C (§70) route and plan correctly. |
| P14 Design | Unified design domain (OpenDesign + Taste + UI/UX Pro Max); inspectable anti-slop criteria (§27). | Scenario D routes to design only. |
| P15 Testing | Testing domain; local-first web verification ladder (§23A); browser lazy/fallback policy + `BROWSER_FALLBACK_ACTIVATED` telemetry. | Scenarios G/H; no browser started in default path. |
| P16 SEO | SEO domain; isolated, pinned BeyondSEO runtime with health/start/stop/test; evidence model FACT…UNKNOWN (§28). | Scenarios E, F, I; core env untouched by SEO deps. |
| P17 Media | Media domain from Brag (§29). | Scenario H (launch video) activates no backend capabilities. |
| P18 Observability | Event model (§30), history, redaction (§78–79). | Events emitted for full routing lifecycle; no secrets in logs. |
| P19–P22 Hosts | Thin adapters for Claude Code, Codex, Cursor, Antigravity (§33); separate statuses "files installed" vs. "host runtime verified" (§34). | Per-host evidence; no business logic in adapters. |
| P23 Dashboard | Data-driven, lightweight local dashboard with lifecycle states (§31–32); no daemon. | Starts on demand, sleeps on idle, reflects real state. |
| P24 Update/rollback | `vikhyath update` / `rollback` (§41–42). | Simulated broken update rolls back bundle+registry+provenance atomically. |
| P25 Diagnostics/benchmarks | Complete doctor (§59); measured token & performance benchmarks, OLD vs NEW (§92–93). | Benchmarks are measured, labeled estimates where tokenizer unavailable. |
| P26 Documentation | `docs/` per §80–83; README/CONTRIBUTING/SECURITY rewritten; migration guide (§69). | Docs describe the actual final architecture. |
| P27 Integration & report | Final test matrix (§91), offline validation (§45), host validations, final report (§95). | Every acceptance criterion in §94 has evidence or a recorded limitation. |

---

## Change history

| Date | Phase | Change |
|---|---|---|
| 2026-10-03 | P0 | Plan created; 28 phases defined (D-004); P0 completed; P1 set as next. Licensing made non-blocking (D-002). |
| 2026-10-03 | P0 | D-005: selective real extraction (actual files copied/adapted into the bundle; no reference-only capabilities). |
| 2026-10-03 | M1 | D-006: dependency closure (selected content pulls in everything it needs). D-007: 8 review milestones. M1 started. |
| 2026-10-03 | P1 | P1 completed: upstream audit, license inventory, security audit, pins (D-008). P2 started. |
| 2026-10-03 | P2 | P2 completed: domain model, extraction rules + per-file matrix, closure 0 open, duplication & runtime matrices. P3 started. |
| 2026-10-03 | P3 | P3 ready for verification: cross-cutting audits, target architecture, D-009…D-022, file-level plan; M1 awaiting user review (Q-1 blocks P6). |
| 2026-10-03 | M1 | Gate passed (D-025). Q-1 → build at install (D-023); Q-3 → NOT VERIFIED where host absent (D-024). M2/P4 started. |
| 2026-10-03 | P4 | P4 completed: `vikhyath` package + CLI (pyproject, Python ≥3.10, PyYAML declared), doctor 52/0 (50 legacy + 2 env), validate 27/0, measured `benchmark --baseline` (121,523 B ≈ 30,380 est. tokens), wrappers kept (§69), 32/32 tests, CI installs the package. Evidence: docs/evidence/P4/run.md. P5 started. |
| 2026-10-03 | P5 | P5 completed: shared rule engine `vikhyath/bundle/rules.py` (matrix regenerated byte-identical), §36 provenance records + validator (2,644 planned records, all valid, hashes = audited blob SHAs), `third_party/licenses.json` + generated `THIRD_PARTY_NOTICES.md` (12 MIT, 2 Apache-2.0), 45/45 tests. P6 started. |
| 2026-10-03 | P6 | P6 completed: `vikhyath bundle fetch/build/verify/list`, gstack template renderer (strong anchors), targeted rewrites with drift detection, hard MCP-config check, closure on transformed output, atomic activation with `previous`, `scripts/install`. Known-good bundle `c98667e034f7`: 2,594 files, 0 errors, Unlazy + UI/UX Pro Max self-tests pass from the bundle; **fresh networked install reproduces the identical bundle id** (153 MB sparse download, 1m54s). D-026 (single-link files), D-027 (render gaps/debts → P13–P17). 60 tests. Evidence: docs/evidence/P6/run.md. P7 started. |
| 2026-10-03 | P7 | Plan audit (user request): header, P3 heading, P4–P6 result sections, chronological history; FILE_LEVEL_PLAN "As built" notes for P5/P6 and D-027 duty in P13–P17; summary/doc 08 counts corrected. |
| 2026-10-03 | P7 | P7 completed: 62 capability cards + rendered L1 CARD.md, `vikhyath/registry` (schema, loader, generator), `registry.yaml` generated into every bundle (rebuilt `c98667e034f7`, valid), `vikhyath registry` CLI; retired `config/capabilities.yaml`, `integrations/*.yaml`, `domain-model.yaml`; priorities → role-named hierarchy + domain defaults (D-028). 79 tests, doctor 45/0, validate 20/0. Evidence: docs/evidence/P7/run.md. **M2 completed; awaiting user review before M3.** |
