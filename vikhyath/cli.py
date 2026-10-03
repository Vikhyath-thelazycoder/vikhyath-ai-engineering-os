"""`vikhyath` command line: the single entry point every host adapter calls (D-009)."""
import argparse
import sys
from pathlib import Path

from . import __version__
from .paths import repo_root

# Subcommands planned in docs/plan/FILE_LEVEL_PLAN.md and the phase that delivers each.
PLANNED = {
    "bootstrap": "P9", "route": "P8", "context": "P9", "state": "P10", "plan": "P10", "decide": "P10",
    "project": "P10", "verify": "P15", "test": "P15", "bundle": "P6", "update": "P24", "rollback": "P24",
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
