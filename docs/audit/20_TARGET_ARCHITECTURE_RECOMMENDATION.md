# 20 — Target Architecture Recommendation (Phase 3)

Derived from the evidence in 01–19. Decisions D-009…D-020 in `21_AUDIT_DECISIONS.md`.

## 1. Shape: one core + thin host adapters

```
                     USER (Claude Code | Codex | Cursor | Antigravity)
                                        │
            ┌───────────────────────────┴───────────────────────────┐
            │  HOST ADAPTER (generated files only, no business logic) │
            │  entry skills (≤10) · SessionStart → L0 bootstrap ·     │
            │  optional opt-in Stop gate · manifests                  │
            └───────────────────────────┬───────────────────────────┘
                                        │  `vikhyath …` CLI (JSON in/out)
┌───────────────────────────────────────┴──────────────────────────────────────────┐
│ VIKHYATH CORE (Python package `vikhyath`, central install)                         │
│ session → project identity → state load → classify → domain/subdomain → impact →  │
│ capability selection → context budget → targeted context → (work by host model) → │
│ verify ladder → state reconciliation → plan index → events → dashboard data        │
│ registry · routing · context+cache · project state · isolation guard · events ·    │
│ bundle/provenance · update/rollback · runtimes · verify · diagnostics · dashboard   │
└───────────────┬──────────────────────────────────┬────────────────────────────────┘
                │ reads                             │ starts on demand (never daemons)
      $VIKHYATH_HOME/bundles/current         isolated runtimes: graphify-venv · seo-venv ·
      (content-addressed, provenance)         uiux (stdlib) · unlazy (node) · brag (uv) ·
                                              playwright (optional, fallback only)
```

The host model does the reasoning. The core does deterministic work: identity, routing, selection, budgets, caching, state, verification orchestration and events. **No MCP anywhere; no background process.**

## 2. Repository layout (the plugin repo is the source of the central install)

| Path | Contents | Notes |
|---|---|---|
| `pyproject.toml` | Package `vikhyath`, Python ≥3.10, deps: `PyYAML`; console script `vikhyath` | Fixes E-1 |
| `vikhyath/cli.py`, `__main__.py` | argparse CLI: `bootstrap, route, context, state, plan, decide, verify, test, doctor, validate, benchmark, bundle, update, rollback, runtime, dashboard, adapters, project` | One entry point for every host |
| `vikhyath/paths.py` | `VIKHYATH_HOME` (default `~/.vikhyath`), bundle resolution (`bundles/current`) | |
| `vikhyath/registry/` | Load/validate the single capability registry (generated per bundle from `capabilities/**/card.yaml` + bundle index) | Replaces `config/capabilities.yaml` + `integrations/*.yaml` (C-1) |
| `vikhyath/routing/` | Request classification (§54 change types), deterministic domain/subdomain rules (`config/routing.yaml` v2), impact hook into codebase, BM25 fallback over cards, selection + conflicts (`config/priorities.yaml`) | No LLM inside the router |
| `vikhyath/context/` | Levels L0–L3, budgets (`config/budgets.yaml`), section extraction, hash-keyed per-project cache, load log | |
| `vikhyath/project/` | Identity, `.vikhyath/` state, plan index, decisions (incl. security/design decision memory), change classification/impact, lifecycle (new vs existing), requirements question engine, plan reconciliation | |
| `vikhyath/isolation/` | Path guard, locks, atomic writes | |
| `vikhyath/events/` | JSONL event log, redactor, CEL-subset risk evaluator over adapted Beacon rules | |
| `vikhyath/bundle/` | Rule engine (shared with `tools/audit`), build pipeline, transforms (gstack template renderer, Taste section splitter, path rewriter, directive stripper), content-addressed store, provenance writer, license/notice carrier | |
| `vikhyath/update/` | `update`, `rollback`, `gc` | |
| `vikhyath/runtimes/` | `graphify`, `seo`, `uiux`, `unlazy`, `brag`, `playwright` wrappers: install, health, run, stop; block excluded subcommands | |
| `vikhyath/verify/` | Local-first ladder (static → config → types → lint → build → unit → integration → HTTP/API → DB/state → security → a11y → DOM → headless → visible), project-type detection, evidence writer, browser-fallback policy + event | §23A |
| `vikhyath/diagnostics/` | doctor/validate/benchmark | `scripts/*` become wrappers (§69) |
| `vikhyath/dashboard/` | stdlib server + `static/index.html` | doc 15 |
| `vikhyath/adapters/` | Generators for the 4 hosts' files from one template set | |
| `capabilities/<domain>/<subdomain>/` | `card.yaml` (registry metadata, spec §13 fields), `CARD.md` (L1 summary ≤ 250 tokens), `sections.yaml` (L2/L3 file+section map into the bundle) | OS-authored; domain-first (§5) |
| `config/` | `routing.yaml` (v2 rules), `budgets.yaml`, `priorities.yaml` (conflict hierarchy kept), `webqa.yaml` (ladder) | |
| `tools/audit/` | Scanner, extraction rules, domain model, matrix, renderer | The rules file is shared with the bundler |
| `skills/` | Entry skills: `vikhyath-routing` (main), `vikhyath-engineering`, `-security`, `-review`, `-production` (compat), `vikhyath-codebase`, `-design`, `-testing`, `-seo`, `-media` | ≤ 800 tokens of descriptions total (doc 13) |
| `agents/` | Domain roles with frontmatter (fixes H-3) | |
| `hooks/hooks.json` | Claude Code: SessionStart → `vikhyath bootstrap --host claude-code`; Stop gate only if enabled | |
| `.claude-plugin/`, `.codex-plugin/`, `.agents/plugins/`, `plugin.json` | Host packaging (kept) | |
| `THIRD_PARTY_NOTICES.md` | Generated summary; full texts carried in the bundle | D-002 |
| `tests/`, `docs/` | doc 17 layout; docs per spec §80–83 | |

## 3. Machine-local layout (`$VIKHYATH_HOME`, default `~/.vikhyath`)

```
core/                      venv with the `vikhyath` package (central install)
bundles/<id>/ current previous     content-addressed bundle versions (doc 16)
runtimes/graphify-<lock>/ seo-<lock>/ brag-<lock>/ playwright-browsers/
projects/<project_id>/     graph/ (GRAPHIFY_OUT), cache/, events/, sessions/, dashboard.json
config.yaml                user prefs (dashboard autostart, budgets overrides, enabled hooks)
```

Per project (project-owned only, §2.3): `<project>/.vikhyath/{state,plan-index,decisions,verification}.yaml` and, for new projects, `docs/{PRD,TRD,ARCHITECTURE,SYSTEM_WORKFLOW,SECURITY,DESIGN,FEATURES,IMPLEMENTATION_PLAN,PROJECT_DECISIONS}.md` (Q-2).

## 4. Request lifecycle (spec §15, §19, §99)

1. **SessionStart hook** → `vikhyath bootstrap` prints L0 (≤1.5k tokens): host, project id, phase, compact state, capability index, plan pointer.
2. The model receives the request and calls `vikhyath route "<request>" [--paths …]`. The router:
   - classifies the request (new project / change type);
   - applies deterministic domain → subdomain rules;
   - for existing projects with code impact, runs the **codebase** step (`graphify update` if stale, then `affected`/`query`);
   - selects capabilities with conflicts resolved;
   - applies the budget;
   - returns JSON: capabilities, context plan (path#section, level, bytes), lifecycle step (UNDERSTAND/PLAN/IMPLEMENT/TEST/VERIFY/RECONCILE), required verification, blocking questions.
3. The model calls `vikhyath context <capability> [--level L2]` to get exactly the planned sections (cache-aware; CONTEXT_LOADED events).
4. Work happens in the host.
5. `vikhyath verify` runs the local-first ladder (browser only as a recorded fallback).
6. `vikhyath state reconcile` updates the plan index, task status (§25 states), decisions and verification evidence. Events feed the dashboard.

## 5. Bundle build (P5–P6)

`vikhyath bundle build` takes the pins plus `extraction-rules.yaml`:
1. fetch or verify the staging snapshots;
2. check every source blob hash against `upstream-file-hashes`;
3. apply decisions;
4. run transforms for ADAPT (directive stripping, path rewrites, gstack template rendering, Taste/large-file sectioning, MCP removal);
5. write content-addressed blobs, `index.json`, `provenance.json` and license/notice files;
6. run closure, no-MCP and forbidden-pattern checks plus runtime self-tests;
7. mark the bundle known-good.

Reproducible: same inputs → same `bundle_id`. Distribution is per Q-1 (recommended: build at install).

## 6. Domain-first capability set

7 domains, 62 capabilities (`06_DOMAIN_MAPPING.md`). Upstream names appear only in provenance. Registry metadata per capability = spec §13 fields. Bundle-derived fields (`source_repositories`, `source_paths`, `commit_sha`, `license`, `token_cost_estimate`) are **generated** from provenance, so there is one source of truth (§13, §68).

## 7. Non-negotiables mapped to mechanisms

| Spec rule | Mechanism | Verified by |
|---|---|---|
| No MCP (§2.1) | Exclusion rules + forbidden-pattern scan of repo and bundle + doctor | `tests/structural`, `doctor` |
| One core (§2.2) | `vikhyath` package; adapters are generated files | `tests/hosts` (no logic in adapter files) |
| Central install (§2.3) | `$VIKHYATH_HOME`; project gets only `.vikhyath/` + owned docs | isolation tests |
| Isolation (§2.4) | `ProjectContext` everywhere, path guard, keyed caches | doc 14 tests |
| No always-on (§2.5) | No daemons; dashboard idle exit; runtimes per command; hooks opt-in except L0 bootstrap | process checks in tests |
| Token efficiency (§2.6) | Entry-skill cap, L0–L3, budgets, cache, section loading, graph narrowing | P25 measured benchmarks vs doc 13 baseline |
| Local-first web verification (§23A) | `vikhyath/verify` ladder; browser FALLBACK class + event | `tests/webqa` |
| Explicit updates + rollback (§41–42) | doc 16 | `tests/update` |
| Provenance (§36) | Generated per file at build | `tests/bundle` |
