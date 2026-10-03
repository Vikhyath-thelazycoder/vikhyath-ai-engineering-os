# 00 — Executive Summary

*Current through **M1 (P0–P3)**, 2026-10-03. Status: READY_FOR_VERIFICATION (user review at the §64 gate).*

## Starting point (v1.0.1)

- **What it is:** 58 files of manifests, five prose skills, three agent cards and YAML. **No executable runtime.**
- **Routing never runs:** the YAML is only validated for shape (R-1).
- **Capabilities are upstream repo names** (R-2), and each assumes the user separately installed that upstream plugin (R-3).
- **Unverified claims:** "Antigravity Runtime Tested" (H-2: `agy`, its plugin dir and any Vikhyath files are absent on this machine) and a hard-coded benchmark (B-1).

## Measured cost of the old model

A Claude Code session with v1.0.1 plus the ECC plugin it routes to loads **≈30,380 estimated tokens** of skill, agent and command descriptions before any task:
- **v1.0.1:** ≈212.
- **ECC 2.2.2:** ≈30,170 (292 skills, 68 agents, 94 commands).
- **Not counted:** MCP tool schemas and hook output, which add more (doc 13).

## Upstream audit (14 repositories, 26,588 files)

| Finding | Detail |
|---|---|
| Pins | All 14 pinned to audited HEADs (D-008); per-file blob hashes for every file |
| MCP | Present in 7 repos; all separable; one documented exception (Graphify `mcp_ingest.py` parses MCP files as data, D-021) |
| Always-on behavior | ECC hooks (24, default on), Ponytail session hooks, gstack browser daemon + Supabase telemetry, Graphify git hooks, OpenDesign daemon, Beacon endpoint agent: all excluded |
| Executable runtimes verified | Unlazy 188/188 · UI/UX Pro Max 164/164 · Graphify install/update/query OK · BeyondSEO 250/250 (browser extra, 557 MB) |
| Token hazards | gstack generated skills up to 132 KB (template 13.7 KB); Taste 87 KB; OpenDesign libraries 38 MB each |

## Extraction result (selective real extraction + dependency closure)

- **Selected:** 2,644 files (50.7 MB): ADAPT 973, COPY 644, PRESERVE 1,027.
- **Left out:** REFERENCE 686 (staging only) and EXCLUDE 21,258, each with a reason code.
- **Closure:** 0 open gaps (37 accepted with reasons).
- **Domains:** 7 domains, 62 capabilities.
- **Single source of truth:** one machine-readable rules file drives both the audit matrix and the future bundler.

## Target architecture (doc 20)

**One core:** a Python package `vikhyath` with a single CLI, centrally installed in `$VIKHYATH_HOME`. Hosts get **thin adapters**: ≤10 entry skills (target ≤800 tokens) plus an L0 bootstrap (≤1.5k).

The core provides:
- deterministic routing;
- L0–L3 context with budgets and a hash cache;
- per-project state split into project-owned `.vikhyath/` and central regenerable data;
- structural isolation;
- JSONL events with redaction;
- a content-addressed, provenance-tracked bundle with versioned rollback;
- isolated on-demand runtimes;
- a local-first verification ladder (browser = fallback);
- an on-demand localhost dashboard.

**No MCP, no daemons.**

## Decisions

D-001 … D-022 in [21_AUDIT_DECISIONS.md](21_AUDIT_DECISIONS.md). User decisions: D-002 (licensing never blocks), D-005 (selective real extraction), D-006 (dependency closure), D-007 (8 milestones).

## Open before implementation

| ID | Priority | Question |
|---|---|---|
| Q-1 | **BLOCKING for P6 only** | How to distribute the bundle (recommended: build at install from pins, hash-verified) |
| Q-2 | Important (default set) | Project artifact locations |
| Q-3 | Important (default set) | Access to Codex / Cursor / `agy` for host runtime verification |

Details: [19_OPEN_QUESTIONS.md](19_OPEN_QUESTIONS.md). Plan: [../plan/IMPLEMENTATION_PLAN.md](../plan/IMPLEMENTATION_PLAN.md) · file-level tasks: [../plan/FILE_LEVEL_PLAN.md](../plan/FILE_LEVEL_PLAN.md).
