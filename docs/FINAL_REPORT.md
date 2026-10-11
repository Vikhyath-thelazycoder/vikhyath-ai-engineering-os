# Agylite v2.0.0 — final report

Branch `feat/v2-os-transformation`, 2026-10-11. The v1.0.1 plugin ("Vikhyath AI Engineering OS", routing notes that
assumed separately installed upstream plugins) was rebuilt as **Agylite**, a working local engineering OS, over eight
milestones (M0–M7, phases P0–P27, decisions D-001…D-046). Every phase has a section in
`docs/plan/IMPLEMENTATION_PLAN.md` and evidence under `docs/evidence/`.

## What exists now

| Area | Delivered | Proof |
|---|---|---|
| Core & CLI | `agylite` package and CLI (`vikhyath` alias), central install `scripts/install` | tests/unit, doctor |
| Supply | 15 pinned upstreams → ~2,580 bundled files (of ~24,600), provenance per file, notices, reproducible bundle ids | bundle `07cd36edb5d9` known-good, `bundle verify` intact |
| Registry | 63 capabilities in 9 domains, one authored source, generated registry | `registry check` valid |
| Routing | deterministic rules + tags + BM25 fallback, impact step, lifecycle | 22/22 spec scenarios, p95 0.34 ms |
| Context | L0–L3 with budgets, sections, session cache | L0 ~1.2 KB; second load 0 bytes read |
| Project | state, one living plan, reconciliation, decisions, lifecycle, completion states | P10/P13 tests, end-to-end test |
| Isolation | path guard, locks, atomic writes | 0 cross-project reads in the interleaved test |
| Codebase | Graphify runtime, `codebase affected` with related tests, 12-file surface, structural fallback | P12 tests incl. real runtime |
| Engineering | lifecycle, gstack/MCP/browser adaptation debts cleared, Unlazy gates | bundle `debts {}`, `unresolved_placeholders {}` |
| Design | UI/UX Pro Max engine, design-token checks | P14 tests |
| Testing | `verify`: detection, impact selection, run, rerun, diagnosis, evidence | payment-webhook scenario, P15 tests |
| SEO | isolated BeyondSEO, evidence labels, live-site authorization | upstream suite 340 passed (9 need the browser extra); P16 tests |
| Media | Brag plan (brag-slim default), music cues | P17 tests |
| Observability | redacted event log, Beacon risk rules | 77 rules, all embedded tests pass |
| Hosts | Claude Code, Codex, Cursor, Antigravity from one entry-skill set | P19–P22 tests |
| Dashboard | Agent Office (pixel office of agents, live from events) | P23 tests |
| Update | `update`/`rollback`/`gc`, dangling-reference check | P24 tests, real rollback |
| Diagnostics | doctor host/supply checks (redacted), measured benchmarks | `docs/benchmarks/RESULTS.md` |
| Docs | 17 architecture docs, migration guide, README/CHANGELOG | `docs/architecture/`, `docs/migration/` |

## Measured results

- Per turn: **~915** est. tokens (Agylite) vs **~31,800** for ECC, Open Design and UI/UX Pro Max installed directly.
- 22 spec tasks: **~176,000** vs **~1,020,000** est. tokens (**83 % less**). Tokens are bytes ÷ 4 estimates; OLD
  excludes MCP tool schemas and hook output, so the saving is a lower bound.
- Routing 22/22, p50 0.23 ms / p95 0.34 ms; L1+L2 context assembly p50 12 ms.
- Tests: **246 pass** (3 opt-in real-runtime Graphify tests also pass against the bundle). Doctor 50/0 (11 warnings
  about separately installed plugins and their MCP servers on this machine); validate 23/0.
- **End-to-end offline test** (`tests/integration/test_end_to_end.py`): init → bootstrap → route → context → codebase
  affected → verify → plan VERIFIED with evidence → Agent Office states → events, with every non-loopback network
  connection failing the test.

## Acceptance checklist (doc 22 §9 and the spec themes)

- No MCP used or configured ✔ · central plugin, no project-local OS ✔ · capability-based, progressive loading ✔ ·
  isolation ✔ · no duplicate design or verification stacks ✔ · Graphify = codebase intelligence, Beacon =
  observability ✔ · dashboard separate and on demand ✔.
- Verification: local test-first default ✔ · Chrome DevTools, screenshot verification, visual browser QA disabled ✔ ·
  evidence machine-readable and recorded in project state ✔ (P15) · diagnostics detect violations and host MCP ✔ (P25).
- Appllama: audited, only unique native-mobile rules merged (3 files + LICENSE), no MCP/usage/simulator loop ✔.
- Provenance and exact SHAs for every bundled file ✔ · updates explicit and reversible ✔ · docs describe the system
  as built ✔ (P26).

## Recorded limitations (not hidden)

1. **Host runtime verification:** all four hosts are FILES_PRESENT here. Claude Code has the old v1.0.1 plugin
   installed, not `agylite`; Codex, Cursor and Antigravity are not installed on this machine (D-024). RUNTIME_VERIFIED
   requires installing Agylite in the host and one session start.
2. **Network-dependent checks** could not run because this machine's DNS does not resolve: a live public SEO crawl
   (the success path was verified offline with saved captures) and 6 Graphify upstream tests that fetch example.com.
3. **Optional extras not installed:** BeyondSEO browser extra (9 upstream tests), Graphify language grammars and LLM
   backends (60 upstream tests). They stay opt-in by design.
4. The `agylite update` network fetch path is exercised only with local trees in tests.
5. The GitHub repository keeps the name `vikhyath-ai-engineering-os` until its owner renames it.

## Release steps (need the owner's go-ahead)

1. Merge `feat/v2-os-transformation` into `main` and push; tag `v2.0.0`.
2. `scripts/install` (central install and bundle), then in Claude Code: update the marketplace and install
   `agylite@agylite-marketplace` (uninstall the v1 `vikhyath-ai-engineering-os` plugin).
3. Start a session and run `agylite adapters status --host claude-code` → RUNTIME_VERIFIED.
4. Optionally remove separately installed ECC / Open Design / UI/UX Pro Max (`agylite doctor` lists their cost).
