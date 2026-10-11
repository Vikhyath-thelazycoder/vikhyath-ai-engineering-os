"""Capability selection: scoring, suppression, project stage, dependencies, conflicts and ordering (spec §15)."""
from dataclasses import dataclass, field

from .classify import find_phrases
from .rules import role_of

ROUTABLE_MODES = ("on-demand", "explicit")


@dataclass
class Candidate:
    cid: str
    score: int = 0
    strong: bool = False
    reasons: list = field(default_factory=list)


def tag_scores(text: str, cards):
    """{cid: (score, matched tags)} for routable capabilities; a multi-word tag counts 2, a single word 1."""
    out = {}
    for cid, card in cards.items():
        if card["activation_conditions"]["mode"] not in ROUTABLE_MODES or not card["intent_tags"]:
            continue
        hit = find_phrases(text, card["intent_tags"])
        if hit:
            out[cid] = (sum(2 if " " in t else 1 for t in hit), hit)
    return out


def domain_of(cid: str) -> str:
    return cid.split("/", 1)[0]


def _rank(cards, roles, hierarchy):
    def key(cid, score=0):
        return (hierarchy.get(role_of(cid, roles), 99), -cards[cid]["priority"], -score, cid)
    return key


def select_capabilities(text, cards, cfg, hierarchy, hits, stage, requested=(), stack=()):
    """Deterministic selection. Returns (selected Candidates in guidance order, suppressed [{id, reason}], extras)."""
    limits = cfg.get("limits") or {}
    roles = cfg.get("roles") or []
    proj = cfg.get("project") or {}
    cands: dict[str, Candidate] = {}

    def add(cid, points, reason, strong):
        c = cands.setdefault(cid, Candidate(cid))
        c.score += points
        c.strong |= strong
        c.reasons.append(reason)

    for h in hits:
        for cid in h.select:
            add(cid, h.weight, f"rule {h.rule} ({', '.join(h.matched[:3])})", True)
    for cid in requested:
        add(cid, 10, "requested explicitly", True)
    for cid, (score, tags) in tag_scores(text, cards).items():
        add(cid, score, f"intent tags ({', '.join(tags[:3])})", False)

    suppress = {t for h in hits for t in h.suppress}
    strong_domains = {domain_of(c.cid) for c in cands.values() if c.strong}
    new_forbids = set(proj.get("new_forbids_domains") or [])
    suppressed = []
    for cid, c in list(cands.items()):
        dom = domain_of(cid)
        why = None
        if not cards[cid]["enabled"]:
            why = "capability disabled"
        elif stage == "new" and dom in new_forbids:
            why = "new project: no existing codebase to analyse (spec §19.2)"
        elif not c.strong and (cid in suppress or dom in suppress):
            why = "suppressed by a matched routing rule (weak tag signal only)"
        elif not c.strong and strong_domains and dom not in strong_domains and c.score < 2:
            why = "single weak tag outside the routed domains"
        elif not c.strong and c.score < limits.get("tag_min_score", 1):
            why = "below tag_min_score"
        if why:
            suppressed.append({"id": cid, "reason": why})
            del cands[cid]

    rank = _rank(cards, roles, hierarchy)
    ordered = sorted(cands.values(), key=lambda c: (not c.strong, -c.score, -cards[c.cid]["priority"], c.cid))
    keep = ordered[:limits.get("max_capabilities", 8)]
    suppressed += [{"id": c.cid, "reason": "over limits.max_capabilities"} for c in ordered[len(keep):]]

    # Declared conflicts (cards' `conflicts`): the capability ranked lower in the conflict hierarchy is dropped.
    chosen = {c.cid: c for c in keep}
    for cid in sorted(chosen, key=rank):
        if cid not in chosen:
            continue
        for other in cards[cid]["conflicts"]:
            if other in chosen:
                suppressed.append({"id": other, "reason": f"conflicts with {cid} (lower in config/priorities.yaml hierarchy)"})
                del chosen[other]
    selected = sorted(chosen.values(), key=lambda c: rank(c.cid, c.score))
    return selected, suppressed, {"suppress": sorted(suppress), "existing_adds": proj.get("existing_adds") or [],
                                  "existing_change_types": proj.get("existing_change_types") or []}


def dependency_closure(selected_ids, cards, stack=()):
    """[{id, required_by}] for dependencies not already selected, plus stack packs when a stack is known."""
    out, seen = [], set(selected_ids)
    queue = [(cid, d) for cid in selected_ids for d in cards[cid]["dependencies"]]
    while queue:
        parent, dep = queue.pop(0)
        if dep in seen or not cards[dep]["enabled"]:
            continue
        seen.add(dep)
        out.append({"id": dep, "required_by": parent})
        queue += [(dep, d) for d in cards[dep]["dependencies"]]
    if stack and "engineering/stack-packs" not in seen and any(domain_of(c) == "engineering" for c in selected_ids):
        out.append({"id": "engineering/stack-packs", "required_by": f"stack-detected: {', '.join(stack)}"})
    return out
