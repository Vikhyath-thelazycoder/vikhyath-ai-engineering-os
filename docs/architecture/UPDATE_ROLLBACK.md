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

## Staying current automatically (P28)

```bash
agylite update --check                 # newest commit per upstream (git ls-remote; seconds, nothing downloaded)
agylite update --latest [--due]        # apply new commits, one upstream at a time, through every check above
agylite update ecc --latest            # just one upstream
agylite update --schedule install      # optional weekly job on this Mac (Mondays 09:00); `remove` undoes it
```

- Policy per upstream in `config/upstreams.yaml`: `weekly`, `monthly`, `manual` (never automatic) or `releases`
  (newest version tag), the branch to follow, and whether to run the runtime's self-tests.
- Only new commits are downloaded: each upstream has a blobless mirror in `~/.agylite/mirrors/`; later runs fetch only
  new commits, and the update reuses the mirror's objects, downloading just the bundled files of the new commit.
- A failing upstream is skipped and reported; the others still update; `current` changes only after every check passes.
- In the repository, `.github/workflows/upstream-updates.yml` checks daily and, weekly (and monthly for monthly
  upstreams), applies new commits, runs the full test suite and benchmarks, and opens one pull request with the new
  pins. Merging it is what ships the update to everyone.
