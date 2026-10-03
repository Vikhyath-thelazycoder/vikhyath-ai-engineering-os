# P7 evidence — 2026-10-03T18:08Z

Interpreter: `Python 3.14.6` with PyYAML. `<scratch>` = session scratch `VIKHYATH_HOME`.

## Cards reproduce the P2 domain model exactly
Seeded from `tools/audit/domain-model.yaml` (one-off migration, then the model was removed). Field-by-field comparison of purpose/triggers/runtime/network/browser/context_level/origin/uses/web_qa_class over all 62 capabilities: **0 mismatches**. Docs 05/06 regenerated from the cards: 05 byte-identical; 06 differs only in its "generated from" line. Extraction matrix regenerated from the cards: evidence files byte-identical (`git status docs/audit/evidence` clean).

## Registry check (repository, no bundle)
```
registry (62 capabilities): valid
```

## Real bundle build with registry (dev staging)
```
bundle c98667e034f7 already built and intact
{
 "bundle_id": "c98667e034f7",
 "status": "known-good",
 "counts": {
  "files": 2594,
  "unique_contents": 2556,
  "bytes": 50325178,
  "transformed": 64,
  "capabilities": 56
 },
 "error_count": 0
}
bundle c98667e034f7: intact
registry (62 capabilities + bundle c98667e034f7): valid
5404 BUILD.json
512 files
1034349 index.json
1891764 provenance.json
239189 registry.yaml
512 third_party
```

Bundle id unchanged from P6 (`c98667e034f7`): no extraction input changed. `--self-test` run in this session: unlazy exit 0, uiuxpromax exit 0.

## Registry listing (bundle)
```
engineering/principles               on-demand      p20     4 files
engineering/planning                 on-demand      p50    37 files
engineering/architecture             on-demand      p50    14 files
engineering/implementation           on-demand      p50     6 files
engineering/backend                  on-demand      p50     9 files
engineering/frontend                 on-demand      p50     5 files
engineering/security                 on-demand      p90    33 files
engineering/performance              on-demand      p50     4 files
engineering/review                   on-demand      p50    29 files
engineering/debugging                on-demand      p50     5 files
engineering/simplicity               explicit       p10    23 files
engineering/completion               on-demand      p70    33 files
engineering/release                  on-demand      p50    35 files
engineering/migration                on-demand      p50     2 files
engineering/documentation            on-demand      p50     8 files
engineering/ai-systems               on-demand      p50    12 files
engineering/stack-packs              stack-detected p40   251 files
codebase/repository-understanding    on-demand      p60   556 files
codebase/impact-analysis             on-demand      p60     0 files
codebase/code-search                 on-demand      p60     0 files
design/design-direction              on-demand      p50    12 files
design/visual-quality                on-demand      p50     7 files
design/design-system                 on-demand      p50   571 files
design/typography                    on-demand      p50     5 files
design/ux                            on-demand      p50     2 files
design/accessibility                 on-demand      p50     6 files
design/motion                        on-demand      p50    15 files
design/frontend                      on-demand      p50   144 files
design/design-review                 on-demand      p50    25 files
design/brand                         on-demand      p50    36 files
testing/strategy                     on-demand      p50    15 files
testing/web-verification             on-demand      p50    16 files
testing/security                     on-demand      p85     0 files
testing/accessibility                on-demand      p50     1 files
testing/performance                  on-demand      p50     4 files
testing/regression                   on-demand      p50    14 files
testing/release-verification         on-demand      p70     5 files
testing/browser-fallback             fallback       p20     7 files
seo/runtime                          internal       p50    60 files
seo/auditing                         on-demand      p50    15 files
seo/technical                        on-demand      p50     4 files
seo/on-page                          on-demand      p50     3 files
seo/content                          on-demand      p50     2 files
seo/keyword-research                 on-demand      p50     8 files
seo/competitor-research              on-demand      p50     7 files
seo/ai-search                        on-demand      p50    10 files
seo/entity                           on-demand      p50     2 files
seo/local                            on-demand      p50     7 files
seo/backlinks-reputation             on-demand      p50    17 files
seo/strategy                         on-demand      p50    11 files
seo/research                         on-demand      p50    23 files
seo/evidence                         internal       p50     5 files
seo/reporting                        on-demand      p50    23 files
seo/website-work                     explicit       p30     3 files
media/launch-video                   on-demand      p50   294 files
media/demo                           on-demand      p50    46 files
media/presentation                   on-demand      p50    23 files
media/showcase                       on-demand      p50     2 files
observability/events                 internal       p50     0 files
observability/sessions               internal       p50     0 files
observability/token-metrics          internal       p50     0 files
observability/risk-detection         internal       p50    78 files
source: bundle c98667e034f7
```

## Totals
```
capabilities: 62 | bundled files: 2594
security_class: {'read-only': 30, 'local-exec': 18, 'network': 13, 'privileged': 1}
cache_strategy: {'static': 37, 'project': 3, 'run': 18, 'none': 4}
context_level: {'L1': 8, 'L2': 52, 'L3': 2}
origin: {'bundled': 48, 'mixed': 11, 'os-native': 3}
activation: {'on-demand': 52, 'explicit': 2, 'stack-detected': 1, 'fallback': 1, 'internal': 6}
web_qa_class: {'testing/strategy': 'CORE', 'testing/web-verification': 'CORE', 'testing/security': 'CORE', 'testing/accessibility': 'CORE', 'testing/performance': 'CORE', 'testing/regression': 'CORE', 'testing/release-verification': 'CORE', 'testing/browser-fallback': 'FALLBACK'}
fallbacks: {'codebase/impact-analysis': 'codebase/code-search', 'design/design-review': 'design/visual-quality', 'testing/web-verification': 'testing/browser-fallback', 'testing/accessibility': 'design/accessibility'}
CARD.md L1 est. tokens: max 189 | total 7664
```

## Tests and diagnostics
```
Ran 79 tests in 9.552s

OK
doctor: ✅ All doctor checks passed!
Results: ✅ 45 passed, ❌ 0 failed, ⚠️  0 warnings
Results: ✅ 20 passed, ❌ 0 failed
```

## L1 card size per domain (input for P9 / D-014)
| Domain | Cards | CARD.md est. tokens |
|---|---:|---:|
| engineering | 17 | 2,341 |
| codebase | 3 | 400 |
| design | 10 | 1,193 |
| testing | 8 | 1,082 |
| seo | 16 | 1,802 |
| media | 4 | 448 |
| observability | 4 | 398 |

Every card is ≤ 189 est. tokens (limit 250). Loading **all** engineering cards would exceed D-014's provisional L1 budget (≤2k/domain) by ~17%; P9 must load only the routed capabilities' cards (or a domain index) at L1. Values are bytes/4 estimates.

## Wrappers
`scripts/validate` / `scripts/doctor` pass (20/0, 45/0) with `VIKHYATH_PYTHON` pointing at a PyYAML interpreter. With this machine's Homebrew `python3` (no PyYAML) the validate wrapper exits 1 at the routing section **before and after P7** (checked with `git stash`): an environment gap, not a regression; CI installs the package first.
