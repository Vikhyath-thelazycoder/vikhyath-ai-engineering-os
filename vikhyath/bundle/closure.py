"""Dependency-closure tracing (D-006): a bundled file must not reference a non-bundled repo file.

Used on staging content by tools/audit/extraction_matrix.py and on transformed content by the bundler.
"""
import os
import re

TEXT_EXT = {".md", ".mdx", ".txt", ".json", ".yaml", ".yml", ".toml", ".py", ".js", ".mjs", ".cjs", ".ts",
            ".tsx", ".sh", ".tmpl", ".html", ".css", ".csv", ".go"}
TRY_EXT = ["", ".md", ".py", ".js", ".mjs", ".cjs", ".ts", ".tmpl", "/index.ts", "/index.js", "/__init__.py", "/SKILL.md"]
MAX_TRACE_BYTES = 2_000_000

REF_PATTERNS = [
    re.compile(r"\]\(([^)\s#?]+)"),                                   # markdown links
    re.compile(r"""(?:from|import)\s+['"](\.{1,2}/[^'"]+)['"]"""),     # JS/TS imports
    re.compile(r"""require\(\s*['"](\.{1,2}/[^'"]+)['"]\s*\)"""),     # CommonJS
    re.compile(r"<skill-dir>/([\w./-]+)"),                            # skill-relative paths
    re.compile(r"(?<![\w/.])((?:\.\.?/)+[\w./-]+\.\w{1,5})"),         # explicit ./ ../ paths
    re.compile(r"(?<![\w/.-])((?:references|templates|scripts|sections|specialists|playbooks|docs|data)/[\w./-]+\.\w{1,5})"),
]
PY_REL_IMPORT = re.compile(r"^\s*from\s+(\.+)([\w.]*)\s+import\s+([\w, ()]+)", re.M)


def references(text, path):
    found = set()
    for rx in REF_PATTERNS:
        for m in rx.finditer(text):
            ref = m.group(1).strip("`'\"")
            if "://" in ref or ref.startswith(("mailto:", "#", "/", "~", "$")) or "{" in ref or "<" in ref:
                continue
            found.add(ref)
    if path.endswith(".py"):
        for dots, mod, _names in PY_REL_IMPORT.findall(text):
            if mod:
                found.add("py:" + "../" * (len(dots) - 1) + mod.replace(".", "/"))
    return found


def resolve(ref, path, files, dirs):
    base_dirs = [os.path.dirname(path), ""]
    # skill-relative: walk up to the nearest dir containing SKILL.md
    parts = path.split("/")
    for i in range(len(parts) - 1, 0, -1):
        cand = "/".join(parts[:i])
        if f"{cand}/SKILL.md" in files:
            base_dirs.insert(1, cand)
            break
    is_py = ref.startswith("py:")
    ref = ref[3:] if is_py else ref
    for base in base_dirs:
        target = os.path.normpath(os.path.join(base, ref)).lstrip("./") if base else os.path.normpath(ref)
        if target.startswith(".."):
            continue
        for ext in ([".py", "/__init__.py"] if is_py else TRY_EXT):
            if target + ext in files:
                return target + ext
        if not is_py and target in dirs:
            return target + "/"
    return None


def trace_gaps(repo, decided, read_text, bundled):
    """Gaps for one repo.

    decided:   {path: decision} for every tracked file of the repo
    read_text: callable(path) -> str | None giving the content to scan (staging or transformed)
    bundled:   set of decisions that put a file in the bundle
    A reference to F is satisfied when F is bundled, or when F.tmpl is bundled (F is rendered from it).
    """
    files = set(decided)
    dirs = {p.rsplit("/", i)[0] for p in files for i in range(1, p.count("/") + 1)}

    def satisfied(target):
        return decided.get(target) in bundled or decided.get(target + ".tmpl") in bundled

    gaps = []
    for path, decision in decided.items():
        if decision not in bundled or os.path.splitext(path)[1].lower() not in TEXT_EXT:
            continue
        text = read_text(path)
        if text is None:
            continue
        for ref in references(text, path):
            target = resolve(ref, path, files, dirs)
            if target is None:
                continue
            if target.endswith("/"):
                members = [p for p in files if p.startswith(target)]
                if any(satisfied(p) for p in members):
                    continue
                tdec = decided[members[0]] if members else "?"
            elif satisfied(target):
                continue
            else:
                tdec = decided[target]
            gaps.append((repo, path, ref, target, tdec))
    return gaps


def staging_reader(repo_root):
    def read(path):
        fp = os.path.join(repo_root, path)
        if not os.path.isfile(fp) or os.path.getsize(fp) > MAX_TRACE_BYTES:
            return None
        with open(fp, encoding="utf-8", errors="ignore") as fh:
            return fh.read()
    return read
