"""Markdown sectioning: load the parts of a file that fit a budget, list the rest by id (spec §16 "exact required
instructions", doc 13 §3 section-level loading)."""
import re
from dataclasses import asdict, dataclass

import yaml

from ..routing.fallback_bm25 import BM25

_FRONTMATTER = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n", re.S)
_HEADING = re.compile(r"^(#{1,3})[ \t]+(.+?)[ \t]*#*[ \t]*$")
_FENCE = re.compile(r"^[ \t]*(```|~~~)")
_SLUG = re.compile(r"[^a-z0-9]+")


def est_tokens(nbytes: int) -> int:
    """Spec §46 estimate: bytes ÷ 4, rounded up."""
    return -(-nbytes // 4)


def nbytes(text: str) -> int:
    return len(text.encode("utf-8"))


@dataclass
class Section:
    id: str
    title: str
    level: int
    start: int   # character offsets into the text
    end: int
    tokens: int

    def as_dict(self):
        return asdict(self)


def frontmatter(text: str):
    """(metadata dict, offset where the body starts). Bad YAML yields {} rather than an error."""
    m = _FRONTMATTER.match(text)
    if not m:
        return {}, 0
    try:
        meta = yaml.safe_load(m.group(1))
    except yaml.YAMLError:
        meta = None
    return (meta if isinstance(meta, dict) else {}), m.end()


def split_sections(text: str):
    """Sections at heading levels 1–3, ignoring headings inside code fences. Text before the first heading (after
    frontmatter) is section `intro`."""
    _, body = frontmatter(text)
    heads, fence, pos = [], None, 0
    for line in text[body:].splitlines(keepends=True):
        f = _FENCE.match(line)
        if f:
            fence = None if fence == f.group(1) else (fence or f.group(1))
        elif fence is None:
            h = _HEADING.match(line.rstrip("\r\n"))
            if h:
                heads.append((body + pos, len(h.group(1)), h.group(2).strip()))
        pos += len(line)
    out, used = [], set()

    def add(sid, title, level, start, end):
        if text[start:end].strip():
            base, n = sid or "section", 2
            while sid in used or not sid:
                sid, n = f"{base}-{n}", n + 1
            used.add(sid)
            out.append(Section(sid, title, level, start, end, est_tokens(nbytes(text[start:end]))))

    first = heads[0][0] if heads else len(text)
    add("intro", "(intro)", 0, body, first)
    for i, (start, level, title) in enumerate(heads):
        end = heads[i + 1][0] if i + 1 < len(heads) else len(text)
        add(_SLUG.sub("-", title.lower()).strip("-")[:60], title, level, start, end)
    return out


def pick_sections(sections, budget_tokens: int, query: str | None = None, wanted=None):
    """Choose sections for a budget from section metadata alone (no file read). `wanted` ids are taken first and only
    (explicit request); otherwise the intro, then the rest by relevance of their titles to `query` (BM25) or document
    order. Returns (chosen sections in document order, skipped sections, truncated: bool). A first section larger than
    the whole budget is truncated on a line boundary when rendered."""
    if not sections:
        return [], [], False
    by_id = {s.id: s for s in sections}
    order = [by_id[w] for w in (wanted or []) if w in by_id]
    rest = [s for s in sections if s not in order]
    intro = [s for s in rest if s.id == "intro"] if not wanted else []
    others = [s for s in rest if s.id != "intro"] if not wanted else []
    if query and others:
        scores = dict(BM25({s.id: s.title for s in others}).score(query))
        others.sort(key=lambda s: (-scores.get(s.id, 0.0), s.start))
    chosen, used = [], 0
    for s in order + intro + others:
        if used + s.tokens <= budget_tokens:
            chosen.append(s)
            used += s.tokens
    truncated = False
    if wanted and not order:
        return [], list(sections), False
    if not chosen:
        first = (order + intro + others)[0]
        chosen, truncated = [first], True
    chosen.sort(key=lambda s: s.start)
    skipped = [s for s in sections if s not in chosen]
    return chosen, skipped, truncated


def render(text: str, chosen, truncated: bool, budget_tokens: int) -> str:
    out = "".join(text[s.start:s.end] for s in chosen)
    if truncated:
        cut = out.encode("utf-8")[:budget_tokens * 4].decode("utf-8", "ignore")
        out = (cut[:cut.rfind("\n") + 1] if "\n" in cut else cut) + "\n[… truncated to the budget]\n"
    return out
