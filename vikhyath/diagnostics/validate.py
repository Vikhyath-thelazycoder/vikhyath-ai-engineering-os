"""`vikhyath validate`: Python port of scripts/validate (v1.0.1)."""
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

from . import Report
from .doctor import PORTABLE_SCHEMA, _json

SHA = re.compile(r"^[0-9a-f]{40}$")
EXPECTED_CAPABILITIES = ["ecc", "graphify", "unlazy", "addy", "agency", "gstack", "opendesign", "ponytail", "karpathy"]


def _load_yaml(path: Path):
    import yaml
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError):
        return None


def _routing_ok(routing):
    try:
        r = routing["routing"]
        return ("ecc" in r["simple-bugfix"]["activate"] and "ecc" in r["complex-codebase"]["activate"]
                and "graphify" in r["complex-codebase"]["activate"] and "ecc" in r["security-task"]["activate"]
                and "addy" in r["security-task"]["activate"] and "ponytail" in r["simplicity-review"]["activate"]
                and "ecc" in r["review-release"]["activate"] and "gstack" in r["review-release"]["activate"]
                and "ecc" in routing["fallback"]["activate"])
    except (TypeError, KeyError):
        return False


def _registry_ok(caps):
    try:
        for cap in EXPECTED_CAPABILITIES:
            meta = caps[cap]
            if not all(k in meta for k in ("source", "role", "priority", "activation")) or not SHA.match(meta.get("ref", "")):
                return False
        return (caps["ecc"]["priority"] > caps["graphify"]["priority"] > caps["unlazy"]["priority"]
                and caps["ponytail"].get("default") == "off")
    except (TypeError, KeyError):
        return False


def _online(caps, r):
    failures = 0
    for meta in caps.values():
        url = f"https://api.github.com/repos/{meta['source']}/commits/{meta['ref']}"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Vikhyath-OS-Validator"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                ok = resp.status == 200
        except OSError as exc:
            ok = False
            print(f"  ❌ {meta['source']} @ {meta['ref'][:8]} online check failed: {exc}")
        if ok:
            print(f"  ✅ {meta['source']} @ {meta['ref'][:8]} verified online")
        failures += not ok
    if failures:
        r.warn("Online verification failed or rate-limited. Offline structural tests remain valid.")
    else:
        r.ok(f"All {len(caps)} capabilities verified against remote GitHub repositories")


def run(root: Path, online=False, unittests=True) -> int:
    r = Report("🧪 Vikhyath AI Engineering OS — Validation Suite")
    print("🌐 Mode: ONLINE (verifying remote GitHub commit SHAs)" if online
          else "📦 Mode: OFFLINE (structural and cryptographic format validation)")
    print()

    r.section("📦 Portable Manifest Tests")
    root_manifest = _json(root / "plugin.json") or {}
    r.check(root_manifest.get("$schema") == PORTABLE_SCHEMA and root_manifest.get("name") == "vikhyath-ai-engineering-os"
            and "version" in root_manifest and "mcpServers" not in root_manifest and "skills" not in root_manifest,
            "Root plugin.json adheres to Agent Plugins 1.0.0 specification", "Root plugin.json failed specification validation")
    r.end_section()

    r.section("📋 Host Manifest Tests")
    codex = _json(root / ".codex-plugin/plugin.json") or {}
    r.check(codex.get("name") == "vikhyath-ai-engineering-os" and "version" in codex and "skills" in codex
            and "mcpServers" not in codex, "Codex manifest valid, no MCP", "Codex manifest validation failed")
    claude = _json(root / ".claude-plugin/plugin.json") or {}
    r.check("name" in claude and "mcpServers" not in claude and "skills" not in claude,
            "Claude manifest valid minimal JSON, no MCP", "Claude manifest validation failed")
    m1, m2 = _json(root / ".agents/plugins/marketplace.json"), _json(root / ".claude-plugin/marketplace.json")
    try:
        markets_ok = m1["plugins"][0]["source"] == "./" and m2["plugins"][0]["source"] == "./"
    except (TypeError, KeyError, IndexError):
        markets_ok = False
    r.check(markets_ok, "Codex and Claude marketplace manifests valid", "Marketplace validation failed")
    r.check((root / ".agents/skills/vikhyath-os/SKILL.md").is_file(), "Antigravity skill adapter exists",
            "Antigravity skill adapter missing")
    r.end_section()

    r.section("🔀 Routing Tests")
    if _routing_ok(_load_yaml(root / "config/routing.yaml")):
        r.ok("Routing rules valid")
        for line in ("fix typo → minimal (ecc)", "unfamiliar monorepo → ecc + graphify", "authentication → ecc + addy",
                     "simplicity review → ponytail", "production release → ecc + gstack"):
            r.ok(f"  {line}")
    else:
        r.fail("Routing validation failed")
    r.end_section()

    r.section("📦 Capability Registry Tests")
    caps = (_load_yaml(root / "config/capabilities.yaml") or {}).get("capabilities", {})
    if _registry_ok(caps):
        r.ok(f"All {len(EXPECTED_CAPABILITIES)} capabilities registered with pinned 40-character hexadecimal SHAs")
        r.ok("Priority ordering correct")
        r.ok("Ponytail defaults to off")
    else:
        r.fail("Capability registry validation failed")
    r.end_section()

    if online:
        r.section("🌐 Online GitHub SHA Verification")
        _online(caps, r)
        r.end_section()

    r.section("🔒 Security Tests")
    manifest_text = "".join(p.read_text(encoding="utf-8", errors="ignore")
                            for p in [root / "plugin.json", *(root / ".codex-plugin").glob("*"), *(root / ".claude-plugin").glob("*")]
                            if p.is_file())
    r.check("mcpServers" not in manifest_text, "No MCP in manifests", "MCP found in manifests")
    r.check(not (root / ".mcp.json").exists(), "No .mcp.json", ".mcp.json exists")
    r.check(not (root / "vendor").exists(), "No vendor/ copies", "vendor/ directory exists")
    r.end_section()

    r.section("🔗 Integration Tests")
    for path in sorted((root / "integrations").glob("*.yaml")):
        data = _load_yaml(path) or {}
        ok = all(k in data for k in ("source", "role", "integration_type")) and bool(SHA.match(str(data.get("ref", ""))))
        r.check(ok, f"{path.stem} integration metadata valid with pinned SHA", f"{path.stem} integration metadata invalid")
    r.end_section()

    if unittests:
        r.section("🧪 Unit Test Discovery")
        result = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", str(root / "tests"), "-p", "test_*.py"],
                                capture_output=True, text=True, cwd=root)
        r.check(result.returncode == 0, "All Python unit tests passed", "Python unit test discovery failed")
        r.end_section()

    print("=================================================")
    print(f"Results: ✅ {r.passed} passed, ❌ {r.failed} failed")
    if r.failed:
        print("❌ Validation failed. Fix the issues above.")
        return 1
    print("✅ All validation tests passed!")
    return 0
