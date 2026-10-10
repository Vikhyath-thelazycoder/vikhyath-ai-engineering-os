---
name: vikhyath-codebase
description: Understand an existing codebase before changing it — affected files and the tests that cover a change, from the project's code graph (Graphify) via `vikhyath codebase`.
---

# Vikhyath Codebase

Use when `vikhyath route` selects a `codebase/*` capability or returns an `impact` step. Narrow the code surface
first; never read or paste the whole repository.

## Steps

1. **Impact of the change** (from the project directory):

   ```bash
   vikhyath codebase affected                       # files changed in the working tree (git status)
   vikhyath codebase affected --paths src/payments  # or the files/directories the task will touch
   ```

   Read only the listed `files` (at most `limit`, default 12) and run the listed `tests` first. `omitted` counts
   what the limit dropped; ask for a narrower path rather than reading everything. Treat each `unknown` entry as
   UNKNOWN in your answer, not as "unaffected".

2. **Questions about the code** — scoped subgraphs with `file:line`, not file dumps:

   ```bash
   vikhyath codebase query "how are webhooks verified"
   vikhyath codebase explain PaymentService
   vikhyath codebase path WebhookHandler charge
   ```

3. **When the result carries a `notice`** ("graph-based analysis unavailable; limited structural analysis used"),
   say so in your answer. Only Python and relative JS/TS imports were followed. `vikhyath runtime status` shows
   why; `vikhyath runtime install graphify` installs the runtime when the user agrees (it needs the network).

## Rules

- The graph lives in the OS data directory, never in the project. Do not run `graphify` directly, and never use
  `graphify hook`, `install`, `watch`, `serve` or `extract`: the OS blocks them (no git hooks, no background
  process, no MCP, no LLM extraction).
- New projects have no codebase step; start from requirements instead.

Verification policy: local test-first (`config/verification.yaml`) — no browser, Chrome DevTools, screenshots or MCP.
