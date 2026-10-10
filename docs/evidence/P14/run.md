# P14 evidence — design domain (2026-10-10)

- `vikhyath bundle build --self-test`: **`495f026f381e` known-good, 2,583 files, 0 errors**, `debts {}`, `unresolved_placeholders {}`; Unlazy + UI/UX Pro Max self-tests exit 0.
- `vikhyath runtime status`: unlazy ready, uiuxpromax ready (stdlib), graphify not-installed in this scratch home (fallback documented in P12).
- `vikhyath design search "calm fintech dashboard" --domain color -n 2` → 2 results from `colors.csv` (primary/secondary/accent tokens).
- `vikhyath design system "fintech dashboard calm" --persist` (test) → only `design-system/ledger/{MASTER.md,pages/}` created, inside the project root.
- `vikhyath design check`: disciplined fixture (1 accent hue, neutral greys, 1 radius, 1 font) → PASS; drift fixture (7 accent hues, slate + stone greys, 7 radii, 4 fonts) → FAIL with values; `node_modules` ignored. On this repository: PASS (no style sources).
- Routing: scenario D ("This landing page looks generic. Make it feel premium.") → domains `[design]`, no lifecycle; "build the onboarding screens for our React Native app" → includes `design/frontend`.
- `python -m unittest discover -s tests`: **199 OK, 3 skipped**; doctor 46/0; validate 22/0.
