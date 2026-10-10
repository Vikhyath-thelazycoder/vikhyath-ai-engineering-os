---
name: vikhyath-engineering
description: Engineering work (features, fixes, refactors, migrations) through the Vikhyath OS lifecycle — route, understand, plan, implement, test, verify, reconcile — with only the routed engineering capabilities loaded.
---

# Vikhyath Engineering

The OS decides which engineering guidance applies; this skill only tells you how to follow it.

1. **Route:** `vikhyath route "<request>" --paths <files…>`. Load only what it selects:
   `vikhyath context <capability-id>…`.
2. **Follow `lifecycle`** from the route result (`config/lifecycle.yaml`), step by step, running each step's
   commands and meeting its `exit` before moving on:
   UNDERSTAND (`vikhyath codebase affected`, `vikhyath plan locate`) → PLAN (`vikhyath plan reconcile`) →
   IMPLEMENT → TEST → VERIFY (`vikhyath verify`) → RECONCILE (`vikhyath plan set-status … --evidence …`).
   Bug fixes start with a failing regression test; refactors keep tests green before and after.
3. **Substantial work** (several files or deliverables): write `GATES.md` first and use
   `vikhyath gates lint|check GATES.md` (Unlazy completion discipline).
4. **Done** means VERIFIED with recorded evidence — never "should work".

Rules: guidance order is the route's `capabilities` order (user requirements → project security → architecture
→ methodology → specialists → review → simplicity). Verify locally (tests, types, lint, build); never by browser
or screenshot. Simplicity review only when the user asks for it.
