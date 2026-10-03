# 16 — Update & Rollback Audit (Phase 3, spec §41–42)

## Current state

v1.0.1: `scripts/validate --online` only checks that pinned SHAs exist on GitHub. There is no update, no rebuild and no rollback.

Upstream update mechanisms are all **excluded** because they update silently or mutate the host: `gstack-update-check`/`gstack-upgrade`, UI/UX Pro Max `cli update`, ECC `install-apply.js`, Agency `install.sh`, BeyondSEO `install_skill.py`, Graphify `install`.

## Design (P24)

```
$VIKHYATH_HOME/bundles/
  <bundle_id>/                 bundle_id = sha256(pins + rules + transforms)[:12]
    blobs/<sha256>             content-addressed files (dedup, spec §37)
    index.json                 capability -> [{dest_path, blob, source repo/path/commit}]
    provenance.json            spec §36 fields per file
    registry.yaml              generated capability registry for this bundle
    runtimes.lock              pinned runtime deps (graphify, beyondseo, brag)
    BUILD.json                 build time, test results, status=known-good|failed
  current -> <bundle_id>       atomic pointer (symlink; JSON pointer file on Windows)
  previous -> <bundle_id>      last known-good
```

`vikhyath update [--repo X] [--to <sha|tag>]` (explicit only, never automatic):

1. Fetch the upstream(s) into `.staging/` (network, user-initiated).
2. Resolve the target commit; compare with the current pin; list changed paths (`git diff --stat old..new`).
3. Re-run `scan_upstream.py` and `extraction_matrix.py`. **Stop if the closure check or rule validation fails** (new files that no rule covers fall to defaults and are reported).
4. Build a new bundle dir (never mutate the current one) and regenerate provenance + registry.
5. Run compatibility tests: registry schema, routing scenario tests, runtime self-tests for changed runtimes (Unlazy/UI-UX/Graphify/BeyondSEO suites), unit + integration tests.
6. Report the changes (capabilities affected, files added/removed, test deltas).
7. Swap `current` atomically **only if all checks pass**; keep `previous`.

`vikhyath rollback [--to <bundle_id>]`: repoint `current` to `previous` (or a named known-good bundle). Bundle files, registry, provenance and runtime lock all switch together because they live in one directory. Runtimes are versioned per bundle (`runtimes/<name>-<lockhash>/`), so a rollback also restores the matching venv.

Retention: keep the current, previous and two most recent failed builds (for diagnosis); `vikhyath gc` removes the rest.

## Acceptance (P24)

- Simulated broken update: a fixture upstream commit that removes a file referenced by a bundled skill → closure check fails → `current` unchanged.
- A forced bad bundle marked current → `rollback` restores the previous one; `doctor` passes.
- An interrupted update (kill mid-build) leaves `current` untouched.
- No network access during normal commands (`route`, `context`, `doctor --offline`); verified with network disabled.
