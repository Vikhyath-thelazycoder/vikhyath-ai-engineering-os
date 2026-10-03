# P6 evidence — 2026-10-03T17:41Z

## Fresh central install (scripts/install, clean VIKHYATH_HOME, network fetch of 14 pins, sparse)
```
→ Installing Vikhyath OS into <scratch>/install-home
→ Fetching pinned upstreams (network, once)
→ Building and verifying the local bundle
  self-test unlazy: exit 0
  self-test uiuxpromax: exit 0
{
 "bundle_id": "c98667e034f7",
 "status": "known-good",
 "counts": {
  "files": 2594,
  "unique_contents": 2556,
  "bytes": 50325954,
  "transformed": 64,
  "capabilities": 56
 },
 "error_count": 0
}
bundle c98667e034f7: intact

✅ Vikhyath OS installed. Add it to your PATH:
   export PATH="<scratch>/install-home/core/bin:$PATH"
VIKHYATH_HOME=$SP/install-home ./scripts/install  30.06s user 9.85s system 34% cpu 1:54.21 total
install_exit=0
153M	<scratch>/install-home/staging
 57M	<scratch>/install-home/bundles
 14M	<scratch>/install-home/core
5.9M	<scratch>/install-home/src
addy        1.0M
agency      1.2M
beacon      4.9M
beyondseo   1.6M
brag         15M
ecc         6.9M
graphify    5.1M
gstack       13M
karpathy    168K
opendesign   43M
ponytail    596K
taste       680K
uiuxpromax  4.8M
unlazy      320K
```

## Dev build from audit staging: same bundle id
```
  0ad1d647c3cd  known-good  2026-10-03T17:33:16Z
* c98667e034f7  known-good  2026-10-03T17:37:22Z
  ce399cef2822  failed      2026-10-03T17:29:45Z
```

## BUILD.json debts / unresolved (c98667e034f7)
```
unresolved_placeholders: {
 "files/gstack/canary/SKILL.md": [
  "unresolved placeholder BASE_BRANCH_DETECT"
 ],
 "files/gstack/design-review/SKILL.md": [
  "unresolved placeholder DESIGN_DETECTOR",
  "unresolved placeholder DESIGN_METHODOLOGY"
 ],
 "files/gstack/document-generate/SKILL.md": [
  "unresolved placeholder BASE_BRANCH_DETECT"
 ],
 "files/gstack/document-release/SKILL.md": [
  "unresolved placeholder BASE_BRANCH_DETECT"
 ],
 "files/gstack/office-hours/SKILL.md": [
  "unresolved placeholder DESIGN_MOCKUP",
  "unresolved placeholder DESIGN_SKETCH"
 ],
 "files/gstack/plan-ceo-review/SKILL.md": [
  "unresolved placeholder BASE_BRANCH_DETECT"
 ],
 "files/gstack/plan-design-review/SKILL.md": [
  "unresolved placeholder BASE_BRANCH_DETECT"
 ],
 "files/gstack/qa/SKILL.md": [
  "unresolved placeholder BASE_BRANCH_DETECT"
 ],
 "files/gstack/retro/SKILL.md": [
  "unresolved placeholder BASE_BRANCH_DETECT"
 ],
 "files/gstack/review/SKILL.md": [
  "unresolved placeholder BASE_BRANCH_DETECT",
  "unresolved placeholder SCOPE_DRIFT",
  "unresolved placeholder QA_REVIEW"
 ],
 "files/gstack/ship/SKILL.md": [
  "unresolved placeholder BASE_BRANCH_DETECT"
 ],
 "files/gstack/ship/sections/changelog.md": [
  "unresolved placeholder CHANGELOG_WORKFLOW"
 ],
 "files/gstack/ship/sections/plan-completion.md": [
  "unresolved placeholder PLAN_COMPLETION_GATE_SHIP",
  "unresolved placeholder PLAN_VERIFICATION_EXEC",
  "unresolved placeholder SCOPE_DRIFT"
 ],
 "files/gstack/ship/sections/review-army.md": [
  "unresolved placeholder QA_REVIEW"
 ],
 "files/gstack/ship/sections/test-coverage.md": [
  "unresolved placeholder TEST_COVERAGE_GATE_SHIP"
 ]
}
debts: {'mcp_mentions': 8, 'gstack_runtime_paths': 52}
```
