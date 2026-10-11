# P24 evidence — update & rollback (2026-10-11)

Real bundles (scratch `VIKHYATH_HOME`): `vikhyath bundle list` → 5 known-good bundles, current `495f026f381e`.
- `vikhyath gc --dry-run` → keep `2d1356913230` (previous), `495f026f381e` (current); would remove `68fcabbc8e1b`, `6fa028f7d9d3`, `cb0635dbf824` and runtimes `graphify-1decefa25e1b`, `graphify-e69effb8c551` (no kept bundle uses them).
- `vikhyath rollback` → from `495f026f381e` to `2d1356913230`; `vikhyath rollback --to 495f026f381e` → back.

Tests (`tests/update/test_update.py`, offline fixture upstream): good update activated with `previous` kept and the new pin stored in the bundle's `evidence/`; removal of a linked reference file → `failed: dangling reference after update: skills/x/SKILL.md -> skills/x/references/r.md`, current unchanged; KeyboardInterrupt during the build → current unchanged and verifies intact; `main` instead of a SHA and an unknown upstream rejected; rollback refuses a tampered bundle; gc keeps current/previous/2 newest, removes the old bundle and an orphaned runtime.

`python -m unittest discover -s tests`: **242 OK, 3 skipped**.
