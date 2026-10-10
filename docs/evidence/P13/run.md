# P13 evidence — engineering domain (2026-10-10)

Interpreter `Python 3.14.7`, Node `v22.14.0`, scratch `VIKHYATH_HOME`.

## Bundle
`vikhyath bundle build --self-test`: **`2d1356913230` known-good, 2,583 files, 0 errors**; Unlazy and UI/UX Pro Max self-tests exit 0. `BUILD.json`: `unresolved_placeholders: {}` (before: 13 files, 9 placeholder kinds), `debts: {}` (before: `gstack_runtime_paths` 48 files, `mcp_mentions` 6 files). Domain transform output: 253 gstack runtime code lines replaced by `# [vikhyath] removed: …`, 94 prose lines marked, frontmatter `hooks:` removed (careful, freeze, guard, investigate, unfreeze), 8 browser/screenshot lines in engineering/testing files annotated with the policy. Notices regenerated (15 upstreams, 13 MIT / 2 Apache-2.0); matrix: closure 42 gaps, 0 open.

## Lifecycle in routes
- `vikhyath route "fix the payment webhook bug" --existing` → BUG_FIX: UNDERSTAND → TEST (rule: failing regression test first) → IMPLEMENT → VERIFY → RECONCILE.
- Scenario A (`build a SaaS for dentists`, new) → UNDERSTAND command `vikhyath project questions "<request>"`; scenario B (Google Maps, existing) ends in RECONCILE; media-only route → no lifecycle.

## Unlazy
- `vikhyath gates lint GATES.md` → `LINT OK` (exit 0); `gates status` → `UNMET: 1` (exit 1, nothing executed).
- `HOME=<scratch> vikhyath runtime unlazy-hook --enable` → hook in `<scratch>/.claude/settings.json`, command `node …/bundles/current/files/unlazy/scripts/stop-hook.mjs --unlazy-hook-v2`; no project file; `--disable` → `{}` (sibling handlers preserved).

## Tests
`python -m unittest discover -s tests`: **194 OK, 3 skipped** (opt-in Graphify runtime). New: `tests/engineering/test_engineering.py` (lifecycle validation, BUG_FIX order, route lifecycle for scenarios A/B and none for media, gstack adaptation incl. continuation lines and idempotence, browser annotation scoped to engineering/testing/codebase, workflows retired, agent frontmatter, thin entry skills, Unlazy gates + central-only hook). `vikhyath doctor` 45/0 (1 warning: Graphify runtime not installed in this home), `vikhyath validate --no-unittest` 22/0, `registry check` valid.
