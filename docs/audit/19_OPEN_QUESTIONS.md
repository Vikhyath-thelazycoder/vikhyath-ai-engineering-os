# 19 — Open Questions (Phase 3, spec §53 priority order)

BLOCKING questions must be answered before the phase they block. Others have a stated default that the plan uses unless the user decides otherwise.

| ID | Priority | Question | Options | Recommendation / default | Blocks |
|---|---|---|---|---|---|
| Q-1 | **BLOCKING (P6)** | How is the local capability bundle distributed? | **A.** Commit the built bundle (50.7 MB incl. 16 MB MP3s) into the plugin repo. **B.** Build it centrally at install time from the pinned upstreams, verified against the recorded blob hashes; offline afterwards. **C.** Commit text content; fetch heavy assets (Brag music, fonts) on first use. | **B**: the repo stays small; each host's marketplace clone does not duplicate 50 MB (spec §2.2/§2.3 spirit); the bundle is reproducible from pins; install is the one explicit network step (§44). Pair with an optional release tarball for offline installs (MR-08). | P6 (not P4/P5) |
| Q-2 | IMPORTANT | Where do project-owned artifacts live, and are they meant to be committed? | `.vikhyath/` (state/plan-index/decisions/verification) + human docs (PRD.md, TRD.md, …) in `docs/`; or everything under `.vikhyath/` | **Default:** `<project>/.vikhyath/` for compact state (committable; caches never in the project) and `<project>/docs/` for PRD/TRD/ARCHITECTURE/… on new projects; configurable per project | P10 |
| Q-3 | IMPORTANT | Can Codex CLI, Cursor and Antigravity (`agy`) be made available for runtime verification? | Install them on this machine / provide another machine / accept NOT VERIFIED | **Default:** build and schema-validate all four adapters; report INSTALLED/RUNTIME_VERIFIED as NOT VERIFIED where the host tool is absent | P20–P22 |
| Q-4 | OPTIONAL | Enable full `/brag` (Hyperframes via `npx`, network + browser) in addition to `/brag-slim`? | Yes, pinned / No | **Default:** `/brag-slim` only; full `/brag` behind explicit opt-in | P17 |
| Q-5 | OPTIONAL | Release version for the transformed OS | 2.0.0 / other | **Default:** 2.0.0 (breaking architecture change); no tag or release until the user says so (spec §97) | P27 |
| Q-6 | OPTIONAL | Commit the user's uncommitted `owner` block in `.claude-plugin/marketplace.json`? | Yes / No / later | **Default:** leave it uncommitted and untouched | — |
| Q-7 | OPTIONAL | Remove the standalone ECC plugin from Claude Code after v2 is installed (MR-02)? | Yes / keep both | **Default:** doctor warns; the user decides | P25 |

## Resolved during M1

| ID | Question | Resolution |
|---|---|---|
| — | Licensing gates | D-002: never blocking (user) |
| — | Reference-only vs real extraction | D-005: selective real extraction (user) |
| — | Interconnected skills | D-006: full dependency closure (user); 0 open gaps |
| — | Review cadence | D-007: 8 milestones (user) |
| — | BeyondSEO browser failures | All 9 caused by the missing optional extra; 250/250 OK with it |
| — | AgentShield | `security-scan` excluded (UNAUDITED_DEPENDENCY) |
