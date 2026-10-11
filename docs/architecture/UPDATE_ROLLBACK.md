# Update and rollback

Upstreams never update themselves. Updates are explicit, checked and reversible.

```bash
agylite update <repo> <40-char commit sha> [--source DIR] [--self-test]
agylite rollback [--to <bundle id>]
agylite gc [--dry-run]
```

**update** — copy the current evidence, take the new commit's inventory (blob hashes) and pin, diff it (bundled paths
and capabilities affected), refuse it if a bundled file still references a path the commit removed, build a new bundle
beside the current one, verify its integrity and registry (and runtime self-tests with `--self-test`), and switch
`current` only if everything passes. `previous` keeps the old bundle. A failed or interrupted update leaves `current`
untouched. History: `~/.agylite/updates/history.jsonl`; event UPSTREAM_UPDATED.

**rollback** — switches to `previous` or a named bundle, only if it is known-good and re-hashes intact. Files,
registry, provenance and the runtime locks derived from them change together. Event UPSTREAM_ROLLBACK.

**gc** — keeps `current`, `previous` and the two newest failed builds; removes other bundles, runtimes that no kept
bundle uses, and leftovers of interrupted builds.

Tags and branches are refused because they move; pin a commit.
