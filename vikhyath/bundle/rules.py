"""Extraction rule engine shared by the audit matrix and the bundler (one engine, D-015).

Every upstream file receives exactly one decision: the first rule whose glob matches wins,
otherwise the repo default applies. Globs: `**` = any depth, `*` / `?` stay within one path segment.
"""
import re
from pathlib import Path

import yaml

from ..paths import repo_root

DECISIONS = {"COPY", "ADAPT", "WRAP", "REFERENCE", "PRESERVE", "EXCLUDE"}
BUNDLED = {"COPY", "ADAPT", "WRAP", "PRESERVE"}


def audit_dir() -> Path:
    return repo_root() / "tools" / "audit"


def evidence_dir() -> Path:
    return repo_root() / "docs" / "audit" / "evidence"


def glob_to_regex(pattern):
    out, i = "", 0
    while i < len(pattern):
        if pattern.startswith("**/", i):
            out += "(?:.*/)?"
            i += 3
        elif pattern.startswith("**", i):
            out += ".*"
            i += 2
        elif pattern[i] == "*":
            out += "[^/]*"
            i += 1
        elif pattern[i] == "?":
            out += "[^/]"
            i += 1
        else:
            out += re.escape(pattern[i])
            i += 1
    return re.compile("^" + out + "$")


def load_yaml(path: Path):
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_rules(path: Path | None = None):
    return load_yaml(path or audit_dir() / "extraction-rules.yaml")


def load_domain_model(path: Path | None = None):
    return load_yaml(path or audit_dir() / "domain-model.yaml")


def known_capabilities(model):
    return {f"{domain}/{sub}": meta
            for domain, d in model["domains"].items() for sub, meta in d["capabilities"].items()}


def compile_rules(rules_doc, caps):
    """Attach compiled globs to every rule; return a list of validation errors."""
    errors = []
    for repo, rr in rules_doc["repos"].items():
        for rule in rr.get("rules", []) + [rr["default"]]:
            rule["_rx"] = [glob_to_regex(p) for p in rule.get("paths", [])]
            if rule["decision"] not in DECISIONS:
                errors.append(f"{repo}: unknown decision {rule['decision']}")
            cap = rule.get("capability")
            if rule["decision"] in BUNDLED and cap not in caps:
                errors.append(f"{repo}: bundled rule without known capability: {rule.get('paths')} -> {cap}")
    return errors


def classify(repo_rules, path):
    for rule in repo_rules.get("rules", []):
        for rx in rule["_rx"]:
            if rx.match(path):
                return rule
    return repo_rules["default"]


def read_inventory(evidence: Path, repo):
    """(path, bytes, git blob sha1) for every tracked file of one upstream snapshot."""
    rows = []
    with open(evidence / "upstream-file-hashes" / f"{repo}.tsv", encoding="utf-8") as f:
        for line in f:
            if line.startswith("#") or line.startswith("blob_sha1\t"):
                continue
            sha, size, path = line.rstrip("\n").split("\t", 2)
            rows.append((path, int(size), sha))
    return rows
