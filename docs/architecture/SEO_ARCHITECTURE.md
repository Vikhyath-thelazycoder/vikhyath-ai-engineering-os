# SEO, media and other runtimes

Engines run in isolated environments under `~/.agylite/runtimes/<name>-<lock>/`, started per command. The lock is a
hash of the bundled code and dependency pins, so documentation changes do not force a reinstall.

| Runtime | Install | Commands | Notes |
|---|---|---|---|
| Graphify (code graph) | `agylite runtime install graphify` | `agylite codebase affected\|update\|query\|path\|explain` | Graph in `~/.agylite/projects/<id>/graph`; hook/install/watch/serve/extract blocked; no MCP script; without it, a structural fallback is used and stated |
| BeyondSEO | `agylite runtime install seo [--browser] [--reports]` | `agylite seo run <cmd>`, `agylite seo evidence <run>`, `agylite seo authorize` | Core install has no browser; `watch` blocked; output in the project's data dir |
| UI/UX Pro Max | none (standard library) | `agylite design search\|system\|check` | `--persist` writes only `design-system/` in the project |
| Unlazy | Node | `agylite gates status\|check\|approve\|reverify\|lint` | Stop hook only via `agylite runtime unlazy-hook --enable` (global settings) |
| Brag | none; music analyser via `agylite runtime install brag` | `agylite media plan [--full]`, `agylite media music-cues <audio>` | brag-slim by default; full /brag only with a locally installed Hyperframes |

`agylite runtime status` reports each one (ready, not-installed, broken, no-bundle).

## SEO evidence

Every SEO claim gets one label from BeyondSEO's own capture quality: FACT (complete capture), OBSERVATION (seen in a
partial capture), INFERENCE (derived from observations), HYPOTHESIS (prediction or no basis), UNKNOWN (could not be
inspected). A failed or partial capture never supports an absence claim.

## Live websites

`edit apply` and `edit rollback` write to real sites over FTP/SFTP. They require
`agylite seo authorize --site <site> --task <T-id> --reason "…"` and `--authorization <id>`: per project, expiring after
two hours by default, each use logged, no credentials stored.
