# Security model

| Area | Control |
|---|---|
| MCP | None used or configured; the bundle build fails on MCP configuration; two parser-only Graphify modules are documented exceptions (D-021, D-037) |
| Always-on behaviour | No daemons, no upstream hooks (gstack, ECC, Ponytail, Graphify, Unlazy installers excluded); upstream skill frontmatter hooks removed at build; runtimes start per command |
| Supply chain | Pinned 40-character SHAs; audited blob hashes checked at build; dependency closure; provenance per file; explicit, checked updates with rollback |
| Secrets | Runtimes run without secret-named environment variables (API keys, tokens, passwords); events and diagnostics are redacted; SEO authorizations store no credentials |
| Live systems | Website edits need a per-task, expiring authorization; deploys are never run without the user's go-ahead |
| Isolation | Path guard, per-project locks and data directories; the dashboard binds 127.0.0.1 and is read-only |
| Verification | Local test-first; browser, DevTools and screenshots disabled (VERIFICATION_POLICY) |
| Risk detection | Beacon rules over host tool events; alerts logged |

Report vulnerabilities as described in [SECURITY.md](../../SECURITY.md).
