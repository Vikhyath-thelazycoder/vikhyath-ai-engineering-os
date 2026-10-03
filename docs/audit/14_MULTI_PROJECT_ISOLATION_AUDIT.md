# 14 — Multi-Project Isolation Audit (Phase 3, spec §2.4)

## Current state

v1.0.1 has no project state, so there is nothing to leak today. The **installed upstream tools do share global state across projects**:

| Source | Global state | Isolation risk |
|---|---|---|
| ECC hooks | `~/.claude/session-data/`, instincts, cost logs; SessionStart "load previous context" | Previous session context from another project can be injected |
| Unlazy | `~/.unlazy/approved` | Approvals are bound to ledger+cwd+command, so they are safe by construction |
| Ponytail | `~/.claude/.ponytail-active`, `~/.config/ponytail/` | Mode flag is global, not per project |
| Graphify | `graphify-out/` inside each project (per project by default) | Safe, but violates §2.3 placement |
| gstack | `~/.gstack/` (learnings, sessions, telemetry) | Learnings shared across projects |

## Structural isolation design (implemented in P10–P11)

1. **Project identity.** `project_id = sha256(realpath(git toplevel or cwd) + "\n" + normalized origin URL or "")[:16]`. Computed by the core and never taken from model output. Moving a repo creates a new id; P11 adds a `vikhyath project relink` command.
2. **Two state roots per project, nothing global and mutable:**
   - `<project>/.vikhyath/`: **project-owned**, compact, human-reviewable: `state.yaml`, `plan-index.yaml`, `decisions.yaml`, `verification.yaml`. May be committed by the user (Q-2).
   - `$VIKHYATH_HOME/projects/<project_id>/`: **regenerable, machine-local**: Graphify output (`GRAPHIFY_OUT`), context cache, event log, session records, dashboard snapshot.
3. **No "current project" singleton.** Every core API takes an explicit `ProjectContext`. Sessions live at `$VIKHYATH_HOME/projects/<id>/sessions/<session_id>.yaml`. Concurrent sessions on different projects never share a writable file.
4. **Path guard.** The context engine refuses to load any file outside `<project root>`, the OS bundle, or `$VIKHYATH_HOME/projects/<same id>/`. Cross-project reads raise an isolation error and emit an event.
5. **Cache keys include `project_id`**, so a cache hit can never cross projects.
6. **Credentials.** Never stored in project state, caches, events or dashboards (§78). Integration secrets stay in the user's environment.
7. **Atomic writes** (temp file + rename) and per-project file locks for concurrent sessions on the same project.

## Acceptance tests (P11)

- Three fixture projects (A, B, C) with distinct decisions/design systems. Interleaved sessions; assert that no file of B or C is read while routing a request in A (load log), and that each project's state hashes change only through its own sessions.
- Same-project concurrency: two sessions writing `state.yaml` concurrently. No lost update (lock) and no partial file (atomic rename).
- Cache poisoning: identical request text in A and B produces different cache keys.
- Relink: moving project A updates the id mapping without merging into another project.
