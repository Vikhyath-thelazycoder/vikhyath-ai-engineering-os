# P8 evidence — routing engine (2026-10-04)

Interpreter: `Python 3.14.7` with PyYAML, in a fresh venv (`pip install -e .`). No model tokenizer is involved; routing is pure Python.

## Config validation
`config/routing.yaml` v2 is validated against the 62 capability cards and the `config/priorities.yaml` hierarchy (`vikhyath.routing.rules.validate_routing`): **0 problems**. Planted errors are caught: an unknown capability, an internal capability selected by a rule, an explicit-only capability selected by a non-explicit rule, and a missing §54 change type (`tests/routing/test_routing.py::test_validator_catches_planted_errors`).

## Spec scenarios (`tests/routing/scenarios.yaml`, all pass)
Each scenario asserts expected capabilities (capabilities ∪ dependencies), forbidden domains/capabilities, and where the spec states them the change type, browser policy and pipeline. Spec names the registry implements under a domain-first id are mapped by the scenario file's `aliases` (testing/integration and testing/responsive → testing/web-verification; seo/aeo and seo/geo → seo/ai-search; "security baseline" → engineering/security; "native crawler" → seo/runtime).

| Scenario | Stage | Change type | Capabilities (guidance order) | Dependencies | Browser |
|---|---|---|---|---|---|
| s14-checkout-security — “Improve checkout security.” | existing | SECURITY_CHANGE | engineering/security, engineering/backend, testing/security, codebase/impact-analysis | codebase/repository-understanding | none |
| s14-landing-premium — “Make the landing page feel premium.” | unknown | DESIGN_CHANGE | design/design-direction, design/visual-quality, design/design-review, design/frontend, design/typography | — | none |
| s14-seo-audit — “Audit my website's SEO.” | unknown | SEO_CHANGE | seo/auditing, seo/content, seo/reporting, seo/technical | seo/runtime, seo/evidence | none |
| s14-ai-search — “Make my website rank better in AI search.” | unknown | SEO_CHANGE | seo/content, seo/ai-search, seo/auditing, seo/entity, seo/reporting, seo/technical | seo/evidence, seo/runtime | none |
| s14-build-saas — “Build a SaaS application.” | new | NEW_FEATURE | engineering/security, engineering/architecture, engineering/planning, engineering/implementation, testing/strategy, design/design-direction | — | none |
| s23a-login-flow — “Check whether the login flow works.” | existing | TESTING_CHANGE | testing/security, testing/web-verification | engineering/security | fallback-only |
| s23a-mobile-overlap — “Check whether the mobile header overlaps the hero.” | existing | TESTING_CHANGE | testing/web-verification, design/frontend, design/visual-quality | — | fallback-only |
| s23a-explicit-visual — “Open the website and show me what it looks like.” | existing | TESTING_CHANGE | testing/browser-fallback | — | explicit-visual |
| s23a-technical-seo — “Audit the site's technical SEO.” | unknown | SEO_CHANGE | seo/technical, seo/auditing, seo/content, seo/reporting | seo/runtime, seo/evidence | none |
| s70-a-new-saas — “Build me a travel booking SaaS with AI trip planning.” | new | NEW_FEATURE | engineering/security, engineering/architecture, engineering/planning, engineering/ai-systems, engineering/implementation, testing/strategy, design/design-direction | — | none |
| s70-b-existing-maps — “Add Google Maps navigation to bookings.” | existing | NEW_FEATURE | engineering/security, engineering/implementation, engineering/backend, testing/strategy, codebase/impact-analysis | codebase/repository-understanding | none |
| s70-c-security-bug — “Fix the payment webhook security.” | existing | SECURITY_CHANGE | engineering/security, engineering/backend, testing/security, codebase/impact-analysis | codebase/repository-understanding | none |
| s70-d-design — “This landing page looks generic. Make it feel premium.” | existing | DESIGN_CHANGE | design/design-direction, design/visual-quality, design/design-review, design/frontend, design/typography | — | none |
| s70-e-seo-audit — “Audit my website.” | unknown | SEO_CHANGE | seo/auditing, seo/content, seo/reporting, seo/technical | seo/runtime, seo/evidence | none |
| s70-f-seo-fix — “Audit my website and fix all technical SEO issues.” | existing | SEO_CHANGE | engineering/implementation, testing/web-verification, seo/auditing, seo/technical, seo/content, seo/reporting | seo/runtime, seo/evidence | fallback-only |
| s70-g-ai-search — “Make the website more visible in AI-generated answers.” | unknown | SEO_CHANGE | seo/ai-search, seo/content, seo/entity | seo/evidence | none |
| s70-h-launch-video — “Make a launch video plan for our product.” | existing | MEDIA_CHANGE | media/launch-video | — | none |
| simplicity-explicit — “Is this overengineered? Please simplify it.” | existing | REFACTOR | engineering/simplicity, codebase/impact-analysis | codebase/repository-understanding | none |
| refactor-no-simplicity — “Refactor the billing module.” | existing | REFACTOR | engineering/implementation, testing/regression, codebase/impact-analysis | codebase/repository-understanding | none |

Scenario F's pipeline is `seo → engineering → testing`. Scenario I (multi-project isolation) is tested in P11.

## Fallback behaviour
- “translate the app into french” → method `bm25`, confidence `low` (engineering/frontend, + its dependency design/frontend).
- “prepare a slide deck about q3” → method `tags`, confidence `low` (media/presentation).
- “hello there” → method `none`, confidence `none`, no capabilities.
BM25 builds its index only when deterministic routing is not confident; confident routes never read CARD.md.

## Performance (acceptance: p95 < 100 ms)
- `Router()` init (62 cards + routing.yaml + priorities.yaml): 41.5 ms, once per process.
- `route()` over 950 calls (19 scenarios × 50): median **0.218 ms**, p95 **0.333 ms**, max 0.381 ms.
- Whole CLI process `vikhyath route "Audit my website." --brief`, 5 runs: 0.08–0.09 s wall (interpreter start included).
- The test suite asserts p95 < 100 ms (`tests/routing/test_scenarios.py::test_routing_p95_under_100ms`).

## Suite
- `python -m unittest discover -s tests`: **96 tests OK** (79 before P8; v1 YAML-shape routing tests replaced by behaviour tests).
- `vikhyath doctor`: 45 passed, 0 failed. `vikhyath validate`: 20 passed, 0 failed (routing section now validates config v2 and five smoke routes).
- `vikhyath registry check` (bundle `c98667e034f7`): reported `registry.yaml is stale` after the `seo/ai-search` card gained `dependencies: [seo/evidence]`; `vikhyath registry build` → valid. `bundle verify`: intact.
