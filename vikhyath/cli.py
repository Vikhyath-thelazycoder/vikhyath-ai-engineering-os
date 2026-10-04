"""`vikhyath` command line: the single entry point every host adapter calls (D-009)."""
import argparse
import sys
from pathlib import Path

from . import __version__
from .paths import repo_root

# Subcommands planned in docs/plan/FILE_LEVEL_PLAN.md and the phase that delivers each.
PLANNED = {
    "bootstrap": "P9", "context": "P9", "state": "P10", "plan": "P10", "decide": "P10",
    "project": "P10", "verify": "P15", "test": "P15", "update": "P24", "rollback": "P24",
    "runtime": "P12", "dashboard": "P23", "adapters": "P19",
}


def _root(args) -> Path:
    return Path(args.root).resolve() if args.root else repo_root()


def _doctor(args):
    from .diagnostics.doctor import run
    return run(_root(args))


def _validate(args):
    from .diagnostics.validate import run
    return run(_root(args), online=args.online, unittests=not args.no_unittest)


def _benchmark(args):
    from .diagnostics.benchmark import run
    return run(plugins_root=Path(args.plugins_root).expanduser() if args.plugins_root else None)


def _bundle(args):
    import json

    from .bundle import build as bundle_build
    from .paths import vikhyath_home
    home = vikhyath_home()
    if args.bundle_cmd == "fetch":
        from .bundle.fetch import fetch
        fetch(Path(args.staging) if args.staging else home / "staging" / "upstream")
        return 0
    if args.bundle_cmd == "build":
        try:
            info = bundle_build.build(home, Path(args.staging) if args.staging else None,
                                      activate_bundle=not args.no_activate, self_test=args.self_test)
        except bundle_build.BuildError as exc:
            print(f"bundle build failed: {exc}", file=sys.stderr)
            return 1
        print(json.dumps({k: info[k] for k in ("bundle_id", "status", "counts", "error_count")}, indent=1))
        if info["status"] != "known-good":
            for err in info["errors"][:20]:
                print(f"  ✗ {err}", file=sys.stderr)
            return 1
        return 0
    if args.bundle_cmd == "verify":
        target = home / "bundles" / (args.bundle_id or "current")
        if not target.exists():
            print(f"no bundle at {target}", file=sys.stderr)
            return 1
        problems = bundle_build.verify(target.resolve())
        for p in problems[:50]:
            print(f"  ✗ {p}")
        print(f"bundle {target.resolve().name}: {'intact' if not problems else f'{len(problems)} problems'}")
        return 1 if problems else 0
    if args.bundle_cmd == "list":
        for b in bundle_build.list_bundles(home):
            print(f"{'*' if b['current'] else ' '} {b['bundle_id']}  {b['status']:10}  {b['created']}")
        return 0
    return 2


def _registry(args):
    import yaml

    from .paths import bundles_dir, current_bundle
    from .registry import generate, loader
    bundle = (bundles_dir() / args.bundle_id).resolve() if getattr(args, "bundle_id", None) else current_bundle()
    if args.registry_cmd == "check":
        problems = generate.check(bundle_dir=None if args.no_bundle else bundle)
        for p in problems[:50]:
            print(f"  ✗ {p}")
        where = f" + bundle {bundle.name}" if bundle and not args.no_bundle else ""
        print(f"registry ({len(loader.load_cards())} capabilities{where}): "
              f"{'valid' if not problems else f'{len(problems)} problems'}")
        return 1 if problems else 0
    if args.registry_cmd == "cards":
        changed = generate.write_card_docs()
        print(f"CARD.md rendered: {len(changed)} changed")
        return 0
    if args.registry_cmd == "build":
        if bundle is None or not (bundle / "provenance.json").is_file():
            print("no built bundle (run `vikhyath bundle build` first)", file=sys.stderr)
            return 1
        reg = generate.write_registry(bundle)
        print(f"registry.yaml written for bundle {bundle.name}: {len(reg['capabilities'])} capabilities")
        return 0
    reg = (generate.load_registry(bundle) if bundle else None) or generate.plan_registry()
    if args.registry_cmd == "list":
        for cid, e in reg["capabilities"].items():
            mode = e["activation_conditions"]["mode"]
            print(f"{cid:36} {mode:14} p{e['priority']:<3} {e['token_cost_estimate']['bundled_files']:>4} files"
                  f"{'' if e['enabled'] else '  DISABLED'}")
        print(f"source: {reg['source']}{' ' + reg['bundle_id'] if reg.get('bundle_id') else ''}")
        return 0
    if args.registry_cmd == "show":
        entry = reg["capabilities"].get(args.capability)
        if entry is None:
            print(f"unknown capability {args.capability}", file=sys.stderr)
            return 1
        if not args.paths:
            entry = dict(entry, source_paths={r: f"{len(p)} files" for r, p in entry["source_paths"].items()})
        print(yaml.safe_dump({args.capability: entry}, sort_keys=False, allow_unicode=True, width=120), end="")
        return 0
    return 2


def _route(args):
    import json

    from .routing import ProjectFacts, Router, RoutingError
    stage = "new" if args.new else "existing" if args.existing else "unknown"
    try:
        result = Router().route(" ".join(args.request), paths=args.paths or (), requested=args.capability or (),
                                project=ProjectFacts(stage=stage, stack=tuple(args.stack or ())))
    except RoutingError as exc:
        print(f"vikhyath route: {exc}", file=sys.stderr)
        return 2
    if args.brief:
        caps = ", ".join(c["id"] for c in result["capabilities"]) or "—"
        deps = ", ".join(d["id"] for d in result["dependencies"])
        print(f"{result['change_type']} · {result['confidence']} ({result['method']}) · {caps}"
              + (f" + deps: {deps}" if deps else ""))
    else:
        print(json.dumps(result, indent=1, ensure_ascii=False))
    return 0


def build_parser():
    parser = argparse.ArgumentParser(prog="vikhyath", description="Vikhyath AI Engineering OS")
    parser.add_argument("-v", "--version", action="version", version=f"vikhyath-ai-engineering-os v{__version__}")
    sub = parser.add_subparsers(dest="command")

    for name, func, helptext in (("doctor", _doctor, "Check plugin structure, manifests, environment and no-MCP"),
                                 ("validate", _validate, "Run the validation suite")):
        p = sub.add_parser(name, help=helptext)
        p.add_argument("--root", help="Repository root to check (default: this package's repo)")
        p.set_defaults(func=func)
        if name == "validate":
            p.add_argument("--online", action="store_true", help="Verify pinned SHAs against GitHub")
            p.add_argument("--no-unittest", action="store_true", help="Skip running the unit test suite")

    p = sub.add_parser("benchmark", help="Measure the always-loaded context of installed host plugins")
    p.add_argument("--baseline", action="store_true", help="Old-model baseline (default, currently the only mode)")
    p.add_argument("--plugins-root", help="Claude Code plugins dir (default: ~/.claude/plugins)")
    p.set_defaults(func=_benchmark)

    p = sub.add_parser("bundle", help="Fetch pinned upstreams, build/verify/list the local capability bundle")
    bsub = p.add_subparsers(dest="bundle_cmd", required=True)
    b = bsub.add_parser("fetch", help="Clone the 14 pinned upstreams (network; explicit, D-023)")
    b.add_argument("--staging", help="Destination (default: $VIKHYATH_HOME/staging/upstream)")
    b = bsub.add_parser("build", help="Build the bundle from staged upstreams")
    b.add_argument("--staging", help="Staged upstream snapshots (default: repo .staging/ or $VIKHYATH_HOME/staging)")
    b.add_argument("--no-activate", action="store_true", help="Build without switching `current`")
    b.add_argument("--self-test", action="store_true", help="Run bundled runtime self-tests (Unlazy, UI/UX Pro Max)")
    b = bsub.add_parser("verify", help="Re-hash a bundle against its provenance")
    b.add_argument("bundle_id", nargs="?", help="Bundle id (default: current)")
    bsub.add_parser("list", help="List built bundles")
    p.set_defaults(func=_bundle)

    p = sub.add_parser("registry", help="Check, generate and inspect the capability registry")
    rsub = p.add_subparsers(dest="registry_cmd", required=True)
    r = rsub.add_parser("check", help="Validate cards, CARD.md and the generated registry (and the current bundle's)")
    r.add_argument("--no-bundle", action="store_true", help="Check the repository only, ignore any built bundle")
    rsub.add_parser("cards", help="Render every CARD.md from its card.yaml")
    r = rsub.add_parser("build", help="(Re)generate registry.yaml for a built bundle")
    r.add_argument("bundle_id", nargs="?", help="Bundle id (default: current)")
    rsub.add_parser("list", help="List capabilities (current bundle's registry, else the extraction plan)")
    r = rsub.add_parser("show", help="Show one capability's registry entry")
    r.add_argument("capability", help="Capability id, e.g. engineering/security")
    r.add_argument("--paths", action="store_true", help="List every source path instead of counts")
    p.set_defaults(func=_registry)

    p = sub.add_parser("route", help="Route a request to capabilities (deterministic; JSON output)")
    p.add_argument("request", nargs="+", help="The user request text")
    p.add_argument("--paths", nargs="*", help="Files the request touches (path rules, spec §15)")
    p.add_argument("--capability", action="append", help="Force-include a capability the user named explicitly")
    stage = p.add_mutually_exclusive_group()
    stage.add_argument("--new", action="store_true", help="Treat the project as new (requirements first)")
    stage.add_argument("--existing", action="store_true", help="Treat the project as existing (codebase first)")
    p.add_argument("--stack", nargs="*", help="Detected stack, e.g. python django (selects stack packs)")
    p.add_argument("--brief", action="store_true", help="One-line summary instead of JSON")
    p.set_defaults(func=_route)

    for name, phase in PLANNED.items():
        p = sub.add_parser(name, help=f"(available in {phase})")
        p.add_argument("args", nargs=argparse.REMAINDER, help=argparse.SUPPRESS)
        p.set_defaults(func=lambda args, n=name, ph=phase: _not_yet(n, ph))
    return parser


def _not_yet(name, phase):
    print(f"vikhyath {name}: not implemented yet (planned for {phase}).", file=sys.stderr)
    return 2


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "func", None):
        parser.print_help()
        return 0
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
