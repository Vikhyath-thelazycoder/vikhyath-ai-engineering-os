# testing/web-verification — Web verification

Local-first ladder: build, types, lint, unit/integration, HTTP/API, DOM/state, console/network capture (§23A).

- **Use when:** verify, check whether, works, flow, login, checkout, qa
- **Activation:** on-demand · priority 50 · context L2
- **Needs:** runtime os-native; network local-only; codebase analysis first
- **Loads:** 16 bundled files; entry points: qa, qa-only
- **Done means:** deterministic ladder run (build, types, lint, tests, HTTP/DOM) with results recorded · no browser started unless the ladder cannot decide
- **Web QA class:** CORE
- **Related:** testing/strategy · **Fallback:** testing/browser-fallback
