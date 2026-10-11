# Verification policy

One global policy, `config/verification.yaml` (D-035), identical on every host and in every project:

- **Mode: local test-first.** A change is verified by its tests, type checks, lint and build, and the result is recorded
  as evidence: command, exit code, result, counts, time.
- **Disabled:** browser visual verification, Chrome DevTools, screenshot verification and comparison, visual browser
  QA, simulator recording loops. `agylite validate` fails if any is switched on or if an enabled capability needs a
  browser outside SEO/media.
- **Evidence never says** "looks correct", "visual inspection" or "screenshot"; such evidence is rejected.
- **A project's own headless E2E suite** is an ordinary test command and runs only with `--include-e2e`.
- **Browser exception:** when local checks cannot verify something and the user explicitly asks to see it, the request
  is recorded with its reason (`agylite verify exception --reason "…"`, event BROWSER_EXCEPTION_REQUESTED). The user
  operates the browser; the agent does not navigate, click or capture, and no screenshot enters model context.
- **Scoped browser use** that is not verification: BeyondSEO's optional rendered captures (installed only with
  `--browser`) and media rendering. Their output is never engineering evidence.

`agylite doctor` reports host MCP servers such as `chrome-devtools` or `playwright` that other plugins enable; Agylite
never uses them.
