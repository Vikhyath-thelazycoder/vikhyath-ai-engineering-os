# observability/events — Events

Event model and append-only per-project event log.

- **Use when:** emitted by the OS core for every routing, context and verification step
- **Activation:** internal · priority 50 · context L1
- **Needs:** runtime os-native
- **Loads:** OS-native (no bundled files)
- **Done means:** events validate against the schema · secrets redacted
- **Related:** — · **Fallback:** —
