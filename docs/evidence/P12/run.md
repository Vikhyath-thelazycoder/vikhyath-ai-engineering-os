# P12 evidence — codebase domain (Graphify) (2026-10-10)

Interpreter: `Python 3.14.7`. `<scratch>` = session scratch `VIKHYATH_HOME`. Graphify `0.9.74` (pin `0b60d47`).

## What was built
- `vikhyath/runtimes/graphify.py`: install from the active bundle's `files/graphify` into `runtimes/graphify-<lock>/venv` (core dependencies only; built in place, `runtime.json` written last; `graphify-mcp` script removed); `health()` → ready / not-installed / broken / no-bundle; per-project `GRAPHIFY_OUT=$VIKHYATH_HOME/projects/<id>/graph`; allowlist `update/query/path/explain/affected`; reserved `--graph/--out/--output/--memory-dir`; secret-named env vars and `PYTHONPATH` dropped; graph rebuilt only on a code fingerprint change, under the project's `graph` lock.
- `vikhyath/runtimes/graphify_probe.py`: runs inside the venv (`python -I`), uses `graphify.affected.resolve_seed/affected_nodes` → JSON.
- `vikhyath/codebase/impact.py` + `structural.py`: changed paths (default `git status`) → affected files + related tests (graph importers + test-name matches; `__init__.py`/`conftest.py` are support, not tests) → `code_files_per_task` (12) limit with `omitted`; `unknown` for deleted/outside/unresolved paths; §74 fallback (Python `ast`, relative JS/TS imports) with the notice.
- CLI: `vikhyath runtime status|install graphify`, `vikhyath codebase affected|update|query|path|explain`. Router: `impact` step (schema v3). Doctor: "Runtimes" section. Skill: `skills/vikhyath-codebase/SKILL.md`.
- D-037: `graphify/serve.py` EXCLUDE → PRESERVE (`query/path/explain` import its search helpers).

## Bundle
- `vikhyath bundle build --self-test` (rules + notices changed): **`68fcabbc8e1b` known-good, 2,584 files (+1 `serve.py`), 0 errors**; Unlazy + UI/UX Pro Max self-tests exit 0; `bundle verify`: intact; `registry check`: 63 capabilities + bundle, valid. Before the rule change, the build reproduced the A-1 id `cb0635dbf824`.
- Notices regenerated: 15 upstreams (13 MIT, 2 Apache-2.0); Graphify bundled count +1.

## Runtime
- `vikhyath runtime install graphify` from the bundle: **5.8 s**, lock `1decefa25e1b`, `graphify 0.9.74`; `runtime status`: ready. `import mcp` in the venv → `ModuleNotFoundError`; no `graphify-mcp` script.
- `bundle verify` after the install: intact (pip builds from a temporary copy).
- Found while running the bundled runtime (not the staged upstream): `codebase query/explain/path` failed with `No module named 'graphify.serve'` → D-037. The real-runtime tests now accept `VIKHYATH_TEST_BUNDLE` so they run against what users get.
- Runtime lock first covered only `pyproject.toml`/`uv.lock`, so the old venv was reused after the rule change; the lock now includes the sha256 of every bundled Graphify file (from `index.json`).

## This repository (real graph)
`vikhyath codebase affected --paths vikhyath/context/budget.py`:

| Run | Method | Graph | Files | Tests | Time |
|---|---|---|---|---|---|
| 1st | graph | rebuilt: 1,826 nodes, 3,470 edges, `update` 3,162 ms | 9 (0 omitted) | 12 (+12 omitted) | 3,320 ms |
| 2nd | graph | not rebuilt (fingerprint equal) | 9 | 12 (+12 omitted) | 155 ms |
| `--structural` | structural (§74 notice) | — | 8 | 10 | 130 ms |

Graph files: `budget.py`, `cli.py`, `codebase/impact.py`, `context/levels.py`, `routing/router.py`, `__main__.py`, `codebase/__init__.py`, `diagnostics/validate.py`, `routing/__init__.py`. `git status` before/after: only the P12 source changes; no `graphify-out/`, no hooks, no `CLAUDE.md`/`AGENTS.md` edits.

- `codebase query "how is the context budget enforced" --budget 300` → 186-node scoped subgraph, truncated to 10 with Graphify's own notice, `src=file loc=L…`.
- `codebase explain load_budgets` → `vikhyath/context/budget.py L13`, degree 18.
- `codebase path Router load_budgets` → `Router --method--> .__init__() --calls--> load_budgets()`.
- `codebase hook` → rejected by the CLI; `graphify.check_command("serve")` → `GraphifyBlocked` (tests).

## Tests
`python -m unittest discover -s tests`: **184 OK, 3 skipped** (opt-in real runtime). With `VIKHYATH_RUNTIME_TESTS=1 VIKHYATH_TEST_BUNDLE=<scratch>/bundles/current`: `tests.runtimes.test_graphify` + `tests.context.test_code_surface` **19/19 OK**; against the staged upstream also 10/10.
- `test_code_surface`: 30 importers + 1 depth-2 file of `app/core.py` → 12 files, `omitted.files = 20`; related tests incl. a depth-2 test; relative Python imports; JS relative imports + `__tests__`; directory expansion; deleted and outside-project paths as `unknown`; default = `git status`; project tree unchanged; router `impact` for existing, none for new.
- `test_graphify`: blocked subcommands and reserved flags; env (`GRAPHIFY_OUT`, no API keys, no `PYTHONPATH`); lock changes with pins; health states; not-installed → fallback with notice; CLI exit codes; real runtime: health ready without MCP, graph method, tests found, graph in data dir, project unchanged, no rebuild when unchanged, `query/explain/path` exit 0.

`vikhyath doctor`: **47 passed, 0 failed** (with the runtime: "graphify 0.9.74 ready"; without it the check is a warning naming the fallback). `vikhyath validate`: **23 passed, 0 failed**.

## Upstream Graphify test suite (opt-in, doc 09/17 duty)
Graphify's own `pytest` (copy of the staged pin, scratch venv, core dependencies only, 5 min 14 s): **5,853 passed, 66 failed, 263 skipped**. The captured failure lines (the last 29) are all language extractors whose optional grammar extras the OS does not install (`terraform` → `tree-sitter-hcl`, `vbnet` → `tree-sitter-vb-dotnet`); the first `-x` run stopped on `test_erlang_extractor` (`erlang` → `tree-sitter-language-pack`). The other 37 failures were not individually captured (output was tail-limited); a per-file breakdown is a recorded follow-up for P25. None of the failing areas is used by `update/query/path/explain/affected` on the languages this repo and the fixtures use, and all OS tests pass.
