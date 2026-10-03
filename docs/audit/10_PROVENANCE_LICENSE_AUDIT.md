# 10 — Provenance & License Audit (Phase 1)

**Licenses never block or narrow extraction (D-002).** This document is an inventory so that P5 can copy each upstream's license and notice files verbatim next to bundled content.

| Repo | Pin | License | License/notice files to carry | Notes |
|---|---|---|---|---|
| ECC | `ef648e0` | MIT, © 2026 Affaan Mustafa | `LICENSE` | — |
| Addy | `a06bc63` | MIT, © 2025 Addy Osmani | `LICENSE` | — |
| Agency | `d3f71c4` | MIT, © 2025 AgentLand Contributors | `LICENSE` | — |
| gstack | `74512c2` | MIT, © 2026 Garry Tan | `LICENSE`, `NOTICE.md`, `licenses/Apache-2.0.txt` | Some design-catalog material derives from Apache-2.0 *impeccable* (per NOTICE.md). |
| Karpathy | `2c60614` | MIT (declared in `plugin.json`, SKILL frontmatter, README) | none exists | No license text upstream (L-1). P5 records the declaration and source URL as attribution. |
| Unlazy | `1667149` | MIT, © 2026 Leonxlnx | `LICENSE` | — |
| Ponytail | `c982cd4` | MIT, © 2026 DietrichGebert | `LICENSE` | — |
| Graphify | `0b60d47` | Apache-2.0 (+ MIT for earlier portions) | `LICENSE`, `LICENSE-MIT`, `NOTICE` | — |
| OpenDesign | `53231d4` | Apache-2.0 | `LICENSE` | — |
| Taste | `ce26fc2` | MIT, © 2026 Leonxlnx | `LICENSE` | — |
| UI/UX Pro Max | `09170ee` | MIT, © 2024 Next Level Builder | `LICENSE` | Also ships `data/data-provenance.json`, `google-font-licenses.json` (data provenance; carry with data). |
| Brag | `cb89b9f` | MIT, © 2026 Shunit Haviv Hakimi | `LICENSE` | 16 MB bundled assets (music/fonts): asset provenance to be recorded in P5. |
| Agent Beacon | `5937da1` | MIT, © 2026 Asymptote Labs | `LICENSE` | — |
| BeyondSEO | `c160b9d` | MIT, © 2026 Muhammad Tahir Ashraf | `LICENSE`, `THIRD_PARTY_NOTICES.md` | `docs/source-catalog-provenance.json` (backlink source provenance). |

Provenance fields the P5 manifest must record per bundled file (spec §36): repository, commit_sha, source_path, destination_path, domain, subdomain, capability, license, attribution, integration_type, original_hash (git blob SHA-1 from [upstream-file-hashes](evidence/upstream-file-hashes/)), bundled_hash, dependencies, runtime, last_verified, update_status.
