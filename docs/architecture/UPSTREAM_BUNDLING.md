# Upstream bundling

Agylite does not ask hosts to install 15 separate plugins. It builds one local bundle from pinned upstream commits.

```bash
agylite bundle fetch            # blobless, sparse clone of the pinned commits (the one network step)
agylite bundle build --self-test
agylite bundle verify           # re-hash every file against provenance
agylite bundle list
```

## Rules

`tools/audit/extraction-rules.yaml` gives every upstream file one decision:

| Decision | Meaning |
|---|---|
| COPY | Shipped unchanged (licenses, references) |
| ADAPT | Shipped with deterministic transforms |
| PRESERVE | Code kept intact to run in an isolated runtime (Graphify, Unlazy, UI/UX Pro Max engine, BeyondSEO, Brag) |
| REFERENCE | Read during the audit, not shipped |
| EXCLUDE | Not shipped, with a reason code (MCP, browser policy, telemetry, installer, always-on, out of domain …) |

About 2,580 of ~24,600 upstream files are bundled.

## Build

- Every source file must match its audited blob hash (no drift, no tampering).
- Transforms (`agylite/bundle/transforms/`): gstack template rendering; targeted rewrites with drift detection;
  domain adaptation — unresolved gstack placeholders replaced with OS text, gstack runtime steps removed and marked,
  upstream skill hooks dropped, browser-verification lines annotated with the policy.
- Dependency closure: a bundled file may not reference a non-bundled file (markdown links, skill-relative paths,
  JS/TS and Python imports including absolute and function-local ones). Accepted exceptions are listed with reasons.
- Hard checks: no MCP configuration in the bundle.
- The build happens in a temporary directory and is renamed into place; `current`/`previous` pointers switch
  atomically. The bundle id is a hash of rules, pins, licenses and transform version, so the same inputs give the
  same bundle.
