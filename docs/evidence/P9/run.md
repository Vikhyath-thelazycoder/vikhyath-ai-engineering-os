# P9 evidence — context engine (2026-10-04)

Interpreter: `Python 3.14.7` with PyYAML. `<scratch>` = session scratch `VIKHYATH_HOME` holding bundle `c98667e034f7` (registry rebuilt in P8). Token figures are **estimates (bytes ÷ 4)**; no tokenizer is used.

## Budgets (`config/budgets.yaml`, validated: 0 problems)
L0 ≤ 1,500 · L1 ≤ 2,000 per domain · L2 ≤ 8,000 per task (≤ 3 capabilities in full, ≤ 2 files each; 15 % of it reserved for headers and listings) · L3 ≤ 12,000 per explicit fetch · reference depth 1 · 12 code files · 2 project-doc sections · 3 semantic results. Each limit carries a `why`; the validator rejects a missing `why`, a non-positive value, or `L3.explicit_only != true`.

## Context index (built once per bundle)
`$VIKHYATH_HOME/cache/context-index/c98667e034f7.json`: 2,594 entries (232 skill, 325 doc, 473 reference, 951 data, 591 binary, 22 license), 2.53 MB, built in **0.40 s** on first use, reloaded in **10 ms**. Section choice uses only this index, so a cached file is never opened.

## L0 bootstrap (this repository)
306 est. tokens (1,224 B) of 1,500 with two state lines: OS identity + bundle id + host, project name/id/stage/branch, session, phase, plan pointer, and the 62-id capability index. A 100-line state flood is truncated to stay ≤ 1,500 (test).

## L1 + L2 per routed scenario, and the second identical load (same session)
Request text ranks entry files (BM25 over name/description/path) and sections (BM25 over titles).

| Scenario | Caps (L2 full / index) | L1 est. tok | L2 est. tok (content sent) | Files read (bytes) | 2nd run: hits · bytes read | 2nd run est. tok |
|---|---|---|---|---|---|---|
| s23a-login-flow | 2 / 0 | 321 | 6557 (6403) | 4 (28,551) | 4/4 · 0 B | 435 |
| s23a-mobile-overlap | 3 / 0 | 459 | 7062 (6277) | 9 (162,546) | 9/9 · 0 B | 941 |
| s23a-explicit-visual | 1 / 0 | 214 | 2889 (2770) | 3 (12,835) | 3/3 · 0 B | 362 |
| s23a-technical-seo | 3 / 1 | 475 | 5711 (5244) | 9 (36,354) | 9/9 · 0 B | 816 |
| s70-a-new-saas | 3 / 4 | 1116 | 7607 (6450) | 13 (82,611) | 13/13 · 0 B | 1446 |
| s70-b-existing-maps | 3 / 2 | 764 | 7860 (6766) | 11 (92,945) | 11/11 · 0 B | 1183 |
| s70-c-security-bug | 3 / 1 | 617 | 6963 (6285) | 8 (52,592) | 8/8 · 0 B | 891 |
| s70-d-design | 3 / 2 | 656 | 6922 (6074) | 11 (121,424) | 11/11 · 0 B | 1170 |
| s70-e-seo-audit | 3 / 1 | 475 | 4624 (4152) | 9 (30,894) | 9/9 · 0 B | 904 |
| s70-f-seo-fix | 3 / 3 | 842 | 7583 (6696) | 11 (62,344) | 11/11 · 0 B | 1273 |
| s70-g-ai-search | 3 / 0 | 335 | 4291 (4032) | 9 (17,385) | 9/9 · 0 B | 811 |
| s70-h-launch-video | 1 / 0 | 152 | 4132 (4009) | 3 (17,400) | 3/3 · 0 B | 329 |

Every L1 ≤ 2,000 per domain and every L2 ≤ 8,000. The second identical load in the same session is **all cache hits, 0 bytes read**, and sends only short `[cached]` markers (329–1,446 est. tokens instead of 2.9k–8.7k). “Files read (bytes)” are whole files read from disk; only the chosen sections are sent.

Two defects found and fixed while measuring:
- A second run reloaded 2 of 8 files: each file's budget share depended on what earlier, cached files had used, so the chosen sections (the cache key) shifted. Section choice is now planned before any cache check.
- AI-search (§70 G) loaded no L2 content: its BeyondSEO playbooks were classified L3 (`playbooks/`). A capability with no skill/doc files now uses its own markdown references at L2.

## L3 is explicit only
- `vikhyath context engineering/security --level 3` → exit 2: “level 3 is explicit only; pass --file”.
- L2 never loads `reference`, `data` or `license` files when a capability has skills/docs (test); it lists them for an explicit `--file` fetch.
- Explicit fetch of `files/addy/skills/security-and-hardening/SKILL.md`: 4,232 est. tokens (file ≈ 4,390) of the 12,000 cap; `--section <id>` loads single sections; an unknown section id is an error; a path outside the bundle index or a license file is refused.

## CLI
`vikhyath bootstrap [--host] [--session] [--json]`; `vikhyath context <ids…> | --route "<request>" [--level 1|2] [--request] [--file --section…] [--session] [--no-cache] [--json]`. `vikhyath context --route "Fix the payment webhook security." --session <id>`: 0.14–0.16 s wall per process (3 runs, warm index).

## Suite
`python -m unittest discover -s tests`: **114 tests OK** (18 new in `tests/context/`: budgets schema, sectioning, L0/L1/L2/L3 limits, explicit L3, identity normalisation, cache hit with zero rereads (instrumented `Path.read_text`), session/project keying, changed-file miss, index built once).
