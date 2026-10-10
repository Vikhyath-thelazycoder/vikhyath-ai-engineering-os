"""Stdlib project scan: code files, test files, and the limited import graph used when Graphify is unavailable (§74).

Only Python (ast) and relative JS/TS imports are resolved; other languages contribute files and test-name matches but
no edges, and the result says so. Nothing here executes project code.
"""
import ast
import hashlib
import os
import re
from collections import deque
from pathlib import Path, PurePosixPath

SKIP_DIRS = {".git", ".hg", ".svn", "node_modules", ".venv", "venv", "env", "__pycache__", ".mypy_cache",
             ".pytest_cache", ".ruff_cache", ".tox", "dist", "build", ".next", ".nuxt", "out", "target", "vendor",
             ".vikhyath", ".staging", "graphify-out", "coverage", ".gradle", ".idea", ".vscode", "Pods"}
CODE_EXT = {".py", ".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx", ".mts", ".cts", ".vue", ".svelte", ".go", ".rb",
            ".java", ".kt", ".kts", ".rs", ".php", ".cs", ".swift", ".dart", ".scala", ".c", ".cc", ".cpp", ".h",
            ".hpp", ".m", ".ex", ".exs"}
JS_EXT = (".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".mts", ".cts", ".vue", ".svelte")
EDGE_LANGS = {".py"} | set(JS_EXT)
MAX_FILES = 20000
MAX_READ_BYTES = 512 * 1024
TEST_SUPPORT = {"__init__.py", "conftest.py", "setup.ts", "setup.js", "jest.setup.js", "jest.setup.ts"}
TEST_DIRS = {"tests", "test", "__tests__", "spec", "specs", "testing"}
_TEST_NAME = re.compile(r"^(test_.+|.+_test|.+\.(test|spec)|.+Tests?|.+_spec)$")
_JS_IMPORT = re.compile(r"""(?:\bfrom\s*|\bimport\s*\(?\s*|\brequire\(\s*)['"](\.{1,2}/[^'"]+)['"]""")


def rel(path: Path, root: Path) -> str:
    return PurePosixPath(path.relative_to(root)).as_posix()


def is_test(path: str) -> bool:
    p = PurePosixPath(path)
    stem = p.name.split(".")[0] if p.name.count(".") > 1 else p.stem
    if _TEST_NAME.match(p.stem) or _TEST_NAME.match(stem):
        return True
    return any(part in TEST_DIRS for part in p.parts[:-1])


def is_runnable_test(path: str) -> bool:
    """A test file a runner would collect: package markers and shared fixtures are test support, not tests."""
    return is_test(path) and PurePosixPath(path).name not in TEST_SUPPORT


def scan(root: Path):
    """Code files under root (repo-relative POSIX paths, sorted), skipping vendored/generated dirs and symlinks."""
    found = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS and not d.startswith("."))
        for name in sorted(filenames):
            full = Path(dirpath) / name
            if full.suffix.lower() in CODE_EXT and not full.is_symlink():
                found.append(rel(full, root))
                if len(found) >= MAX_FILES:
                    return found, True
    return found, False


def fingerprint(root: Path, files) -> str:
    """Cheap change detector for graph staleness: path + size + mtime of every scanned file (no reads)."""
    h = hashlib.sha256()
    for f in files:
        try:
            st = (root / f).stat()
        except OSError:
            continue
        h.update(f"{f}\0{st.st_size}\0{st.st_mtime_ns}\n".encode())
    return h.hexdigest()[:16]


def _python_imports(source: str, path: str, known: set) -> set:
    try:
        tree = ast.parse(source)
    except (SyntaxError, ValueError):
        return set()
    pkg = PurePosixPath(path).parent
    targets = set()

    def resolve(mod: str):
        base = PurePosixPath(*mod.split(".")) if mod else PurePosixPath()
        for prefix in (PurePosixPath(), PurePosixPath("src")):
            for cand in (prefix / f"{base}.py", prefix / base / "__init__.py"):
                if str(cand) in known:
                    return str(cand)
        return None

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                hit = resolve(alias.name)
                if hit:
                    targets.add(hit)
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                anchor = pkg
                for _ in range(node.level - 1):
                    anchor = anchor.parent
                mod = ".".join(p for p in (*anchor.parts, *(node.module or "").split(".")) if p)
            else:
                mod = node.module or ""
            for alias in node.names:
                hit = resolve(f"{mod}.{alias.name}" if mod else alias.name)
                if hit:
                    targets.add(hit)
            hit = resolve(mod)
            if hit:
                targets.add(hit)
    targets.discard(path)
    return targets


def _js_imports(source: str, path: str, known: set) -> set:
    targets = set()
    here = PurePosixPath(path).parent
    for spec in _JS_IMPORT.findall(source):
        parts = []
        for part in (*here.parts, *PurePosixPath(spec).parts):
            if part == "..":
                if parts:
                    parts.pop()
            elif part != ".":
                parts.append(part)
        base = "/".join(parts)
        for cand in (base, *(base + e for e in JS_EXT), *(f"{base}/index{e}" for e in JS_EXT)):
            if cand in known:
                targets.add(cand)
                break
    targets.discard(path)
    return targets


def import_graph(root: Path, files):
    """file → set of project files it imports (Python + relative JS/TS only)."""
    known = set(files)
    edges = {}
    for f in files:
        ext = PurePosixPath(f).suffix.lower()
        if ext not in EDGE_LANGS:
            continue
        try:
            with open(root / f, "rb") as fh:
                data = fh.read(MAX_READ_BYTES)
        except OSError:
            continue
        text = data.decode("utf-8", errors="ignore")
        edges[f] = _python_imports(text, f, known) if ext == ".py" else _js_imports(text, f, known)
    return edges


def reverse_reach(edges, seeds, depth: int):
    """Files that import the seeds, transitively up to `depth` hops: {file: (depth, via)}."""
    importers = {}
    for src, targets in edges.items():
        for t in targets:
            importers.setdefault(t, set()).add(src)
    seen, out = set(seeds), {}
    queue = deque((s, 0) for s in seeds)
    while queue:
        cur, d = queue.popleft()
        if d >= depth:
            continue
        for src in sorted(importers.get(cur, ())):
            if src not in seen:
                seen.add(src)
                out[src] = (d + 1, cur)
                queue.append((src, d + 1))
    return out


def _bare(stem: str) -> str:
    s = stem.split(".")[0]
    for pre in ("test_",):
        if s.startswith(pre):
            s = s[len(pre):]
    for suf in ("_test", "_spec", "Tests", "Test"):
        if s.endswith(suf) and len(s) > len(suf):
            s = s[: -len(suf)]
    return s.lower()


def tests_named_after(files, tests):
    """Test files whose name targets a non-test file (test_x.py ↔ x.py, x.test.ts ↔ x.ts, x_test.go ↔ x.go)."""
    by_stem = {}
    for t in tests:
        by_stem.setdefault(_bare(PurePosixPath(t).name), []).append(t)
    out = {}
    for f in files:
        if is_test(f):
            continue
        for t in by_stem.get(_bare(PurePosixPath(f).name), ()):
            out.setdefault(t, f)
    return out
