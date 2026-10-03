# 08 — Duplication Analysis (Phase 2, spec §37)

## 1. Exact duplicates inside each upstream (not bundled twice)

| Repo | Byte-identical groups | Cause | Handling |
|---|---:|---|---|
| OpenDesign | 495 | `DESIGN-<lang>.md` translations; shared token files across design systems | Translations EXCLUDE (TRANSLATION); shared token files stored once (see §3) |
| ECC | 258 | Host ports (`.kiro/`, `.cursor/`, `.agents/`, `pi/`, `.opencode/` …) | HOST_PORT EXCLUDE; canonical `skills/`, `agents/`, `rules/` only |
| UI/UX Pro Max | 192 | `.claude/skills/*` vs `cli/assets/skills/*` | `cli/` EXCLUDE (INSTALLER) |
| Graphify | 31 | Per-host skill copies | One canonical (`graphify/skills/claude/`) ADAPT |
| gstack / Beacon / Brag / Addy / Ponytail | 16 / 16 / 13 / 6 / 1 | Fixtures, host copies, docs | Covered by EXCLUDE rules |

## 2. Cross-repo duplicates and near-duplicates

| Content | Repos | Finding | Canonical choice |
|---|---|---|---|
| Taste skills (taste-skill, soft, minimalist, brutalist, redesign, stitch, brandkit, output, image-to-code, imagegen-*) | Taste, OpenDesign `skills/` | Same names; **only 2 files byte-identical**, so OpenDesign carries diverged copies | **Taste** (upstream origin); OpenDesign copies EXCLUDE (DUPLICATE) |
| UI/UX Pro Max skill | UI/UX Pro Max, OpenDesign `skills/ui-ux-pro-max` | Vendored copy | **UI/UX Pro Max** engine + skill |
| SEO skill | ECC `skills/seo`, `agents/seo-specialist`, BeyondSEO | ECC's is a 4 KB prompt; BeyondSEO is a full runtime + 134 playbooks | **BeyondSEO**; ECC SEO EXCLUDE (SUPERSEDED) |
| Code review | Addy `code-review-and-quality`, gstack `review`, ECC `agents/code-reviewer` + language reviewers, Agency `code-reviewer` | Overlapping intent, **different content** (multi-axis vs pre-landing checklist vs per-language) | Keep all; the ADAPT step merges them into one `engineering/review` capability with layered sections (Addy axes → gstack checklist/specialists → stack-pack reviewer) |
| Security | Addy `security-and-hardening`, gstack `cso`, ECC `security-review`, Agency security roles | Overlapping intent, different depth | Keep; ordered L2 (Addy workflow) → L3 (CSO phases, OWASP patterns) |
| Simplicity | Ponytail, Addy `code-simplification`, ECC `code-simplifier`, gstack `deslop-shared-libs`, Agency `minimal-change-engineer` | Complementary | Keep; Ponytail is the rule set, others are procedures |
| Completion | Unlazy, Taste `output-skill`, Addy `definition-of-done`, ECC `verification-loop`/`delivery-gate` | Complementary; Unlazy is the only executable gate system | Unlazy is the engine; others are guidance |
| Destructive-command guards | gstack `careful`/`guard`/`freeze`, ECC `safety-guard` | Overlapping | Keep both as opt-in; P3 picks one implementation |
| Planning | Addy spec/planning/interview, gstack office-hours/spec/plan-*-review, ECC blueprint/intent-driven/product-lens, Agency product roles | Overlapping phases | Keep; mapped to lifecycle stages in P3 (intake → spec → plan → plan review) |

Similar-but-different files are kept and the reason is recorded here (spec §37: no unsafe deduplication).

## 3. Exact duplicates inside the selected bundle

Computed from git blob SHA-1 over all 2,645 bundled files:

- **37 groups, 53 redundant copies, 0.99 MB.**
- Mostly OpenDesign `design-systems/*/design-tokens.json` shared by several systems (groups of 2–7).
- Also: the BeyondSEO logo in two places; ECC `taste-*` script copies (now excluded).

**Rule for P6:** the bundle stores content once, addressed by its hash. Each capability mapping references the canonical blob, and provenance records every source path that maps to it.
