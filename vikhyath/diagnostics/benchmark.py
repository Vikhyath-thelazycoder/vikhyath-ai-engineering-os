"""`vikhyath benchmark --baseline`: measure what installed host plugins load before any task.

Replaces the hard-coded tables of v1.0.1's scripts/benchmark (finding B-1) with measurements.
Method (docs/audit/13_TOKEN_CONTEXT_AUDIT.md): sum `name + description` frontmatter bytes of every
skill, agent and command each installed Claude Code plugin exposes. Tokens are ESTIMATES (bytes / 4).
"""
import json
import re
from pathlib import Path

FIELD = re.compile(r"^([A-Za-z_-]+):\s*(.*)$")


def frontmatter(text):
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    fields, key = {}, None
    for line in text[3:end if end > 0 else 0].splitlines():
        m = FIELD.match(line)
        if m:
            key = m.group(1)
            fields[key] = m.group(2)
        elif key and line[:1] in (" ", "\t"):
            fields[key] += " " + line.strip()
    return fields


def _skill_files(plugin_dir: Path):
    manifest = plugin_dir / ".claude-plugin" / "plugin.json"
    listed = None
    if manifest.is_file():
        try:
            listed = json.loads(manifest.read_text(encoding="utf-8")).get("skills")
        except ValueError:
            listed = None
    if isinstance(listed, str):
        listed = [listed]
    if not isinstance(listed, list):
        listed = ["skills"]
    files = []
    for entry in listed:
        base = plugin_dir / entry
        # An entry is either one skill directory or a directory of skill directories (e.g. "./skills/").
        files += [base / "SKILL.md"] if (base / "SKILL.md").is_file() else sorted(base.glob("*/SKILL.md"))
    return files


def measure_plugin(plugin_dir: Path):
    """Return {kind: (count, bytes)} for skills, agents and commands of one installed plugin."""
    groups = {
        "skills": _skill_files(plugin_dir),
        "agents": sorted((plugin_dir / "agents").glob("*.md")),
        "commands": sorted((plugin_dir / "commands").glob("**/*.md")),
    }
    result = {}
    for kind, files in groups.items():
        total = 0
        for f in files:
            fm = frontmatter(f.read_text(encoding="utf-8", errors="ignore"))
            text = (fm.get("name", "") + " " + fm.get("description", "")).strip()
            if not text:
                text = f.parent.name if kind == "skills" else f.stem
            total += len(text.encode("utf-8"))
        result[kind] = (len(files), total)
    return result


def installed_plugins(plugins_root: Path):
    registry = plugins_root / "installed_plugins.json"
    if not registry.is_file():
        return []
    data = json.loads(registry.read_text(encoding="utf-8"))
    out = []
    for name, installs in sorted(data.get("plugins", {}).items()):
        for inst in installs:
            path = Path(inst.get("installPath", ""))
            if path.is_dir():
                out.append((name, inst.get("version", "?"), path))
    return out


def run(plugins_root: Path | None = None) -> int:
    plugins_root = plugins_root or Path.home() / ".claude" / "plugins"
    print("📊 Vikhyath AI Engineering OS — Benchmark (old-model baseline)")
    print("Token figures are ESTIMATES (bytes / 4); bytes are measured.\n")
    plugins = installed_plugins(plugins_root)
    if not plugins:
        print(f"No installed plugins found under {plugins_root}.")
        return 0
    print("| Plugin | Version | Skills | Agents | Commands | Bytes | Est. tokens |")
    print("|---|---|---:|---:|---:|---:|---:|")
    grand = 0
    for name, version, path in plugins:
        m = measure_plugin(path)
        total = sum(b for _, b in m.values())
        grand += total
        print(f"| {name} | {version} | {m['skills'][0]} | {m['agents'][0]} | {m['commands'][0]} | {total:,} | {total // 4:,} |")
    print(f"\nAlways-loaded descriptions across installed plugins: {grand:,} bytes ≈ {grand // 4:,} tokens (estimate).")
    print("Not included: MCP tool schemas and hook output, which add to this cost.")
    return 0
