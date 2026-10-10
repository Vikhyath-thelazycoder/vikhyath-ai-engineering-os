# P15 evidence — local test-first verification (2026-10-10)

- Fixture (payment webhook, `tests/verify/test_verify.py`): `vikhyath verify --plan --paths app/webhook.py` → unittest narrowed to `tests.test_webhook` (api), `tests.test_webhook_signature` (security), `tests.test_webhook_idempotency` (idempotency), `tests.integration.test_payment_flow` (integration), `tests.security.test_webhook_auth` (security); `tests.test_reports` not selected; build check (`compileall`) added.
- Run: PASSED, unittest `passed=5 failed=0`; evidence JSON validated (command, exit_code, result, at, counts); all subprocess commands recorded — none contains chrome/playwright/puppeteer/screenshot/browser.
- Broken `charge()` → FAILED, `failed=5`, rerun FAILED (not flaky), diagnosis lines include the AssertionError.
- Missing tool → BLOCKED; `npx chrome-devtools …` refused; "looks correct in the screenshot" evidence rejected.
- `vikhyath verify exception --reason "drag-and-drop feel needs a human"` → recorded in the project's `.vikhyath/verification.yaml`, `subprocess.run` never called; without `--reason` → exit 2.
- `vikhyath test --task T-1.1` → state `verification.last = PASSED T-1.1` with the evidence path.
- This repository: `vikhyath verify --paths vikhyath/verify/select.py` (structural impact) → 13 impacted test modules + build, **PASSED in 2.9 s**; the first run caught a real failing assertion in the new test, fixed before commit.
- `python -m unittest discover -s tests`: **209 OK, 3 skipped**; doctor 46/0; validate 22/0.
