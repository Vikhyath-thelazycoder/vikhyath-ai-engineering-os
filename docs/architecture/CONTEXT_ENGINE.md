# Context engine

Context is loaded in four levels with budgets in `config/budgets.yaml` (every limit documented with its reason).
Tokens are estimates: bytes ÷ 4.

| Level | What | Budget | Command |
|---|---|---|---|
| L0 | Identity, host, project, session, phase, compact state, plan pointer, capability index | 1,500 | `agylite bootstrap` (SessionStart) |
| L1 | Routed capability cards (CARD.md) | 2,000 per domain | `agylite context <ids> --level 1` |
| L2 | The most relevant sections of up to 3 capabilities' files; the rest as an index | 8,000 per task | `agylite context <ids>` |
| L3 | One explicit file (or sections) | 12,000 per fetch | `agylite context --file <bundle path>` |

- Sections are split from markdown headings and ranked by BM25 against the request.
- A per-bundle context index is built once; a per-project, per-session cache skips files already sent in the session
  (bundle files keyed by provenance hash, project files by size + mtime). A second identical load reads 0 bytes.
- Project decisions relevant to the routed capabilities are appended to L1.
- The code surface is limited separately: `agylite codebase affected` returns at most 12 files plus their tests.
- `$AGYLITE_BUNDLE/files/…` in bundled text refers to bundle files; load one with `agylite context --file files/…`.
