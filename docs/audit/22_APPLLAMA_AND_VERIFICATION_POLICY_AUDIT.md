# 22 — Appllama overlap audit and local test-first verification policy

Date: 2026-10-05 · Decisions: **D-034** (Appllama MERGED), **D-035** (local test-first; supersedes D-020), **D-036** (testing capability shape) · Evidence: [docs/evidence/D034-D036/run.md](../evidence/D034-D036/run.md) · Bundle: `c98667e034f7` → **`cb0635dbf824`**

This is an amendment to the existing architecture, not a parallel one: one registry, one router, one plan, one verification policy.

## 1. Audit of the current repository (before any change)

| Area | Finding |
|---|---|
| Architecture | P0–P11 + P18 built (M0–M3). Bundle `c98667e034f7` (2,594 files, 14 upstreams), registry 62 capabilities, routing v2, context L0–L3, project state, isolation, event log. M4–M7 not started. |
| Browser verification in the **registry** | `testing/browser-fallback` (`runtime_type: playwright-optional`, `requires_browser: fallback`, `web_qa_modes {headless OPTIONAL, visible FALLBACK, screenshot FALLBACK}`); `testing/web-verification` → `fallback_capability: testing/browser-fallback`; `testing/accessibility`, `design/design-review` had `requires_browser: fallback`; schema class `FALLBACK`. |
| … in the **bundle** (extraction rules) | `testing/browser-fallback` ← Addy `skills/browser-testing-with-devtools/**` (Chrome DevTools MCP), ECC `skills/browser-qa/**`, `skills/e2e-testing/**`, `skills/click-path-audit/**`, `agents/e2e-runner.md`, gstack `qa/sections/browser-{setup,verify}.md*`. `testing/web-verification` ← gstack `qa/**`, `qa-only/**` (16 of 20 files drive the gstack browser). `design/design-review` ← gstack `design-review/**` (88 screenshot/browse mentions). `testing/*` ← Agency `testing-evidence-collector.md`, `testing-reality-checker.md` (screenshot-evidence personas, 34 and 36 mentions). |
| … in **routing** | Rule `explicit-visual` selected `testing/browser-fallback`; router output `browser: none / fallback-only / explicit-visual`; scenarios s23a-* expected `fallback-only`. |
| … in **events / plan** | `BROWSER_FALLBACK_ACTIVATED`; D-020 ladder (… → headless → visible); P15 plan had `vikhyath/runtimes/playwright.py`, `verify/browser.py`, `config/webqa.yaml`. |
| MCP | None in the plugin. Upstream MCP surfaces already excluded (D-021 exception for Graphify's parser only). Host note: the user's separately installed ECC plugin exposes a `chrome-devtools` MCP — outside this repo; P25 doctor reports it (§7). |
| Design stack | OpenDesign + Taste + UI/UX Pro Max + ECC design skills in 10 design capabilities. Native mobile: ECC `react-native-patterns` + `rules/react-native/*` (engineering), UI/UX Pro Max `stacks/react-native.csv` (generic), Taste `imagegen-frontend-mobile` (image direction). OpenDesign `apple-hig`, `platform-design`, `swiftui-design` are **1.3 KB catalogue stubs** pointing at other repos — no guidance. |

Classification of the browser paths: **required** — none; **optional** — none survive; **duplicated** — gstack `qa-only` ≈ `qa`; **incompatible** — all of the above (they make the agent operate a browser or treat screenshots as evidence). **Kept, scoped:** SEO crawler/capture inside the isolated SEO runtime (P16) and media rendering (Brag, P17) — output, never verification evidence.

## 2. Appllama audit (`Appllama/appllama-skills@dd5caaec3d5d50ad7fc0324da238119c6b7c3707`, MIT, 18 files, 68 KB)

Inventory: `.claude-plugin/`, `.cursor-plugin/` (Cursor's manifest declares `mcpServers`), `.mcp.json` + `mcp.json` (`https://mcp.appllama.io/mcp`), `skills/appllama-usage/` (4 files: MCP tool map, credits, research playbooks), `skills/appllama-app-design-skill/` (SKILL.md 20 KB + 5 references). Scanner: MCP files 2, MCP indicators 3; network, telemetry, background, shell 0. Runtime assumptions: an Appllama Pro account + monthly credits for `appllama-usage`; the design skill claims to work without the MCP, but its prime directive and definition of done assume it, and its verification is a simulator screenshot + screen-recording loop.

### Overlap matrix

| Capability | Existing Vikhyath source | Appllama source | Overlap | Unique value | Decision |
|---|---|---|---|---|---|
| Mobile app research (top-grossing screens) | — | `appllama-usage/**` | — | Paid remote service | **EXCLUDE** (MCP, credits) |
| Navigation semantics (push vs replace, modal/sheet/overlay meaning, one-way doors, when back may be blocked, tabs as peers, deep links) | ECC RN patterns: route params only; UI/UX RN CSV: "handle back button" | SKILL.md "Navigation laws" | Low | High — no bundled source | **EXTRACT → MERGE** `design/frontend` |
| Native control selection + wiring (switch/segmented/slider/pickers/menus/sheets/forms; rebuilt-control numbers) | UI/UX RN CSV generic rows; zeego in 4 design-system files | `references/native-controls.md` | Low | High | **EXTRACT → MERGE** `design/frontend` |
| Native fidelity (semantic colors, SF Symbols, continuous corners, safe areas, type ramp, haptics) | design-system CSVs (touch targets, dark mode, tabular nums); OpenDesign HIG stubs | SKILL.md "Native fidelity laws" | Partial | Medium (Expo-specific, concrete) | **EXTRACT → MERGE** `design/frontend` (same file) |
| RN motion (gesture-velocity springs, UI-thread worklets, frequency gate, Reduce Motion) | `design/motion`: ECC motion-* + OpenDesign GSAP/Emil — web only | `references/motion.md` + SKILL.md "Motion laws" | Low for RN | High | **EXTRACT → MERGE** `design/motion` (+ laws in SKILL.md) |
| Anti-slop | Taste `taste-skill` (accent/grey/radius/gradient/glass rules), OpenDesign `craft/anti-ai-slop.md` | SKILL.md "Anti-slop laws" | High | Low (mechanical counts) | **EXCLUDE** — canonical in `design/visual-quality`; rewrite points there |
| State architecture | ECC `react-native-patterns` (TanStack Query, Zustand, form state) | SKILL.md "State architecture" | High | Low (uncontrolled inputs) | **EXCLUDE** — canonical `engineering/stack-packs`; one-line mobile addition kept |
| RN performance | ECC `rules/react-native/performance.md`, `engineering/performance` | `references/performance.md` | ~60% | Budgets table, typing perf | **EXCLUDE** — ECC canonical; SKILL.md keeps its perceived-performance bullets |
| Image/illustration assets | Taste `imagegen-frontend-mobile`, `design/brand` | `references/image-assets.md` | High; suggests Higgsfield MCP | Low | **EXCLUDE** (DUPLICATE) |
| Simulator verification loop | — | `references/simulator-loop.md`, SKILL.md "simulator loop" + "full-motion pass" | — | Contradicts D-035 | **EXCLUDE** (BROWSER_POLICY); replaced by testable checks |

**Result: APPLLAMA_STATUS = MERGED** (outcome B). No Appllama domain or capability (the registry validator rejects repo-named ids). The OS is fully functional with Appllama absent: no runtime, no network, no account.

### Extracted files (provenance in every bundle's `provenance.json`; license in `third_party/licenses.json`)

| Source path | Decision | Capability | Modification |
|---|---|---|---|
| `LICENSE` | COPY | design/frontend | verbatim (D-002) |
| `skills/appllama-app-design-skill/SKILL.md` | ADAPT | design/frontend | 11 targeted rewrites (`vikhyath/bundle/transforms/rewrites.py`; drift fails the build): description; prime directive → "study patterns, not pixels" (no MCP); navigation law 6 de-branded; anti-slop → pointer to `design/visual-quality`; motion bar → measured, no recording; state → pointer to `engineering/stack-packs`; performance link → ECC; image assets removed; simulator loop → "Verification (local test-first)"; definition of done → testable checks; references table → 2 files. 20,098 → 13,339 B. |
| `…/references/native-controls.md` | COPY | design/frontend | none |
| `…/references/motion.md` | COPY | design/motion | none |

Excluded: `skills/appllama-usage/**` (PAID_SERVICE), `.mcp.json`, `mcp.json` (MCP), `references/simulator-loop.md` (BROWSER_POLICY), `references/image-assets.md`, `references/performance.md` (DUPLICATE), `.claude-plugin/**`, `.cursor-plugin/**` (HOST_PORT), `README.md`, `.gitignore` (REPO_META). Closure: the three removed links are accepted gaps (removed by the ADAPT rewrite). Extraction date 2026-10-05.

## 3. Upstream browser / MCP classification (all 15 upstreams)

`MCP ind.`/`Browser ind.` = scanner indicator counts over the full snapshot (doc 04 method).

| Upstream | MCP files | MCP ind. | Browser ind. | Browser material | Decision |
|---|---|---|---|---|---|
| addy | 0 | 4 | 4 | `browser-testing-with-devtools` (DevTools MCP) | EXCLUDE; TDD/testing knowledge kept |
| agency | 0 | 3 | 0 | evidence-collector, reality-checker personas (screenshot evidence) | EXCLUDE (2); API tester, results analyzer kept |
| appllama | 2 | 3 | 0 | simulator loop | EXCLUDE + MCP + usage (§2) |
| beacon | 2 | 72 | 35 | detection-rule strings only | no change (rules evaluate events) |
| beyondseo | 0 | 1 | 11 | crawler/browser extra | **scoped to the SEO runtime** (P16); never global verification |
| brag | 0 | 0 | 1 | video rendering | **scoped to media** (P17) |
| ecc | 2 | 157 | 33 | `browser-qa`, `e2e-testing`, `e2e-runner` | EXCLUDE (3); `click-path-audit` → local-verification |
| graphify | 0 | 46 | 6 | none bundled for verification | no change (D-021) |
| gstack | 0 | 24 | 272 | `browse/` etc. (already excluded); `qa`/`qa-only` SKILL + browser/exploratory/patterns sections + report template; `design-review/` | EXCLUDE; non-browser QA methodology kept; `review/SKILL.md` exploratory-QA step rewritten to local verification |
| karpathy, taste, unlazy | 0 | 0 | 0 | — | no change |
| opendesign | 1 | 200 | 389 | product app/daemon (already excluded) | no change |
| ponytail | 0 | 4 | 1 | — | no change |
| uiuxpromax | 1 | 7 | 20 | `stack/.mcp.json` (already excluded) | no change |

Residual (honest): 110 bundled files outside SEO/media still *mention* Playwright or screenshots in passing (test-automation guidance, design-system docs, issue-taxonomy wording; 499 mentions in the pre-Agency-exclusion count). None is an executable browser step or acceptance gate. Domain adaptation in P13–P15 owns removing or reframing them (adaptation debt, D-027 style). A project's own E2E suite run headless (`npx playwright test`) remains an ordinary test command whose counts are evidence.

## 4. Target verification architecture

```
IMPLEMENT → TEST → STATIC → SECURITY → INTEGRATION → ACCEPTANCE → EVIDENCE → STATE UPDATE
            │       │        │          │             │            │          │
            │       types,   testing/   API/route/    plan task    testing/   state.yaml verification
            │       lint,    security   state tests   acceptance   evidence   (mode, last, evidence);
            │       build                             criteria     command +  verification.yaml history
            └ selection: codebase/impact-analysis (Graphify) → smallest sufficient set; full suite only at release
```

- One policy: `config/verification.yaml` (mode `local-test-first`; six mechanisms disabled; evidence fields; exception rules; scoped SEO/media use), loaded by `vikhyath/verify/policy.py`.
- Registry: `testing/local-verification` (CORE), `testing/evidence` (CORE, internal), `testing/browser-exception` (DISABLED_BY_POLICY, `enabled: false`, no files). `runtime_status` on every registry entry. The schema rejects `requires_browser ≠ none` outside SEO/media and any enabled DISABLED_BY_POLICY card; routing validation rejects any rule that selects a disabled capability.
- Router: `browser: disabled` always; `exception-requested` only for an explicit "show me the site" (local verification still runs; the user opens the URL themselves); `verification_mode` in every route.
- Exception path: `state.record_browser_exception(project, reason)` → that project's `verification.yaml` + `BROWSER_EXCEPTION_REQUESTED`; screenshots never enter context. CLI `vikhyath verify exception` lands in P15.
- Not acceptable evidence: "looks correct in Chrome", "screenshot looks good". Acceptable: `npm test: 184 passed`, `pytest: 97 passed`, `pnpm typecheck: passed`.

## 5. Phase impact matrix (existing P0–P27; the update's "Phase 0–25" map 1:1 onto P0–P2 and P5–P27)

| Phase | Changed? | Why | Files | Verification |
|---|---|---|---|---|
| P0 Repo audit | Amended | Browser/Chrome/screenshot search; Appllama setup | this doc §1 | grep evidence (run.md) |
| P1 Upstream audit | Amended | +Appllama; browser/MCP classification for all 15 | `upstream-file-hashes/appllama.tsv`, `upstream-scan/appllama.json`, §2–3 | scanner |
| P2 Capability architecture | Amended | Appllama merged (no domain); testing reshaped | cards, `domain.yaml`, D-034/D-036 | registry check |
| P3 Cross-cutting/plan | Amended | Plan + file-level plan reconciled | `docs/plan/*` | review |
| P4 Core | NO CHANGE | CLI/package unaffected (new module only) | — | tests |
| P5 Provenance | Amended | Appllama license/attribution; reason codes BROWSER_POLICY, PAID_SERVICE | `licenses.json`, `THIRD_PARTY_NOTICES.md`, rules | test_provenance |
| P6 Bundling | Amended | Exclusions, 2 rewrites, accepted gaps; new known-good bundle | rules, `rewrites.py` | build 0 errors, self-tests |
| P7 Registry | Amended | 63 caps, `runtime_status`, DISABLED_BY_POLICY, browser scope rule | `schema.py`, `generate.py`, cards | test_registry |
| P8 Routing | Amended | Browser output, `mobile-native`, `webhook-verification`, explicit-visual → exception; BM25 method-label bug | `routing.yaml`, `rules.py`, `router.py`, scenarios | 22 scenarios |
| P9 Context | NO CHANGE (code) | Progressive loading already ranks files; browser files no longer exist in the bundle | — | measured §8 |
| P10 State | Amended | Verification block (mode + disabled switches + last), exception log | `state.py` | test_project |
| P11 Isolation | Amended (tests) | Exceptions/evidence per project | `test_project.py` | isolation test |
| P12 Graphify | Plan only | Graphify selects tests (impact → test set); it is not a verifier | plan | P12 |
| P13 Engineering | Plan only | Remove residual browser steps from adapted gstack/ECC/Addy text | plan | P13 |
| P14 Design | Plan only | Overlap matrix done (§2); design-token validation checks | plan | P14 |
| P15 Testing | **Rewritten** | Runner + evidence writer under the policy; no Playwright runtime | plan | P15 |
| P16 SEO | Plan note | Browser stays inside the SEO runtime | plan | P16 |
| P17 Media | Plan note | Showcase output ≠ evidence | plan | P17 |
| P18 Observability | Amended | `BROWSER_EXCEPTION_REQUESTED` replaces the fallback event | `events/schema.py` | test_project |
| P19–P22 Hosts | Plan only | Same policy file; adapters may not enable browser/MCP | plan | P19–P22 |
| P23 Dashboard | Plan only | Shows verification mode, evidence, disabled caps; no visual-QA view | plan | P23 |
| P24 Update | Plan only | Appllama: update only the extracted files; overlap re-audit on diff | plan | P24 |
| P25 Diagnostics | Partly pulled forward | `validate` already checks policy + forbidden bundle paths; doctor adds host MCP/Chrome detection | `validate.py` | validate 23/0 |
| P26 Docs | Plan only | Architecture/testing/verification docs | plan | P26 |
| P27 Integration | Plan only | Adds the policy checklist (§9) | plan | P27 |

Phase order: unchanged (no dependency moved).

## 6. Migration order (as executed) and rollback

1. Pin + inventory + scan Appllama → 2. extraction rules (exclusions, Appllama) → 3. rewrites → 4. cards (rename, disable, evidence) → 5. schema/generator → 6. policy file + `verify/policy.py` → 7. routing rules + router → 8. state + events → 9. validate → 10. tests → 11. regenerate notices, cards, matrices → 12. bundle build + verify.

Rollback: `git revert <commit>`; delete `$VIKHYATH_HOME/bundles/cb0635dbf824` (the previous id stays valid via `previous`). Projects' `.vikhyath/state.yaml` only gain extra verification keys; the old reader ignores them.

## 7. Diagnostics

`vikhyath validate` (section "Verification Policy"): mode; six disabled switches; no enabled card needing a browser outside SEO/media; no DISABLED_BY_POLICY card enabled; no forbidden file (MCP config, `appllama-usage`, simulator loop, DevTools/browser-QA/e2e-runner, gstack browser sections/design-review) in the bundle plan. Routing validation: no rule selects a disabled capability. Schema: repo-named ids rejected (no `design/appllama`). Bundle build: hard MCP-config check; pins are 40-hex SHAs. Still for P25: doctor detection of a host-installed Chrome DevTools MCP (this machine has one through the separately installed ECC plugin) and stale-pin age.

## 8. Token / context impact (measured from the two registries, bytes/4 estimates)

| Measure | Before `c98667e034f7` | After `cb0635dbf824` | Δ |
|---|---|---|---|
| Bundled browser/visual material | browser-fallback 10,532; web-verification browser QA 14,036; gstack design-review 13,683; Agency personas 2,714; review step 122 | 0 | **−41,087** |
| Appllama added | — | design/frontend +4,774, design/motion +1,117 | **+5,891** |
| All bundled content | 12,581,275 | 12,546,079 | −35,196 |
| L1 cards (63; only routed cards load) | 7,664 | 7,915 | +251 |
| Bootstrap (L0) | — | + one policy line | ≈ +15 |
| L2 "Build a React Native application…" | — | 9,314 | Appllama not loaded (design/frontend is beyond the 3 full capabilities) |
| L2 `design/frontend`, mobile query | — | Appllama SKILL ranks 1st (13.0 KB) | loaded only when relevant |
| L2 `design/frontend`, web query | — | Appllama not loaded | 0 |

## 9. Acceptance checklist

APPLLAMA: audited ✔ · overlap documented ✔ · unique capabilities identified ✔ · only required material extracted (3 files + LICENSE) ✔ · no appllama-usage ✔ · no Appllama MCP ✔ · no credits ✔ · no remote runtime ✔ · no simulator/screenshot loop ✔ · provenance ✔ · exact SHA ✔.

VERIFICATION: local test-first default ✔ · Chrome DevTools disabled ✔ · screenshot verification disabled ✔ · visual browser QA disabled ✔ · gstack browser QA excluded ✔ · ECC browser workflows excluded ✔ · Agency browser workflows excluded ✔ · upstreams classified ✔ · evidence machine-readable: policy fields ✔, writer/CLI in P15 ◐ · project state records verification ✔ · diagnostics detect violations ✔ (host MCP detection: P25 ◐).

ARCHITECTURE: no MCP ✔ · central plugin ✔ · no project-local OS ✔ · isolation ✔ · capability-based ✔ · progressive loading ✔ · no duplicate design stacks ✔ · no duplicate verification systems ✔ · Graphify = codebase intelligence ✔ · Beacon = observability ✔ · dashboard separate (P23) ✔.

PLANNING: plan updated ✔ · affected phases updated ✔ · acceptance/verification/migration/rollback updated ✔ · provenance ✔ · docs: this doc ✔, full docs set in P26 ◐.
