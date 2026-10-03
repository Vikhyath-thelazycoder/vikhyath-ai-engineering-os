"""Bundle content checks.

HARD (build fails): MCP configuration (spec §2.1): an `.mcp.json`/`mcp*.json` file, or a JSON/YAML/TOML
file declaring `mcpServers`. The only exception is test data for Graphify's MCP-file parser (D-021).
SOFT (recorded as adaptation debt in BUILD.json, cleared by the domain phases): MCP tool mentions and
gstack runtime paths left inside ADAPT text.
"""
import re

CONFIG_EXT = (".json", ".jsonc", ".yaml", ".yml", ".toml")
MCP_FILE = re.compile(r"(^|/)(\.?mcp[^/]*|[^/]*\.mcp)\.json$", re.I)  # .mcp.json, mcp*.json, *.mcp.json
MCP_MENTION = re.compile(r"mcp__|mcpServers|chrome-devtools-mcp|@modelcontextprotocol|\.mcp\.json")
GSTACK_RUNTIME = re.compile(r"\.claude/skills/gstack|gstack-skill-start|gstack-telemetry|gstack-update-check")
D021_ALLOWED = {("graphify", "tests/fixtures/sample.mcp.json")}


def hard_violations(repo, source_path, dest, data: bytes):
    if (repo, source_path) in D021_ALLOWED:
        return []
    found = []
    if MCP_FILE.search(dest):
        found.append(f"{dest}: MCP configuration file")
    elif dest.lower().endswith(CONFIG_EXT) and b"mcpServers" in data:
        found.append(f"{dest}: declares mcpServers")
    return found


def soft_debts(dest, decision, data: bytes):
    if decision != "ADAPT":
        return []
    text = data.decode("utf-8", errors="ignore")
    debts = []
    if MCP_MENTION.search(text):
        debts.append(("mcp_mentions", dest))
    if GSTACK_RUNTIME.search(text):
        debts.append(("gstack_runtime_paths", dest))
    return debts
