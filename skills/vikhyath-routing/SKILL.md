---
name: vikhyath-routing
description: Route a task to the minimum Vikhyath OS capabilities with the deterministic `vikhyath route` command, then load only their context.
---

# Vikhyath Routing

Routing is done by the OS core, not by reading this file. Do not pick capabilities by hand and do not load every skill.

## Steps

1. **Route.** Run, from the project directory:

   ```bash
   vikhyath route "<the user's request>" --brief          # one line
   vikhyath route "<the user's request>"                  # full JSON
   ```

   Add `--paths <files…>` when the request touches known files, `--new` / `--existing` when the project stage is
   known, and `--capability <id>` only when the user explicitly names a capability.

2. **Load context for the routed capabilities only** (levels L1 → L2; L3 only when needed):

   ```bash
   vikhyath context <capability-id>…
   ```

3. **Follow the result.**
   - `capabilities` are listed in guidance order (`config/priorities.yaml`: user requirements → project security →
     project architecture → methodology → specialists → review → simplicity). On conflicting advice, the earlier one wins.
   - `dependencies` are internal capabilities the selected ones need; use them through those capabilities.
   - `fallbacks` apply only when the primary capability cannot decide (e.g. browser fallback after deterministic checks).
   - `browser`: `none` → no browser; `fallback-only` → deterministic checks first; `explicit-visual` → the user asked
     to see the page.
   - `pipeline` gives the domain order for multi-domain work (e.g. SEO audit → engineering → testing).
   - `confidence: low` (BM25 fallback) or `none`: confirm the intent with the user before acting.

## Rules

- Simplicity review (Ponytail-derived) runs only when the user asks for it.
- New projects start with requirements; existing projects start with codebase understanding (spec §19.2).
- Never activate SEO, media or design capabilities the route did not select.
