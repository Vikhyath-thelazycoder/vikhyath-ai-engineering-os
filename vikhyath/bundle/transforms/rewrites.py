"""Targeted rewrites for ADAPT files whose instructions point at excluded mechanisms.

Every rewrite must match; a non-matching pattern means the upstream text changed (rewrite drift)
and the build fails instead of shipping un-adapted instructions.
"""
import re


class RewriteDrift(ValueError):
    pass


BUNDLE = "$VIKHYATH_BUNDLE"  # expanded to the active bundle path by the context engine (P9)

# (repo, path) -> [(pattern, replacement)]
REWRITES = {
    ("unlazy", "SKILL.md"): [
        (re.compile(r"node <skill-dir>/scripts/install-hooks\.mjs"),
         "vikhyath runtime unlazy-hook --enable   # Vikhyath OS registers the Stop hook centrally, never in the project"),
    ],
    ("beyondseo", "SKILL.md"): [
        (re.compile(r"For an installation request, follow \[the host-specific guide\]\(docs/agent-installation\.md\), "
                    r"including Cursor, Lovable workspace imports and agents managing Vercel projects\."),
         "Installation and host registration are handled by Vikhyath OS (`vikhyath runtime install seo`)."),
        (re.compile(r"For Lovable execution, read \[the Lovable host guide\]\(docs/lovable\.md\)[^\n]*\n\n?"), ""),
    ],
    ("ecc", "rules/README.md"): [
        (re.compile(r"(?:^\./install\.sh [^\n]*\n)+", re.M),
         "# Vikhyath OS activates these rule packs for the detected stack; no install step is needed.\n"),
    ],
    ("uiuxpromax", ".claude/skills/ui-ux-pro-max/SKILL.md"): [
        (re.compile(r"\$\{CLAUDE_PLUGIN_ROOT\}/\.claude/skills/ui-ux-pro-max/scripts/"),
         f"{BUNDLE}/files/uiuxpromax/src/ui-ux-pro-max/scripts/"),
    ],
}


def applies(repo, path):
    return (repo, path) in REWRITES


def apply(repo, path, text):
    for pattern, replacement in REWRITES[(repo, path)]:
        text, count = pattern.subn(replacement, text)
        if count == 0:
            raise RewriteDrift(f"{repo}:{path}: pattern no longer matches upstream text: {pattern.pattern[:60]}")
    return text
