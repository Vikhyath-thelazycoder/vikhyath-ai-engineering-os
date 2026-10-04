# P10 evidence — project state, plan index, decisions (2026-10-04)

Interpreter: `Python 3.14.7`, PyYAML 6.0.3 with libyaml. Fixture: a scratch "travel" project (git repo, `package.json` with react/next/stripe, `src/bookings/api.ts`), `vikhyath project init --docs`, then phases P2 (COMPLETED, accounts), P3 (IN_PROGRESS, Booking System), P4 (PLANNED, Payments) added to the generated plan.

## Init
```
initialised travel (226174c3d60f42dc) as existing project; stack: node, react, next, stripe
  + docs/ARCHITECTURE.md … docs/TRD.md (9 templates, never overwriting)
```
Stage is detected (manifest/source files → existing); stack from manifests only.

## Acceptance 1 — state read ≪ full docs (bytes measured)
| What the OS reads every turn | Bytes |
|---|---|
| `.vikhyath/state.yaml` | 306 |
| `.vikhyath/plan-index.yaml` | 2,047 |
| L0 state lines (what bootstrap actually sends) | 158 |
| **vs.** `docs/*.md` (9 templates, still mostly empty) | 9,107 |
| one phase on demand (`vikhyath plan show P3`) | 782 |

On templates alone the per-turn read is 4× smaller than the documents; the test fills seven documents with realistic prose and asserts state + index < 1/5 of the docs (`tests/project/test_project.py::TestStateCost`). L0 carries 158 B of state:
```
existing project · stack node, react, next, stripe
phase P3 Booking System (IN_PROGRESS) · active tasks: T-3.1
phases: 1 COMPLETED, 1 IN_PROGRESS, 2 PLANNED
```
Index fast path (one `stat`, no plan read): **0.21 ms**; rebuild after a plan edit: 0.41 ms; `state.yaml` read: 0.05 ms. (Before switching to libyaml's C loader the fast path was 1.5 ms, slower than a rebuild; fixed.)

## Acceptance 2 — "Add Google Maps navigation to bookings." (spec §21)
`vikhyath plan locate` ranks P3 Booking System first (score 4; P4 Payments 2). `vikhyath plan reconcile "Add Google Maps navigation to bookings."`:
- route: NEW_FEATURE → engineering/security, engineering/implementation, engineering/backend, testing/strategy, codebase/impact-analysis (+ repository-understanding, stack-packs);
- task **T-3.3** appended to the existing P3 table, PLANNED, with security ("security capability routed") and testing ("NEW_FEATURE requires tests") impact; change-history row `T-3.3 added to P3 Booking System`;
- §55 impact: all 12 fields (affected phase P3, files `src/bookings/**`, docs to update FEATURES.md + SYSTEM_WORKFLOW.md, rollback "revert the task's commits");
- `ls docs` before/after: identical; **no new file anywhere in the project** (test compares the full file list); `## P3 ·` appears once.

## Other behaviour (tests)
- §49 index fields per phase; current phase = first active; `plan show P3` returns only that section.
- §25 transitions: PLANNED → COMPLETED refused; DONE refused (not a §25 state); VERIFIED/COMPLETED need `--evidence` and are recorded in `verification.yaml` + `state.verification.last`.
- Adding a task to a COMPLETED phase reopens it (IN_PROGRESS) with a history note; an unmatched request returns `needs_phase`, and `--new-phase` appends P5 to the same plan.
- Decisions (§50–52): D-001… ids, `supersedes` marks the old one SUPERSEDED; `relevant()` returns security decisions only with security capabilities and design decisions only with design ones; `docs/PROJECT_DECISIONS.md` table re-rendered between markers; `vikhyath context engineering/security --level 1` appends “D-001 [security] Keys: Server-side”.
- Questions (§53): for “Build me a travel booking SaaS with AI trip planning” on a new project → only BLOCKING (product-goal, database, auth); frontend inferred (react), payments inferred (stripe); analytics/ai deferred; after answering, IMPORTANT ones (incl. ai) follow; “Fix the typo in the footer” on an existing project → no questions.
- `vikhyath bootstrap` shows phase, plan pointer `docs/IMPLEMENTATION_PLAN.md#P3` and records the session under `$VIKHYATH_HOME/projects/<id>/sessions/<sid>/session.yaml`. `vikhyath route` takes stage/stack/phase from state (else detection).
- `vikhyath project relink --from <old id>` after moving the repo: data dir moved to the new id, alias recorded, state id updated; refuses to merge into a non-empty data dir.
- Templates: all nine §20 documents carry their required headings; the plan template parses.

## Suite
`python -m unittest discover -s tests`: **130 tests OK** (16 new in `tests/project/`). `vikhyath doctor` 45/0; `vikhyath validate --no-unittest` 19/0.
