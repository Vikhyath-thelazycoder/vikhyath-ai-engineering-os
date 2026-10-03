"""Load capability cards: `capabilities/<domain>/<sub>/card.yaml` merged with registry and domain defaults.

Merge order (later wins): capabilities/defaults.yaml (host_compatibility) → config/priorities.yaml domain_defaults
(priority, activation mode) → the card itself.
"""
import copy
import hashlib
from pathlib import Path

import yaml

from ..paths import repo_root


class RegistryError(RuntimeError):
    pass


def capabilities_dir(root: Path | None = None) -> Path:
    return (root or repo_root()) / "capabilities"


def _yaml(path: Path):
    try:
        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except OSError as exc:
        raise RegistryError(f"cannot read {path}: {exc}") from exc


def load_defaults(root: Path | None = None):
    return _yaml(capabilities_dir(root) / "defaults.yaml")


def load_domain_defaults(root: Path | None = None):
    return _yaml((root or repo_root()) / "config" / "priorities.yaml").get("domain_defaults") or {}


def load_domains(root: Path | None = None):
    """{domain: {"purpose": str, "capabilities": [capability ids in registry order]}} in domain order."""
    base = capabilities_dir(root)
    out = {}
    for domain in load_defaults(root).get("domains") or []:
        meta = _yaml(base / domain / "domain.yaml")
        out[domain] = {"purpose": meta.get("purpose", ""),
                       "capabilities": [f"{domain}/{sub}" for sub in meta.get("capabilities") or []]}
    return out


def load_cards(root: Path | None = None):
    """Ordered {capability_id: merged card}. Identity fields are not part of the card; the path is the id."""
    base = capabilities_dir(root)
    defaults = load_defaults(root)
    domain_defaults = load_domain_defaults(root)
    cards = {}
    for domain, meta in load_domains(root).items():
        dd = domain_defaults.get(domain) or {}
        for cid in meta["capabilities"]:
            path = base / cid / "card.yaml"
            if not path.is_file():
                raise RegistryError(f"{cid}: listed in {domain}/domain.yaml but {path} is missing")
            card = _yaml(path)
            card.setdefault("host_compatibility", copy.deepcopy(defaults.get("host_compatibility") or {}))
            if "priority" in dd:
                card.setdefault("priority", dd["priority"])
            act = card.get("activation_conditions")
            if isinstance(act, dict) and "activation" in dd:
                act.setdefault("mode", dd["activation"])
            cards[cid] = card
    return cards


def structure_problems(root: Path | None = None):
    """Directories, domain lists and default-file entries must describe the same capability set."""
    base = capabilities_dir(root)
    problems = []
    domains = load_defaults(root).get("domains") or []
    on_disk = sorted(p.name for p in base.iterdir() if p.is_dir())
    if sorted(domains) != on_disk:
        problems.append(f"defaults.yaml domains {sorted(domains)} != domain directories {on_disk}")
    missing_defaults = [d for d in domains if d not in load_domain_defaults(root)]
    if missing_defaults:
        problems.append(f"config/priorities.yaml domain_defaults missing {missing_defaults}")
    for domain in domains:
        if not (base / domain / "domain.yaml").is_file():
            problems.append(f"{domain}: domain.yaml missing")
            continue
        listed = [c.split("/", 1)[1] for c in load_domains(root)[domain]["capabilities"]]
        dirs = sorted(p.name for p in (base / domain).iterdir() if p.is_dir())
        if sorted(listed) != dirs:
            problems.append(f"{domain}: domain.yaml lists {sorted(listed)} but directories are {dirs}")
        if len(set(listed)) != len(listed):
            problems.append(f"{domain}: duplicate entries in domain.yaml")
    return problems


def source_files(root: Path | None = None):
    """Every file the registry is generated from (cards, domain files, defaults, domain defaults)."""
    base = capabilities_dir(root)
    files = sorted(base.glob("*/*/card.yaml")) + sorted(base.glob("*/domain.yaml")) + [base / "defaults.yaml"]
    return files + [(root or repo_root()) / "config" / "priorities.yaml"]


def cards_hash(root: Path | None = None) -> str:
    """Content hash of the registry inputs; a bundle's registry.yaml is stale when this changes."""
    h = hashlib.sha256()
    top = root or repo_root()
    for path in source_files(root):
        h.update(path.relative_to(top).as_posix().encode() + b"\0" + path.read_bytes() + b"\0")
    return h.hexdigest()[:16]
