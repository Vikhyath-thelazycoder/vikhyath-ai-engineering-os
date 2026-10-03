# observability/sessions — Sessions

Session/agent state model (SLEEPING…FAILED).

- **Use when:** OS core records session and agent state transitions
- **Activation:** internal · priority 50 · context L1
- **Needs:** runtime os-native
- **Loads:** OS-native (no bundled files)
- **Done means:** state transitions follow the lifecycle
- **Related:** — · **Fallback:** —
