# 00 — Executive Summary

*Updated at the end of each audit phase. Current through **P0** (2026-10-03).*

## Where v1.0.1 stands

v1.0.1 (58 files, 128 KB) is a set of host manifests, five prose skills, three agent cards and YAML config. **It has no executable runtime.** Its routing YAML is never executed (R-1), its capabilities are upstream repository names (R-2), and every capability assumes the user has separately installed that upstream plugin (R-3). Structural checks pass (20/20 tests, doctor 50/0, validate 27/0), but only when PyYAML happens to be installed (E-1).

## What blocks the v2 spec

1. **The zero-vendoring tenet** (T-1) contradicts the v2 local-bundle model. Retired by **D-001**.
2. **Absent core:** no router, context engine, state, isolation, observability, dashboard, update or rollback (S-1).
3. **Missing hosts and sources:** no Cursor adapter (H-1). Five spec sources were never integrated: Taste, UI/UX Pro Max, Brag, Agent Beacon and BeyondSEO.
4. **Unverified claims:** "Antigravity Runtime Tested" (H-2) and a hard-coded benchmark (B-1).

## Already in good shape

- No MCP anywhere in the repo.
- No free-for-dev references.
- Manifests are valid.
- The policy of never copying the plugin into projects already exists (README).

## Inputs ready for P1

All 14 upstream repositories are staged as complete, blobless snapshots with recorded HEAD SHAs ([evidence/upstream-staging-snapshot.yaml](evidence/upstream-staging-snapshot.yaml)). All nine v1.0.1 pins exist in upstream history and are 0–2,037 commits behind HEAD.

## Decisions so far

D-001 local bundle · D-002 licensing never blocks (user) · D-003 staging location · D-004 28-phase plan. See [21_AUDIT_DECISIONS.md](21_AUDIT_DECISIONS.md) and [../plan/IMPLEMENTATION_PLAN.md](../plan/IMPLEMENTATION_PLAN.md).
