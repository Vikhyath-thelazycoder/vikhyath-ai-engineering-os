---
name: vikhyath-production
description: Release readiness — plan completion, verification evidence, changelog and rollback — through engineering/release and testing/release-verification.
---

# Vikhyath Production

1. **Route:** `vikhyath route "prepare the release" --paths <files…>` → `engineering/release`,
   `testing/release-verification`; load with `vikhyath context <id>…`.
2. **Plan completion:** every task the release claims is VERIFIED with evidence (`vikhyath plan show <phase>`);
   PARTIAL or unverified items block the release unless the user accepts the risk
   (`vikhyath decide add --kind process --topic "risk acceptance" …`).
3. **Verify:** `vikhyath verify` on the release candidate — tests, types, lint, build, security checks — with the
   evidence file recorded.
4. **Ship notes:** changelog from the commit list; migration and rollback steps written before deploying.

No deploy step is taken without the user's explicit go-ahead. No browser or screenshot verification.

Verification policy: local test-first (`config/verification.yaml`) — no browser, Chrome DevTools, screenshots or MCP.
