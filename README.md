# Agylite

[![CI](https://github.com/Vikhyath-thelazycoder/vikhyath-ai-engineering-os/actions/workflows/ci.yml/badge.svg)](https://github.com/Vikhyath-thelazycoder/vikhyath-ai-engineering-os/actions/workflows/ci.yml)

**A light engineering OS for coding agents.** Agylite routes every request to the few capabilities it needs, loads only
their relevant sections, keeps one living plan per project, and verifies work with local tests instead of screenshots.
It runs the same way in Claude Code, Codex, Cursor and Antigravity, and uses no MCP servers.

It is built from a curated, pinned bundle of 15 open-source projects — ECC, Addy Agent Skills, Agency Agents, gstack,
Graphify, Unlazy, Ponytail, Karpathy Skills, Open Design, Taste, UI/UX Pro Max, Appllama, BeyondSEO, Brag and Beacon —
so you get their knowledge and engines without installing them as separate plugins.

## Why

Measured on the development machine (`agylite benchmark --compare`, [results](docs/benchmarks/RESULTS.md); tokens are
bytes ÷ 4 estimates):

| | Upstream plugins installed directly | Agylite |
|---|---:|---:|
| Loaded on every turn | ~31,800 tokens (ECC, Open Design, UI/UX Pro Max descriptions) | ~900 tokens |
| 22 spec tasks, total context | ~1,020,000 tokens | ~176,000 tokens (83 % less) |
| Routing | the model chooses among all descriptions | deterministic, 22/22 scenarios correct, p95 0.34 ms |

## Install

```bash
git clone https://github.com/Vikhyath-thelazycoder/vikhyath-ai-engineering-os.git
cd vikhyath-ai-engineering-os
scripts/install                                   # Python ≥ 3.10, git; builds the bundle into ~/.agylite (network once)
export PATH="$HOME/.agylite/core/bin:$PATH"
agylite doctor
```

Then add it to your host:

| Host | Command |
|---|---|
| Claude Code | `claude plugin marketplace add Vikhyath-thelazycoder/vikhyath-ai-engineering-os` · `claude plugin install agylite@agylite-marketplace` |
| Codex | `codex plugin marketplace add Vikhyath-thelazycoder/vikhyath-ai-engineering-os` · `codex plugin add agylite@agylite-marketplace` |
| Cursor | `agylite adapters install --host cursor` |
| Antigravity | `agylite adapters install --host antigravity` |

`agylite adapters status` shows each host as FILES_PRESENT, INSTALLED or RUNTIME_VERIFIED (only after the host has
actually run Agylite).

## Use

Agents follow the entry skills (`skills/agylite-*`); you can run the same commands yourself:

```bash
agylite route "Fix the payment webhook security." --brief
agylite context engineering/security testing/security
agylite codebase affected                    # files and tests your current change reaches (≤ 12 files)
agylite verify --plan && agylite verify      # impacted tests + typecheck/lint/build, evidence recorded
agylite dashboard --open                     # the Agent Office
```

| Area | Commands |
|---|---|
| Routing & context | `route`, `context`, `bootstrap` |
| Project | `project init`, `state`, `plan …`, `decide …` |
| Codebase | `codebase affected\|update\|query\|path\|explain` (Graphify) |
| Engineering | `gates …` (Unlazy acceptance gates) |
| Testing | `verify`, `test`, `verify exception --reason` |
| Design | `design search\|system\|check` (UI/UX Pro Max, design-token checks) |
| SEO | `seo run\|evidence\|authorize` (BeyondSEO) |
| Media | `media plan\|music-cues` (Brag) |
| Operations | `dashboard`, `events …`, `runtime status\|install`, `update`, `rollback`, `gc`, `bundle …`, `registry …`, `adapters …`, `doctor`, `validate`, `benchmark` |

## The Agent Office

`agylite dashboard` opens a pixel office where every capability is an agent at a desk — engineering floor, design
studio, QA lab, SEO & media, mentors & watch. Agents light up when a request routes to them, wait on dependencies, say
why they are blocked, and go idle again. It is read-only, local (127.0.0.1) and stops when idle.

## Staying current

Upstreams are pinned, never pulled blindly. `agylite update --check` shows which have new commits;
`agylite update --latest` applies them through every check (only new commits are downloaded) and switches only if all
pass; `agylite rollback` undoes it. A GitHub Action checks daily and opens a weekly pull request with checked updates;
`agylite update --schedule install` adds an optional weekly job on your Mac.

## Principles

- **Light:** a few short entry skills on every turn; everything else routed and loaded in budgeted sections.
- **Deterministic:** routing is rules, not a model call.
- **Local test-first:** done means recorded evidence from tests, types, lint and build. Browser, Chrome DevTools and
  screenshot verification are disabled ([policy](docs/architecture/VERIFICATION_POLICY.md)).
- **Nothing always-on:** no daemons, no upstream hooks; engines start per command in isolated environments.
- **Isolated projects** and **traceable files:** every bundled file records its upstream, commit, path, hash and license.

## Documentation

- [Architecture](docs/architecture/TARGET_ARCHITECTURE.md) and component docs in `docs/architecture/`
- [Migrating from v1.0.1](docs/migration/V1_TO_V2.md)
- [Benchmarks](docs/benchmarks/RESULTS.md)
- Plan and decisions: `docs/plan/IMPLEMENTATION_PLAN.md`, `docs/audit/21_AUDIT_DECISIONS.md`

## Development

```bash
python -m venv .venv && .venv/bin/pip install -e .
.venv/bin/python -m unittest discover -s tests
.venv/bin/agylite doctor && .venv/bin/agylite validate
```

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT for Agylite itself ([LICENSE](LICENSE)). Bundled upstream files keep their own licenses (13 MIT, 2 Apache-2.0);
see [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) and each bundle's `third_party/` directory.
