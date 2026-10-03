# 03 — Gap Analysis: v1.0.1 → v2 target (Phase 0)

Legend: **Absent** = nothing exists · **Partial** = something exists but doesn't meet the spec · **Conflict** = exists and contradicts the spec · **Met**

| # | Spec requirement | v1.0.1 state | Gap | Addressed in phase |
|---|---|---|---|---|
| 1 | No MCP (§2.1) | No MCP; checks limited to manifests/config | **Met**; checks must extend to the bundle (upstream ECC ships MCP) | P1, P6, P25 |
| 2 | One core + host adapters (§2.2, §33) | No core; 3 manifests + 1 Antigravity skill | Absent core; Cursor absent | P4, P19–P22 |
| 3 | Central install, nothing copied into projects (§2.3) | README already forbids copying the plugin into projects | Partial (policy only; no project-state model defines what *is* allowed) | P10 |
| 4 | Multi-project isolation (§2.4) | No state at all | Absent | P10, P11 |
| 5 | No always-on swarm/daemon/browser (§2.5) | No processes exist | Met trivially; must stay met as the dashboard and runtimes are added | P16, P23 |
| 6 | Token efficiency measured (§2.6, §46, §92) | `benchmark` prints hard-coded estimates | Conflict (B-1) | P3 baseline, P9, P25 |
| 7 | Complete pinned upstream snapshots audited (§3) | 9 pins, no audit artifacts; 5 sources missing (Taste, UI/UX Pro Max, Brag, Beacon, BeyondSEO) | Snapshots now staged (14/14); audit absent | P1 |
| 8 | Domain-first architecture (§5–12) | Repo-first | Conflict (R-2) | P2, P7 |
| 9 | Single capability registry with full metadata (§13) | 3 overlapping files, minimal fields | Conflict (C-1) | P7 |
| 10 | Deterministic routing algorithm (§14–15) | Prose only (R-1) | Absent | P8 |
| 11 | Context levels 0–3, budget, cache with hashes (§16–17, §47) | None | Absent | P9 |
| 12 | Compact project state, plan index, decision memory (§18, §49–52) | None | Absent | P10 |
| 13 | Project lifecycle: new vs. existing, requirements engine, change engine (§19, §53–56) | None | Absent | P10, P13 |
| 14 | Project doc templates PRD/TRD/… (§20) | None | Absent | P13 |
| 15 | Codebase intelligence (Graphify) (§4.8, §23) | Registry entry only; `supported: false` on all hosts | Absent integration | P12 |
| 16 | Unified design domain (§8, §26–27) | OpenDesign reference only | Absent; Taste & UI/UX Pro Max missing | P14 |
| 17 | Testing domain + local-first web verification (§9, §23A) | None | Absent | P15 |
| 18 | SEO domain + isolated BeyondSEO runtime (§10, §28) | None | Absent | P16 |
| 19 | Media domain (Brag) (§11, §29) | None | Absent | P17 |
| 20 | Observability events (§12, §30) | None | Absent | P18 |
| 21 | Vikhyath-owned dashboard + lifecycle (§31–32) | None | Absent | P23 |
| 22 | Local bundle, provenance, duplication control (§35–37) | Forbidden by v1.0.1 tenet | Conflict (T-1 → D-001) | P5, P6 |
| 23 | Licenses/notices preserved (§40) | `license:` field only | Partial; non-blocking per D-002 | P5 |
| 24 | Explicit update + rollback (§41–42) | `validate --online` only checks SHAs exist | Absent | P24 |
| 25 | Network/offline policy (§44–45) | Offline validation exists (structural) | Partial | P25 |
| 26 | Completion states & verification language (§25, §76) | None | Absent | P13 |
| 27 | Diagnostics doctor/validate/test/benchmark/update/rollback (§59) | doctor/validate/benchmark (bash) | Partial | P4, P25 |
| 28 | Declared core dependencies | PyYAML only in CI (E-1) | Absent | P4 |
| 29 | Security of third-party source (§43) | None | Absent | P1 |
| 30 | Final test matrix + report (§91, §95) | 20 structural tests | Partial | P27 |
