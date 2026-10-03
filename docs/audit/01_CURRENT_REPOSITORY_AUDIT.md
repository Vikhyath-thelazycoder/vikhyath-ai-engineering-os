# 01 — Current Repository Audit (Phase 0)

| Field | Value |
|---|---|
| Audited revision | `d77834e` (main, v1.0.1) |
| Audit branch | `feat/v2-os-transformation` |
| Date | 2026-10-03 |
| Tracked files | 58 (128,124 bytes) — per-file hashes in [evidence/phase0-file-inventory.tsv](evidence/phase0-file-inventory.tsv) |
| Uncommitted at audit start | `.claude-plugin/marketplace.json` (+`owner` block). User-owned; left uncommitted, not overwritten. |

## 1. Baseline match

The checkout matches the expected v1.0.1 baseline: `VERSION`, `plugin.json`, `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json` and both marketplace files all declare `1.0.1`. The only deviation is the uncommitted `owner` block noted above.

## 2. What v1.0.1 actually is

v1.0.1 is **declarative configuration plus prompt files**. There is no executable runtime: no Python package, no CLI, no router code, and no state store.

| Layer | Files | What it really does (evidence) |
|---|---|---|
| Host manifests | `plugin.json`, `.claude-plugin/{plugin,marketplace}.json`, `.codex-plugin/plugin.json`, `.agents/plugins/marketplace.json` | Packaging metadata only. Claude Code discovers `skills/` and `agents/` by convention; Codex reads `"skills": "./skills/"`. |
| Antigravity adapter | `.agents/skills/vikhyath-os/SKILL.md` (1,288 B) | Pointer to `skills/vikhyath-routing/SKILL.md` plus a quick-reference list. |
| Skills | `skills/vikhyath-{routing,engineering,production,security,review}/SKILL.md` (8,943 B total) | Prose instructions telling the model which *upstream repo name* to "route to". |
| Agents | `agents/{engineering-architect,production-reviewer,security-reviewer}.md` (2,812 B) | Prose role cards. **No YAML frontmatter** (all three start with `# ...`), so Claude Code lists them with the generic description "Agent from vikhyath-ai-engineering-os plugin". |
| Workflows | `workflows/{feature,bugfix,refactor,release,security-review}.md` (4,269 B) | Step lists naming upstream repos per step. Not referenced by any manifest, skill or script. |
| Config | `config/capabilities.yaml`, `routing.yaml`, `priorities.yaml` (13,354 B) | Registry, keyword routing and priorities. **Consumed only by tests and `scripts/validate`/`doctor`** (see §3). |
| Integration metadata | `integrations/*.yaml` (9 files, 6,848 B) | Per-upstream source/ref/install hints. Duplicates fields in `config/capabilities.yaml`. |
| Scripts | `scripts/{doctor,validate,benchmark}` (bash + inline Python, 21,460 B) | Structural checks. `benchmark` prints **hard-coded** tables; it measures nothing. |
| Tests | `tests/**/test_*.py` (20 tests, 11,808 B) | Assert manifest fields, YAML shape, SHA format, no-MCP and no-vendor. |
| CI | `.github/workflows/ci.yml` | Runs unittest, doctor, validate, benchmark, a no-MCP grep and a no-vendor check on Python 3.11. |
| Docs/governance | README (579 lines), AGENTS.md, CLAUDE.md, CHANGELOG, CONTRIBUTING, SECURITY, CODE_OF_CONDUCT, `.github` templates | Public docs and policy. |

## 3. Current routing (traced)

```
grep for routing.yaml|capabilities.yaml|priorities.yaml consumers (excluding .md):
  tests/security/test_security.py:28   tests/routing/test_routing.py:9-10
  scripts/validate:128,158,192          scripts/doctor:191
```

**Finding R-1:** no component executes routing. `routing.yaml` signals such as `"implement"` or `"UI"` are never matched against a request by code. The model receives routing only as prose in `skills/vikhyath-routing/SKILL.md`, and the YAML is only validated for shape. Routing is therefore non-deterministic and unmeasurable.

**Finding R-2:** routing targets are **upstream repository names** (`ecc`, `addy`, `gstack`, …), not domains or capabilities. This is exactly the repository-first model spec §5 prohibits.

**Finding R-3:** "activating" a capability presumes the upstream is separately installed in the host. Example: `skills/vikhyath-engineering/SKILL.md` says "Before routing to ECC, verify it is installed". Nothing in v1.0.1 checks this. Graphify, OpenDesign and others are recorded as `supported: false` on every host.

## 4. Current capability model

- 9 capabilities keyed by repo, each with `source, role, priority, ref (40-hex), license, activation tags, hosts.{codex,antigravity,claude}, provides`.
- Two parallel registries hold the same facts: `config/capabilities.yaml` and `integrations/*.yaml`. This violates the single-source-of-truth rule in spec §13 and §68.
- `priorities.yaml` adds a third copy of the priority numbers (`capability_priorities`).
- No domain, subdomain, context level, token cost, runtime type, browser requirement or verification metadata exists.

## 5. Current host support (claims vs. evidence)

| Host | Packaging present | Claimed in README | Verifiable in this audit |
|---|---|---|---|
| Claude Code | `.claude-plugin/plugin.json` + marketplace | "Packaging supported, marketplace verified" | Partially. This session runs with the plugin loaded: its 5 skills and 3 agents appear in the host's skill and agent lists. Agents lack descriptions (§2). |
| Codex | `.codex-plugin/plugin.json` + `.agents/plugins/marketplace.json` | "Packaging supported, marketplace verified" | UNKNOWN. No Codex CLI here; verify in the Codex adapter phase. |
| Antigravity | `.agents/skills/vikhyath-os/SKILL.md` + root `plugin.json` | **"Runtime Tested"**, and `scripts/benchmark` prints "✅ Verified" | UNKNOWN. No evidence artifact backs the claim. The spec §96 claim rule applies, so it's treated as unverified. |
| Cursor | **None** | Not mentioned | Absent. Required by spec §2.2. |

## 6. Baseline checks (executed 2026-10-03)

| Check | System python3 3.14.7 (no PyYAML) | Isolated venv + PyYAML |
|---|---|---|
| `python -m unittest discover -s tests` | FAIL: 9 run, 3 import errors (`No module named 'yaml'`) | **PASS: 20/20** |
| `scripts/doctor` | exit 1 | **50 passed, 0 failed** |
| `scripts/validate` | exit 1 | **27 passed, 0 failed** |

**Finding E-1:** the repo declares no dependency manifest (no `requirements.txt` or `pyproject.toml`). PyYAML is installed only inside CI (`ci.yml`), so a fresh machine fails every check. v2 needs a declared core runtime.

## 7. MCP status

`grep -rli mcp` (excluding `.git` and `.staging`) matches 16 files. **Every match is a prohibition, check or documentation statement.** No `mcpServers`, `.mcp.json`, MCP dependency or MCP client exists. MCP checks only cover `.codex-plugin/`, `.claude-plugin/`, `plugin.json`, `config/` and the test walk over JSON/YAML.

Environment observation (not repo content): the separately installed ECC plugin in this host exposes `mcp__plugin_ecc_chrome-devtools__*` tools. **ECC ships MCP configuration upstream**, so Phase 1 must locate it and exclude it from extraction (spec §2.1).

## 8. free-for-dev

`grep -rni "free-for-dev\|free_for_dev"` → exit 1 (no matches). **No references to remove.** Nothing was fetched.

## 9. Architectural tenets v1.0.1 enforces that conflict with the v2 spec

| v1.0.1 tenet (where enforced) | v2 spec requirement | Conflict |
|---|---|---|
| "Zero Vendoring: upstream code is never copied" (README §3, CONTRIBUTING:14, CI "Verify NO Vendor Copies", `test_no_vendor_directories`, doctor/validate) | Local bundle with COPY/ADAPT/WRAP/PRESERVE extraction and offline use (§35, §38, §45) | **Direct.** Resolved by decision D-001. |
| "GitHub is the Source of Truth" (README §3) | Normal runtime uses the LOCAL BUNDLE, not remote (§35, §44) | Direct. Resolved by D-001. |
| Host capability = "install the upstream plugin too" (integrations/*.yaml `install:`) | One core + host adapters; user experiences one system (§1, §2.2) | Direct. |
| Routing by repo name (routing.yaml) | Domain-first capability routing (§5, §14) | Direct. |
| Ponytail default OFF, explicit-only (priorities.yaml, `test_simplicity_review_routing`) | Ponytail = simplicity discipline folded into completion (§4.7, §25) | Partial. v2 can keep "never auto-run a full simplicity review" while letting simplicity *principles* inform completion. Decided in Phase 2. |

## 10. Token/context baseline (OLD MODEL, for spec §92 comparison)

Byte counts are measured. Tokens are **estimated** at bytes ÷ 4 and labeled as estimates.

| Surface | Bytes | Est. tokens | When loaded |
|---|---|---|---|
| Skill frontmatter (6 SKILL.md incl. Antigravity) | 1,027 | ~257 | Always (host skill index) |
| Agent cards (3) | 2,812 | ~703 | Agent descriptions are absent, so the host shows a generic label. Full body is loaded on invocation. |
| `vikhyath-routing` skill body | 2,580 | ~645 | On activation |
| All 5 skill bodies | 8,943 | ~2,236 | Worst case |
| Repo `CLAUDE.md` / `AGENTS.md` | see inventory | — | Only when the OS repo itself is the workspace |

v1.0.1's context cost is small **because it delegates everything to separately installed upstream plugins.** Those plugins' own always-loaded surfaces aren't counted. The ECC plugin alone contributes hundreds of skill and command descriptions to this session's host index. The real old-model cost is therefore "v1.0.1 + every upstream plugin the user installed", and it will be measured in the Phase 3 token audit.

## 11. Summary of findings

| ID | Finding | Severity |
|---|---|---|
| R-1 | Routing is prose only; YAML is never executed | High |
| R-2 | Repository-first capability model | High |
| R-3 | Capabilities assume separately installed upstream plugins; nothing verifies them | High |
| C-1 | Three overlapping registries (capabilities.yaml, integrations/*.yaml, priorities.yaml) | Medium |
| H-1 | No Cursor adapter | High |
| H-2 | Antigravity "Runtime Tested" claim has no evidence | Medium |
| H-3 | Agent files lack frontmatter, so the host shows no description | Low |
| E-1 | No declared Python dependency; checks fail outside CI | Medium |
| B-1 | `scripts/benchmark` prints hard-coded results presented as analysis | Medium |
| T-1 | Zero-vendoring tenet conflicts with the v2 bundle model | Critical (decision) |
| S-1 | No project state, multi-project isolation, observability, dashboard, update or rollback | High (gap) |
| P-1 | All v1.0.1 upstream pins are stale (up to 2,037 commits behind) | Medium |
| L-1 | Karpathy upstream ships no LICENSE text (MIT declared in metadata) | Informational (D-002: non-blocking) |
