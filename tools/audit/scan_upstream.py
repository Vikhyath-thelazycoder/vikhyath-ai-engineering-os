#!/usr/bin/env python3
"""Scan staged upstream snapshots and emit audit evidence.

For each repo in .staging/upstream/<name>:
  docs/audit/evidence/upstream-file-hashes/<name>.tsv  blob_sha1, bytes, path (every tracked file)
  docs/audit/evidence/upstream-scan/<name>.json        structural + behavioral indicators

Usage: python3 tools/audit/scan_upstream.py [name ...]   (default: all staged repos)
Stdlib only. Read-only with respect to the snapshots.
"""
import json
import os
import re
import subprocess
import sys
from collections import Counter

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
STAGING = os.path.join(ROOT, ".staging", "upstream")
EVIDENCE = os.path.join(ROOT, "docs", "audit", "evidence")
MAX_SCAN_BYTES = 1_000_000
MAX_FILES_LISTED = 60

TEXT_EXT = {
    ".md", ".mdx", ".txt", ".json", ".jsonc", ".yaml", ".yml", ".toml", ".py", ".js", ".mjs", ".cjs",
    ".ts", ".tsx", ".jsx", ".sh", ".bash", ".zsh", ".ps1", ".rb", ".go", ".rs", ".html", ".css",
    ".tmpl", ".mdc", ".cfg", ".ini", ".env", ".sql", ".vue", ".svelte", "",
}

HOST_DIRS = [
    ".claude", ".claude-plugin", ".codex", ".codex-plugin", ".cursor", ".cursor-plugin", ".agents",
    ".gemini", ".opencode", ".windsurf", ".kiro", ".qwen", ".trae", ".zed", ".github/copilot",
]

# name -> regex applied to file content (code/config only unless noted)
INDICATORS = {
    "mcp": r"mcpServers|@modelcontextprotocol|\bmcp\.json\b|FastMCP|McpServer|mcp_server",
    "network": r"\bfetch\(|axios|requests\.(get|post|put|delete|Session)|urllib\.request|httpx|\bcurl\s|\bwget\s|aiohttp|node-fetch|got\(",
    "telemetry": r"posthog|telemetry|mixpanel|segment\.(io|com)|sentry|amplitude|plausible|google-analytics|gtag\(",
    "background": r"\bdaemon\b|launchctl|systemd|\bnohup\b|setInterval\(|crontab|\bcron\b|detached:\s*true|start_new_session|disown",
    "browser": r"playwright|puppeteer|chromium|selenium|chrome-devtools|headless",
    "shell_exec": r"child_process|subprocess\.|os\.system\(|execSync|spawnSync|\bexec\(|\beval\(",
    "env_secrets": r"process\.env\.|os\.environ|API_KEY|_TOKEN\b|SECRET",
    "home_writes": r"~/\.claude|~/\.codex|~/\.cursor|\$HOME|os\.path\.expanduser|homedir\(\)|Path\.home\(\)",
    "self_update": r"git pull|npm (i|install) -g|pip install|curl[^\n|]*\|\s*(ba)?sh|auto-?update|self-?update",
    "llm_api": r"anthropic|openai|api\.anthropic\.com|generativelanguage|OPENAI_API_KEY|ANTHROPIC_API_KEY",
}
CODE_EXT = {".py", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx", ".sh", ".bash", ".zsh", ".ps1", ".rb", ".go", ".rs",
            ".json", ".jsonc", ".yaml", ".yml", ".toml", ".vue", ".svelte", ""}

MANIFEST_NAMES = {
    "package.json", "pyproject.toml", "requirements.txt", "setup.py", "setup.cfg", "Cargo.toml", "go.mod",
    "plugin.json", "marketplace.json", "hooks.json", ".mcp.json", "Dockerfile", "docker-compose.yml",
    "uv.lock", "pnpm-workspace.yaml", "bun.lock", "Gemfile", "agent.yaml", "conductor.json",
}
INSTALL_RE = re.compile(r"(^|/)(install|setup|bootstrap|update|uninstall)[^/]*\.(sh|ps1|py|js|mjs|ts)$", re.I)
LICENSE_RE = re.compile(r"(^|/)(LICEN[CS]E|COPYING|NOTICE|THIRD[_-]PARTY)[^/]*$", re.I)


def git(repo, *args):
    return subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True, check=True).stdout


def frontmatter(text):
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    out = {}
    for line in text[3:end].splitlines():
        m = re.match(r"^([A-Za-z_-]+):\s*(.*)$", line)
        if m:
            out[m.group(1)] = m.group(2).strip().strip('"\'')
    return out


def capped(paths):
    return sorted(paths)[:MAX_FILES_LISTED]


def scan(name):
    repo = os.path.join(STAGING, name)
    head = git(repo, "rev-parse", "HEAD").strip()
    rows = []
    for line in git(repo, "ls-tree", "-r", "-l", "HEAD").splitlines():
        meta, path = line.split("\t", 1)
        mode, typ, sha, size = meta.split()
        if typ != "blob":
            continue  # submodules (commit) recorded separately below
        rows.append((sha, int(size) if size != "-" else 0, path))
    submodules = [l.split("\t", 1)[1] for l in git(repo, "ls-tree", "-r", "HEAD").splitlines() if " commit " in l]

    os.makedirs(os.path.join(EVIDENCE, "upstream-file-hashes"), exist_ok=True)
    with open(os.path.join(EVIDENCE, "upstream-file-hashes", f"{name}.tsv"), "w", encoding="utf-8") as f:
        f.write(f"# {name} @ {head}\nblob_sha1\tbytes\tpath\n")
        for sha, size, path in rows:
            f.write(f"{sha}\t{size}\t{path}\n")

    top_dirs = Counter(p.split("/", 1)[0] if "/" in p else "(root)" for _, _, p in rows)
    exts = Counter(os.path.splitext(p)[1].lower() or "(none)" for _, _, p in rows)
    hits = {k: set() for k in INDICATORS}
    compiled = {k: re.compile(v, re.I) for k, v in INDICATORS.items()}
    skills, agents, commands, hooks, manifests, installers, licenses, mcp_files = [], [], [], [], [], [], [], []

    for _, size, path in rows:
        base = os.path.basename(path)
        ext = os.path.splitext(path)[1].lower()
        if base in MANIFEST_NAMES:
            manifests.append(path)
        if base == ".mcp.json" or re.search(r"(^|/)mcp[^/]*\.json$", path, re.I):
            mcp_files.append(path)
        if INSTALL_RE.search(path):
            installers.append(path)
        if LICENSE_RE.search(path):
            licenses.append(path)
        if "hooks" in path.split("/") or base in ("hooks.json", "settings.json"):
            hooks.append(path)
        if ext not in TEXT_EXT or size > MAX_SCAN_BYTES:
            continue
        try:
            with open(os.path.join(repo, path), encoding="utf-8", errors="ignore") as fh:
                text = fh.read()
        except OSError:
            continue
        if base == "SKILL.md":
            fm = frontmatter(text)
            skills.append({"path": path, "name": fm.get("name", ""), "description": fm.get("description", "")[:240], "bytes": size})
        elif ext == ".md" and "/agents/" in f"/{path}" and frontmatter(text).get("name"):
            agents.append({"path": path, "name": frontmatter(text)["name"], "bytes": size})
        elif ext == ".md" and "/commands/" in f"/{path}":
            commands.append(path)
        if ext in CODE_EXT:
            for key, rx in compiled.items():
                if rx.search(text):
                    hits[key].add(path)
        elif rows and compiled["mcp"].search(text):
            hits["mcp"].add(path)  # MCP mentions in docs still matter

    result = {
        "repo": name,
        "head": head,
        "totals": {"files": len(rows), "bytes": sum(s for _, s, _ in rows), "submodules": submodules},
        "top_dirs": dict(top_dirs.most_common()),
        "extensions": dict(exts.most_common(25)),
        "host_dirs": [d for d in HOST_DIRS if any(p == d or p.startswith(d + "/") for _, _, p in rows)],
        "manifests": sorted(manifests),
        "mcp_files": sorted(mcp_files),
        "installers": capped(installers),
        "license_files": sorted(licenses),
        "skills": sorted(skills, key=lambda s: s["path"]),
        "agents": sorted(agents, key=lambda a: a["path"]),
        "commands": {"count": len(commands), "files": capped(commands)},
        "hooks": {"count": len(hooks), "files": capped(hooks)},
        "indicators": {k: {"count": len(v), "files": capped(v)} for k, v in hits.items()},
    }
    os.makedirs(os.path.join(EVIDENCE, "upstream-scan"), exist_ok=True)
    with open(os.path.join(EVIDENCE, "upstream-scan", f"{name}.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=1)
    return result


def main(argv):
    names = argv or sorted(d for d in os.listdir(STAGING) if os.path.isdir(os.path.join(STAGING, d)))
    for name in names:
        r = scan(name)
        ind = " ".join(f"{k}={v['count']}" for k, v in r["indicators"].items())
        print(f"{name:11} files={r['totals']['files']:6} skills={len(r['skills']):4} agents={len(r['agents']):4} "
              f"cmds={r['commands']['count']:4} hooks={r['hooks']['count']:4} mcp_files={len(r['mcp_files'])} | {ind}")


if __name__ == "__main__":
    main(sys.argv[1:])
