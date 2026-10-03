# 17 — Testing Audit (Phase 3, spec §57–58, §91)

## Existing tests (v1.0.1)

20 unittest cases in 4 files: manifest fields, YAML shape, SHA format, no-MCP walk, no-vendor, community files. Gaps:

- No behavior tests (routing is never executed).
- Version strings hard-coded (`"1.0.1"` ×5).
- `test_no_vendor_directories` contradicts D-001.
- No dependency declaration (E-1).

## Upstream test suites available as runtime self-tests

| Runtime | Suite | Result in audit | Use |
|---|---|---|---|
| Unlazy | `npm test` (7 suites + self-check) | **188 ok, exit 0** | Bundle self-test for `engineering/completion` |
| UI/UX Pro Max | `unittest` in `scripts/tests` | **164 OK** | Bundle self-test for `design/design-system` |
| BeyondSEO (core only) | `unittest` (250) | 232 pass / 9 skip / 9 fail: the 9 need the optional browser extra | Runtime health for `seo/runtime` without browser |
| BeyondSEO (+`.[browser]` + Chromium) | `unittest` (250) | **250 run, OK, 6 skipped, 0 failures** (28.8 s); browser download **557 MB** | Confirms rendering is a supported, *optional* fallback; size justifies lazy install |
| Graphify | pytest suite (not run; smoke OK) | Smoke: install, update, query | Full run in P12 |
| Addy | `evals/cases/*.json` + fixtures | Not run (REFERENCE) | Acceptance cases for adapted skills (P25) |
| Beacon rules | Embedded `tests:` per rule (77 files) | Not run | Unit tests for the OS rule evaluator (P18) |

## Target test layout (P4 onward)

| Layer | Location | Examples |
|---|---|---|
| Unit | `tests/unit/` | registry schema, glob/rule engine, project id, redactor, context budgets, CEL-subset evaluator |
| Structural | `tests/structural/` | manifests per host, no-MCP across repo **and bundle**, no giant prompts, every capability card valid |
| Routing scenarios | `tests/routing/` | spec §14, §23A.14, §70 A–I as table-driven `request → expected capabilities / forbidden capabilities` |
| Context | `tests/context/` | bytes per level within budget; cache hit skips reread; L3 never loaded by default |
| Isolation | `tests/isolation/` | 3-project interleaving, concurrency, cache keys (doc 14) |
| Bundle/provenance | `tests/bundle/` | rebuild reproducibility (same bundle_id), blob hashes match provenance, closure 0 open, licenses carried |
| Update/rollback | `tests/update/` | doc 16 acceptance cases |
| Runtime self-tests | `tests/runtimes/` (opt-in, slow) | Unlazy, UI/UX Pro Max, BeyondSEO, Graphify suites inside their isolated envs |
| Web verification | `tests/webqa/` | fixture web app: ladder order, no browser started unless a fallback is required, BROWSER_FALLBACK_ACTIVATED emitted with reason |
| Hosts | `tests/hosts/` | generated adapter files validate; host runtime checks recorded as NOT VERIFIED when the tool is absent |
| Offline | `tests/offline/` | all non-update commands with network blocked |

## Evidence format (§58)

`vikhyath test` writes `verification.yaml` entries (TEST-###, objective, command, environment, expected, actual, result, timestamp, phase, task, evidence path) per project. The OS repo uses the same writer for its own test runs under `docs/evidence/`.

## CI changes (P4)

Declared dependencies installed from `pyproject.toml`. Unit, structural and routing suites run on every push. Runtime self-tests run on a nightly or manual workflow (they need venvs and downloads). The "NO vendor" step is replaced by bundle-integrity checks; the no-MCP step stays and also covers the bundle.
