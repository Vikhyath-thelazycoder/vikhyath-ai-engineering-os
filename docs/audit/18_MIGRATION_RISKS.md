# 18 — Migration Risks (Phase 3)

| ID | Risk | Likelihood | Impact | Mitigation | Phase |
|---|---|---|---|---|---|
| MR-01 | v1.0.1 users rely on skill names `vikhyath-routing/-engineering/-production/-security/-review` | High | Medium | Keep all five names as thin entry skills that call the core router (spec §69); document the mapping | P19, P26 |
| MR-02 | **Double context**: a user keeps the standalone ECC plugin installed next to v2 → ≈30k always-loaded tokens remain (doc 13) | High | High | `vikhyath doctor` detects separately installed upstream plugins (ECC, Ponytail, gstack, …) and warns with the measured cost; the migration guide recommends removing them once v2 covers them | P25, P26 |
| MR-03 | Standalone ECC hooks (GateGuard, continuous-learning) keep running and interfere with OS behavior | High | Medium | Same doctor check; document `ECC_DISABLED_HOOKS` / uninstall | P25, P26 |
| MR-04 | Existing tests encode v1.0.1 tenets (hard-coded version, no-vendor) | Certain | Low | De-hardcode the version in P4; replace no-vendor with bundle-integrity in P6 (D-001) | P4, P6 |
| MR-05 | Deterministic router misroutes natural-language requests | Medium | High | Table-driven scenario tests (§70 A–I, §23A.14); explicit `--capability` override; BM25 fallback over capability cards; CAPABILITIES_SELECTED events for tuning | P8 |
| MR-06 | Adapted upstream text still carries host-specific or self-referential instructions (SEC-16) | Medium | Medium | Transform pipeline strips known directives (preambles, install steps, MCP calls); structural test scans the bundle for forbidden patterns (`mcp__`, `npx … mcp`, `~/.claude/skills/gstack`, telemetry endpoints) | P6 |
| MR-07 | Repo/clone size if the bundle (50.7 MB incl. 16 MB MP3s) is committed; each host's marketplace clone duplicates it | Depends on Q-1 | Medium | Q-1 recommendation: build the bundle centrally at install from pinned sources, verified by recorded blob hashes | P6 |
| MR-08 | An upstream repo or commit becomes unavailable → bundle cannot be rebuilt | Low | High | Keep the last known-good bundle (rollback); optional release tarball of the bundle per OS version | P24 |
| MR-09 | Graphify tree-sitter wheels unavailable on a platform / Python version | Low | Medium | Failure handling per §74 ("graph-based analysis unavailable; limited structural analysis used"); doctor reports it | P12 |
| MR-10 | Browser runtime is heavy (557 MB measured) | Certain if installed | Low | Never installed by default; explicit `vikhyath runtime install playwright`; FALLBACK class only | P15 |
| MR-11 | Full `/brag` depends on external Hyperframes skills + `npx` (G-2, SEC-13) | Certain | Low | Route launch videos to `/brag-slim` by default; full `/brag` enabled only when Hyperframes is detected and pinned | P17 |
| MR-12 | Codex/Cursor/Antigravity not installed here → adapters cannot be runtime-verified | Certain | Medium | Report FILES_PRESENT vs NOT VERIFIED honestly (§34); Q-3 asks the user for host access | P20–P22 |
| MR-13 | Concurrent sessions on the same project corrupt `state.yaml` | Medium | High | File locks + atomic rename + tests (doc 14) | P10–P11 |
| MR-14 | Secrets leak into events/state/dashboard | Low | High | Redactor on every write path + tests with planted secrets | P18 |
| MR-15 | Pinned HEADs include unreleased upstream changes | Medium | Low | All four executable runtimes pass their own suites at these pins; text-only sources carry no runtime risk; updates go through P24 gates | P24 |
| MR-16 | Python floor ≥3.10 vs older system Pythons | Low | Medium | Doctor checks the version; the installer creates its own venv | P4 |
