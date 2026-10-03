# 13 — Token & Context Audit (Phase 3, spec §2.6, §16–17, §46–47, §92)

Token figures are **estimates: bytes ÷ 4** unless stated. No model tokenizer was used. Bytes are measured.

## 1. OLD MODEL baseline (measured on this machine)

What a Claude Code session loads **before any task** with v1.0.1 as documented (v1.0.1 + the ECC plugin it routes to):

| Surface | Count | Bytes | Est. tokens |
|---|---:|---:|---:|
| v1.0.1 skill name+description | 5 | 784 | 196 |
| v1.0.1 agent names (no descriptions) | 3 | 57 | 14 |
| **v1.0.1 subtotal** | | **841** | **≈210** |
| ECC 2.2.2 skill name+description | 292 | 95,218 | 23,804 |
| ECC 2.2.2 agent name+description | 68 | 15,325 | 3,831 |
| ECC 2.2.2 command name+description | 94 | 10,139 | 2,535 |
| **ECC subtotal** | | **120,682** | **≈30,170** |
| **Always-loaded total (v1.0.1 + ECC)** | | **121,523** | **≈30,380** |

Not counted above, also present: ECC `.mcp.json` Chrome DevTools tool schemas (the session exposes ~29 `mcp__plugin_ecc_chrome-devtools__*` tools), ECC SessionStart hook output ("load previous context"), and any per-turn hook output. Real always-on cost is therefore **higher** than 30.4k.

Measurement method: parse frontmatter of every `SKILL.md`/agent/command in `~/.claude/plugins/cache/{vikhyath-marketplace/.../1.0.1, ecc/ecc/2.2.2}`, sum `name + description` bytes. Reproduced by `vikhyath benchmark --baseline` (P4). P4 correction: description-less agents are counted by file stem (as the host displays them), not filename with `.md` (−9 bytes vs the P3 figure).

**When a task runs (old model):** routing happens in prose. The model chooses ECC skills by description and loads full bodies (ECC skills average 5.5 MB / 293 ≈ 19 KB ≈ 4.7k tokens each). gstack skills reached through v1.0.1 would cost up to 132 KB (≈33k tokens) for `design-review` alone, because the generated `SKILL.md` includes the preamble.

## 2. NEW MODEL design targets (to be measured in P25)

| Level (§16) | Contents | Target budget (est. tokens) | Rationale |
|---|---|---:|---|
| Always-loaded host surface | Entry skills' name+description (≤ 8 skills: `vikhyath` + one per domain) | **≤ 800** | v1.0.1 already spends ≈212 for 5 skills; 8 terse descriptions fit in 800. Replaces ≈30k when ECC is no longer required separately. |
| L0 bootstrap | OS identity, host, project id, session id, phase, compact state summary, capability index (ids + one-line purpose), plan pointer | **≤ 1,500** | 62 capability ids × ~15 tokens ≈ 930 + ~400 state/pointers. |
| L1 domain | Selected domain + subdomain summaries (capability cards) | **≤ 2,000** per domain | A card ≈ 150–250 tokens; ≤ 8 cards. |
| L2 capability | Specific files chosen by the router (sections, not whole files) | **≤ 8,000** per task by default; ≤ 3 capabilities fully loaded | Addy/ECC skills are 2–5k tokens each; section-level loading keeps 2–3 skills within budget. |
| L3 deep reference | Playbooks, design systems, stack packs, examples | On explicit need only; **≤ 12,000** per fetch | Large libraries (design systems, BeyondSEO playbooks) are fetched by id, never listed. |
| Code surface | Files returned by Graphify `affected`/`query` | ≤ 12 files default | The graph narrows first; full-repo dumps are forbidden (§23). |
| Project docs per turn | State + plan index; full docs by section on demand | ≤ 2 sections | §48–49. |

These are starting values. P9 makes them configurable, and P25 tests them against representative prompts (spec §47: "do not make arbitrary limits without testing").

## 3. Token hazards found in sources (must be handled at bundle build)

| Hazard | Size | Handling |
|---|---|---|
| gstack generated `SKILL.md` | up to 132 KB | Bundle from `.tmpl` + companions; PREAMBLE removed; sections loaded by `{{SECTION_INDEX}}` manifest |
| Taste `taste-skill` | 87 KB | Split by `##` sections; L1 card = brief inference + dials; L2 = selected sections; §9 AI Tells as a separate checklist file |
| OpenDesign design systems | 154 systems, 38 MB source | Index (name, tags, palette summary) at L3; one system fetched by id |
| ECC stack packs | 252 files | Activated only for the detected stack (language/framework detection from project files) |
| BeyondSEO playbooks | 134 files | Per-subdomain loading (technical audit never loads backlink playbooks, §28.4) |
| `engineering/planning` on disk | ≈171k tokens across 43 files | Lifecycle stage picks one workflow (intake vs spec vs plan review), not all |

## 4. Cache design inputs (§17)

- Graphify already keys its AST cache by SHA-256 content hash. The OS context cache uses the same principle: `(project_id, file path, sha256) → loaded-section ids`.
- Routing decisions are cached per `(project_id, normalized request intent, state hash)`.
- A file is re-read only when its hash changes. The plan is re-sent only when the plan-index hash changes.
- REFERENCE inputs: ECC `context-budget`, `content-hash-cache-pattern`, `strategic-compact`, `token-budget-advisor`, `iterative-retrieval`; Addy `context-engineering`.

## 5. Benchmark protocol (P25, spec §92)

For each representative prompt (scenarios A–I in spec §70 plus the §23A web-QA examples), record for OLD and NEW: files loaded, bytes, est. tokens, capabilities activated, cache reuse, code files loaded, project docs loaded, time to route. OLD is measured by replaying v1.0.1 routing prose plus the ECC skills its description-matching would select (methodology recorded with results). The goal is **minimum sufficient context**, not the smallest number.
