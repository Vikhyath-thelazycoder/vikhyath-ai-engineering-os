# testing/browser-exception — Browser exception

Browser/visual verification is disabled by policy; an explicit user request is recorded as a logged per-project exception instead.

- **Use when:** never by routing; only `vikhyath verify exception` after local checks are insufficient, no equivalent test exists and the user explicitly asked (config/verification.yaml)
- **Activation:** explicit · priority 50 · context L1 · DISABLED_BY_POLICY
- **Needs:** runtime os-native
- **Loads:** OS-native (no bundled files)
- **Done means:** BROWSER_EXCEPTION_REQUESTED event with the reason local verification was insufficient · no screenshot in model context
- **Web QA class:** DISABLED_BY_POLICY (headless DISABLED_BY_POLICY, visible DISABLED_BY_POLICY, screenshot DISABLED_BY_POLICY, chrome_devtools DISABLED_BY_POLICY)
- **Related:** testing/local-verification · **Fallback:** —
