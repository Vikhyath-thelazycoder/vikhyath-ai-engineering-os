---
name: vikhyath-security
description: Security-sensitive changes (auth, secrets, payments/webhooks, input handling, OWASP) — route to engineering/security and testing/security and prove fixes with negative tests run locally.
---

# Vikhyath Security

1. **Route:** `vikhyath route "<request>" --paths <files…>`; security work selects `engineering/security` (project
   security outranks every methodology) and `testing/security`. Load them with `vikhyath context <id>…`.
2. **Understand the surface:** `vikhyath codebase affected --paths <files…>`; check recorded security decisions
   with `vikhyath decide list --kind security`.
3. **Fix with negative tests** (lifecycle rule for SECURITY_CHANGE): forged/expired signatures rejected,
   unauthorised access denied, injection inputs neutralised, secrets never logged. Each test must fail without the fix.
4. **Verify locally:** `vikhyath verify` (tests + dependency audit + secret scan where available); record the
   evidence. Record new security rules as decisions: `vikhyath decide add --kind security …`.

Never paste real secrets into prompts, logs or evidence. No browser or screenshot verification.

Verification policy: local test-first (`config/verification.yaml`) — no browser, Chrome DevTools, screenshots or MCP.
