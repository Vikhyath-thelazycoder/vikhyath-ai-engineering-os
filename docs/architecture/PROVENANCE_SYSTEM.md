# Provenance

Every bundled file has a record in the bundle's `provenance.json`:

repository · commit SHA · source path · destination path · domain/subdomain · capability · license · attribution ·
integration type (COPY/ADAPT/PRESERVE) · original hash (git blob SHA-1, as audited) · bundled hash (SHA-256) ·
runtime · last verified · update status.

- Pins: `docs/audit/evidence/upstream-staging-snapshot.yaml` (40-character SHAs only). A bundle built by
  `agylite update` stores its own pins and inventories in `<bundle>/evidence/`.
- Licenses: `third_party/licenses.json` (machine-readable) and the generated `THIRD_PARTY_NOTICES.md`; each bundle
  carries `third_party/<repo>/` with the upstream license and notice files (13 MIT, 2 Apache-2.0).
- `agylite bundle verify` re-hashes every file against its record; `agylite registry show <id> --paths` lists a
  capability's sources.
