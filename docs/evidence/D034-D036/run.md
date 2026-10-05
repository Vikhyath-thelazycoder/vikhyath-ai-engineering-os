# A-1 evidence — Appllama merge + local test-first verification (2026-10-05)

Interpreter: Python 3.14.7, scratch venv and scratch `VIKHYATH_HOME`s. Details: [doc 22](../../audit/22_APPLLAMA_AND_VERIFICATION_POLICY_AUDIT.md).

## Baseline (before any change)
- `python -m unittest discover -s tests`: 160/160 OK
- `vikhyath bundle build`: `c98667e034f7`, 2,594 files, 0 errors (reproduced the P6/P7 id)

## Appllama
- Pinned `Appllama/appllama-skills@dd5caaec3d5d50ad7fc0324da238119c6b7c3707` (MIT); scanner: 18 files, MCP files 2, network/telemetry/background/shell 0
- Bundled: `LICENSE`, `skills/appllama-app-design-skill/SKILL.md` (ADAPT, 20,098 → 13,339 B; 0 MCP mentions), `references/native-controls.md`, `references/motion.md`
- Excluded: `skills/appllama-usage/**`, `.mcp.json`, `mcp.json`, `simulator-loop.md`, `image-assets.md`, `performance.md`, manifests, README

## After
- Tests: **165/165 OK** (5 new: browser-disabled registry, browser-scope rejection, Appllama rewrite, state policy, per-project exception)
- `vikhyath validate`: **23 passed, 0 failed** (new section "Verification Policy": mode + disabled switches; no forbidden file in the bundle plan)
- `vikhyath doctor`: **45 passed, 0 failed**
- `vikhyath registry check`: 63 capabilities + bundle, valid
- Extraction matrix: closure gaps 42 total, **0 open**
- `vikhyath bundle build --self-test`: **`cb0635dbf824` known-good, 2,583 files, 0 errors**; Unlazy and UI/UX Pro Max self-tests exit 0; `bundle verify`: intact
- Bundle contents: no `.mcp.json`/`mcp.json`; no Addy DevTools, ECC browser-qa/e2e-testing/e2e-runner, gstack browser/exploratory/qa-patterns sections or design-review, Agency evidence-collector/reality-checker; gstack `review/SKILL.md` has no exploratory-QA read

## Routing (selected)
| Request | Browser | Capabilities |
|---|---|---|
| Fix the payment webhook. | disabled | engineering/security, engineering/backend, codebase/impact-analysis, testing/local-verification, testing/security (+ testing/evidence) |
| Build a React Native application. | disabled | … engineering/frontend, testing/local-verification, design/frontend (+ testing/evidence) |
| Open the website and show me what it looks like. | exception-requested | testing/local-verification (browser-exception never selected) |

## Context (bytes/4 estimates)
- Bundled browser/visual material removed: −41,087 · Appllama added: +5,891 · net −35,196
- `design/frontend` L2: mobile query ranks the Appllama SKILL first (13.0 KB); web query loads 0 Appllama bytes
