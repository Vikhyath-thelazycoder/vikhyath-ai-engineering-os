# Project state

Each project owns compact state in `<project>/.agylite/` (a pre-rename `.vikhyath/` is used while it is the only one):

| File | Content |
|---|---|
| `state.yaml` | identity, stage (new/existing), stack, plan pointer, answered questions, verification block (policy + last result) |
| `plan-index.yaml` | phases and tasks parsed from the one human plan (`docs/IMPLEMENTATION_PLAN.md` by default) |
| `decisions.yaml` | structured decisions by kind (architecture, security, design, product, data, infrastructure, testing, seo, media, process) |
| `verification.yaml` | verification history and recorded browser exceptions |
| `evidence/<time>.json` | machine-readable verification evidence |
| `seo-authorizations.yaml` | per-task, expiring authorizations for live-site edits |

Commands: `agylite project init [--new|--existing] [--docs]`, `agylite state`, `agylite plan index|show|locate|add-task|set-status|reconcile`,
`agylite decide add|list|show`, `agylite project questions|answer`.

## Lifecycle

`config/lifecycle.yaml`: UNDERSTAND → PLAN → IMPLEMENT → TEST → VERIFY → RECONCILE, reordered per change type
(bug fix: failing regression test first; refactor: green before and after; security: negative tests). Completion
states follow spec §25; VERIFIED and COMPLETED require evidence. `agylite plan reconcile "<request>"` adds a change to
the right phase of the existing plan instead of creating a new document.
