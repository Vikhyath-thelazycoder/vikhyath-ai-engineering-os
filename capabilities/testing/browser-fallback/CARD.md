# testing/browser-fallback — Browser fallback

Bounded headless browser (then visible) only when deterministic checks cannot decide; emits BROWSER_FALLBACK_ACTIVATED.

- **Use when:** visually, overlap, screenshot, open the site, rendering
- **Activation:** fallback · priority 20 · context L2
- **Needs:** runtime playwright-optional; network local-only; browser fallback
- **Loads:** 7 bundled files; entry points: browser-qa, browser-testing-with-devtools, click-path-audit, e2e-runner, e2e-testing
- **Done means:** BROWSER_FALLBACK_ACTIVATED emitted with a reason · bounded run: headless first, visible only if needed
- **Web QA class:** FALLBACK (headless OPTIONAL, visible FALLBACK, screenshot FALLBACK)
- **Related:** — · **Fallback:** —
