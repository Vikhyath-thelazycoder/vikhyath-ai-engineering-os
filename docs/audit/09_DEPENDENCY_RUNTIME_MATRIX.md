# 09 — Dependency & Runtime Matrix (Phase 2)

Each runtime starts only when a selected capability needs it (spec §2.5); nothing runs in the background.

| Runtime | Capabilities | Dependencies | Isolation | Verified in this audit | Start / stop | Network |
|---|---|---|---|---|---|---|
| **OS core** | router, registry, context, state, events, diagnostics | Python 3 + PyYAML (to be declared in P4; E-1) | Central install (venv owned by the OS) | Python 3.14.7 present; PyYAML only in scratch venv today | Per command invocation | None |
| **Node ≥16** | `engineering/completion`, `testing/release-verification` (Unlazy gate checker), ECC eval-harness / package-manager detection / codemaps | Zero npm deps for Unlazy; ECC scripts use Node stdlib (+ `npx tsx` for codemaps) | System Node | Node 22.14.0; Unlazy suite 188 ok | Per gate check; Stop hook only when registered by the OS (opt-in) | None |
| **Graphify** | `codebase/*` | `networkx`, `numpy`, `rapidfuzz`, `tree-sitter` + ~25 grammar wheels; optional extras **not installed** (mcp, neo4j, llm providers, watchdog, …) | **Dedicated venv** (151 MB) | `pip install .` 15 s; `update` 1.5 s; `query` OK | Per command; `GRAPHIFY_OUT` → OS per-project state; `hook`/`install`/`watch`/`serve` blocked by the wrapper | None (AST mode); LLM extraction opt-in only (SEC-09) |
| **BeyondSEO** | `seo/*` | Core: `beautifulsoup4`, `colorama`. Extras on demand: `browser` (Playwright + Chromium), `reports` (reportlab), `sftp` (paramiko) | **Dedicated venv** | `pip install -e .`; CLI 22 subcommands; tests 232/250 core-only; **250/250 OK (6 skipped) with `.[browser]` + Chromium** | Per command; Chromium only via explicit `browser-setup` | Required for crawls/research (SEO tasks only) |
| **UI/UX Pro Max engine** | `design/design-system` (+ design skills that query it) | Python 3 **stdlib only** | Runs under the OS Python; no venv needed | 164/164 tests; offline query OK | Per query | None |
| **Brag** | `media/launch-video` | `/brag-slim`: tools already on the machine (ffmpeg expected, UNKNOWN until P17). `/brag`: Python ≥3.11 via **uv** with `librosa`, `numpy`, `scipy`, `soundfile`; **Hyperframes** via `npx` (+ headless browser for render) | Dedicated uv env for the music-cue script | Not executed in P1/P2 (scheduled for P17) | Per video job | `/brag`: npx download on first use (SEC-13); `/brag-slim`: none required |
| **Playwright (optional)** | `testing/browser-fallback`, `media/demo`, BeyondSEO rendering | Playwright + Chromium (+ headless shell, ffmpeg): **557 MB** measured | Inside the runtime that needs it (SEO venv or a testing venv); browsers in `$VIKHYATH_HOME/runtimes/playwright-browsers` | Installed in the isolated SEO venv during P3; BeyondSEO browser tests pass | Lazy, bounded, terminated after the task (§23A.9) | Local targets by default |
| ~~AgentShield~~ | ECC `security-scan` **excluded in P3** (UNAUDITED_DEPENDENCY: external `ecc-agentshield` npm package) | — | — | Resolved | — | — |

## Python version compatibility

All Python runtimes exercised in this audit ran on **Python 3.14.7**. Declared floors: Graphify ≥3.10, BeyondSEO ≥3.10, Brag script ≥3.11, UI/UX Pro Max stdlib. P4 sets the OS floor at **≥3.10**, the strictest common floor among the runtimes it hosts directly.

## UNKNOWN items (BeyondSEO browser extra and AgentShield resolved in P3)

| Item | Why unknown | How to verify | Impact |
|---|---|---|---|
| Brag runtime (ffmpeg, Hyperframes version) | Not executed | Dry-run `/brag-slim` on a fixture project in P17 | Media domain readiness |
| Graphify full test suite | Only smoke-tested | Run `pytest` in the isolated venv in P12 | Runtime confidence |
