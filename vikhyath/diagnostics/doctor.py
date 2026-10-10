"""`vikhyath doctor`: Python port of scripts/doctor (v1.0.1) plus environment checks."""
import json
import sys
from pathlib import Path

from . import Report

PORTABLE_SCHEMA = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
STRUCTURE_DIRS = ["skills", "agents", "capabilities", "config", "tests", "scripts", ".codex-plugin",
                  ".claude-plugin", ".agents/skills", ".agents/plugins", ".github/workflows"]
KEY_FILES = ["README.md", "AGENTS.md", "CLAUDE.md", "LICENSE", "CHANGELOG.md", "CONTRIBUTING.md", "SECURITY.md",
             "CODE_OF_CONDUCT.md"]


def _json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _yaml_ok(path: Path):
    import yaml
    try:
        yaml.safe_load(path.read_text(encoding="utf-8"))
        return True
    except (OSError, yaml.YAMLError):
        return False


def _marketplace_ok(data):
    try:
        plugin = data["plugins"][0]
        return plugin["name"] == "vikhyath-ai-engineering-os" and plugin["source"] == "./"
    except (TypeError, KeyError, IndexError):
        return False


def _contains(paths, needle):
    for p in paths:
        files = [p] if p.is_file() else list(p.rglob("*")) if p.is_dir() else []
        for f in files:
            if f.is_file() and needle in f.read_text(encoding="utf-8", errors="ignore"):
                return True
    return False


def run(root: Path) -> int:
    r = Report("🔍 Vikhyath AI Engineering OS — Doctor")

    r.section("🐍 Environment")
    r.check(sys.version_info >= (3, 10), f"Python {sys.version.split()[0]} (>= 3.10)",
            f"Python {sys.version.split()[0]} is older than 3.10")
    try:
        import yaml  # noqa: F401
        r.ok("PyYAML importable")
    except ImportError:
        r.fail("PyYAML missing — install with `pip install -e .`")
        r.end_section()
        print(f"Results: ✅ {r.passed} passed, ❌ {r.failed} failed, ⚠️  {r.warned} warnings")
        return 1
    r.end_section()

    r.section("📁 Repository Structure")
    for d in STRUCTURE_DIRS:
        r.check((root / d).is_dir(), f"{d}/ exists", f"{d}/ missing")
    r.end_section()

    r.section("📦 Portable Root Manifest (Agent Plugins 1.0.0)")
    data = _json(root / "plugin.json")
    if data is None:
        r.fail("plugin.json (root portable manifest) missing or invalid")
    else:
        forbidden = [f for f in ("skills", "mcpServers", "interface", "hooks", "tools") if f in data]
        valid = (data.get("$schema") == PORTABLE_SCHEMA and data.get("name") == "vikhyath-ai-engineering-os"
                 and all(k in data for k in ("version", "description", "author", "license")) and not forbidden)
        r.check(valid, "plugin.json conforms to Agent Plugins 1.0.0 schema",
                "plugin.json validation failed (invalid schema or forbidden top-level fields)")
    r.end_section()

    r.section("📋 Host Manifests & Marketplaces")
    codex = _json(root / ".codex-plugin/plugin.json")
    r.check(codex is not None and "mcpServers" not in codex, ".codex-plugin/plugin.json valid JSON (no MCP)",
            ".codex-plugin/plugin.json missing, invalid or contains MCP")
    claude = _json(root / ".claude-plugin/plugin.json")
    r.check(claude is not None and "mcpServers" not in claude and "skills" not in claude,
            ".claude-plugin/plugin.json valid minimal JSON", ".claude-plugin/plugin.json invalid or contains non-standard fields")
    r.check(_marketplace_ok(_json(root / ".agents/plugins/marketplace.json")), ".agents/plugins/marketplace.json valid",
            ".agents/plugins/marketplace.json missing or invalid")
    r.check(_marketplace_ok(_json(root / ".claude-plugin/marketplace.json")), ".claude-plugin/marketplace.json valid",
            ".claude-plugin/marketplace.json missing or invalid")
    r.end_section()

    r.section("🌌 Antigravity Packaging")
    skill = root / ".agents/skills/vikhyath-os/SKILL.md"
    r.check(skill.is_file() and "name: vikhyath-os" in skill.read_text(encoding="utf-8"),
            ".agents/skills/vikhyath-os/SKILL.md adapter intact", ".agents/skills/vikhyath-os/SKILL.md missing or unnamed")
    r.end_section()

    r.section("⚙️  CI Workflow Integrity")
    import yaml
    ci = root / ".github/workflows/ci.yml"
    try:
        ci_data = yaml.safe_load(ci.read_text(encoding="utf-8"))
        ci_ok = isinstance(ci_data, dict) and "name" in ci_data and "jobs" in ci_data
    except (OSError, yaml.YAMLError):
        ci_ok = False
    r.check(ci_ok, ".github/workflows/ci.yml valid YAML workflow", ".github/workflows/ci.yml missing or invalid")
    r.end_section()

    r.section("🚫 MCP Absence Check")
    manifests = [root / ".codex-plugin", root / ".claude-plugin", root / "plugin.json"]
    r.check(not _contains(manifests, "mcpServers"), "No MCP in plugin manifests", "MCP configuration found in plugin manifests!")
    r.check(not (root / ".mcp.json").exists(), "No .mcp.json file", ".mcp.json file exists — MCP is prohibited")
    config_mcp = any(_contains([root / "config"], n) for n in ("mcpServers", "mcp-configs", "mcp_server"))
    r.check(not config_mcp, "No MCP configuration in config/", "MCP references found in config/")
    r.end_section()

    r.section("📄 YAML Configuration")
    for name in ("config/routing.yaml", "config/priorities.yaml"):
        path = root / name
        r.check(path.is_file() and _yaml_ok(path), f"{name} valid YAML", f"{name} missing or invalid YAML")
    r.end_section()

    r.section("🗂️  Capability Registry")
    from ..registry import loader, schema
    try:
        problems = loader.structure_problems(root)
        cards = loader.load_cards(root)
    except (OSError, loader.RegistryError) as exc:
        problems, cards = [str(exc)], {}
    r.check(not problems and cards, f"capabilities/ layout consistent ({len(cards)} cards in {len(loader.load_domains(root)) if cards else 0} domains)",
            "capabilities/ layout inconsistent: " + "; ".join(problems[:3]))
    card_problems = schema.validate_cards(cards) if cards else ["no cards"]
    r.check(not card_problems, "All capability cards match the registry schema (spec §13)",
            "Capability card problems: " + "; ".join(card_problems[:3]))
    no_doc = [cid for cid in cards if not (loader.capabilities_dir(root) / cid / "CARD.md").is_file()]
    r.check(cards and not no_doc, "Every capability has an L1 CARD.md", f"CARD.md missing for {no_doc[:5]}")
    r.end_section()

    r.section("🎯 Skills")
    for skill_dir in sorted((root / "skills").glob("vikhyath-*/")):
        r.check((skill_dir / "SKILL.md").is_file(), f"{skill_dir.name}/SKILL.md exists", f"{skill_dir.name}/SKILL.md missing")
    r.end_section()

    r.section("🧠 Runtimes")
    from ..paths import current_bundle, vikhyath_home
    from ..runtimes import graphify
    h = graphify.health(vikhyath_home(), current_bundle())
    if h["status"] == "ready":
        r.ok(f"graphify {h.get('version') or ''} ready ({h['lock']})")
    else:   # MR-09: codebase work falls back to limited structural analysis (§74); not a failure
        r.warn(f"graphify {h['status']}: {h['reason']} — codebase analysis uses the structural fallback")
    r.end_section()

    r.section("📦 No Upstream Copies")
    r.check(not (root / "vendor").exists(), "No vendor/ directory", "vendor/ directory exists — upstream copies prohibited")
    r.ok("No upstream repository copies detected")
    r.end_section()

    r.section("🏷️  Version Consistency")
    version_file = root / "VERSION"
    if version_file.is_file():
        version = version_file.read_text(encoding="utf-8").strip()
        found = {name: (_json(root / name) or {}).get("version", "")
                 for name in ("plugin.json", ".codex-plugin/plugin.json", ".claude-plugin/plugin.json")}
        r.check(all(v == version for v in found.values()),
                f"Version consistent across VERSION, plugin.json, and host manifests: {version}",
                f"Version mismatch: VERSION={version}, " + ", ".join(f"{k}={v}" for k, v in found.items()))
    else:
        r.fail("VERSION file missing")
    r.end_section()

    r.section("📝 Key Files")
    for name in KEY_FILES:
        r.check((root / name).is_file(), f"{name} exists", f"{name} missing")
    r.end_section()

    print("=======================================")
    print(f"Results: ✅ {r.passed} passed, ❌ {r.failed} failed, ⚠️  {r.warned} warnings")
    if r.failed:
        print("❌ Doctor found issues. Please fix the failures above.")
        return 1
    print("✅ All doctor checks passed!")
    return 0
