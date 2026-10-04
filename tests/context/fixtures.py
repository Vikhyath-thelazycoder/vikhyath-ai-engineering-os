"""Fixture bundle + project for context tests (no real bundle needed)."""
import hashlib
import json
from pathlib import Path


def _skill(name, sections, words=120):
    body = [f"---\nname: {name}\ndescription: {name} guidance for webhook signature checks\n---\n", f"# {name}\n\nIntro text.\n"]
    for i, title in enumerate(sections):
        body.append(f"\n## {title}\n\n" + " ".join(f"{title.split()[0].lower()}{i}w{n}" for n in range(words)) + "\n")
    body.append("\n```md\n## not a heading inside a fence\n```\n")
    return "".join(body)


FILES = {
    "files/alpha/skills/security-review/SKILL.md": _skill("security-review", [
        "Webhook signature verification", "Secrets management", "SQL injection", "Rate limiting", "Logging",
        "Session handling", "CSRF", "Dependency audit"], words=400),
    "files/alpha/skills/hardening/SKILL.md": _skill("hardening", ["Headers", "CORS", "Cookies"], words=200),
    "files/alpha/skills/hardening/references/checklist.md": _skill("checklist", ["Auth", "Input"], words=300),
    "files/alpha/agents/backend-reviewer.md": _skill("backend-reviewer", ["Queues", "Payments"], words=200),
    "files/alpha/scripts/check.sh": "#!/bin/sh\necho ok\n",
    "files/alpha/LICENSE": "MIT License\n",
    "files/beta/skills/test-security/SKILL.md": _skill("test-security", ["Authn tests", "Authz tests"], words=150),
    "files/beta/skills/impact/SKILL.md": _skill("impact", ["Reverse traversal"], words=100),
}
CAPABILITIES = {
    "engineering/security": ["files/alpha/skills/security-review/SKILL.md", "files/alpha/skills/hardening/SKILL.md",
                             "files/alpha/skills/hardening/references/checklist.md", "files/alpha/scripts/check.sh",
                             "files/alpha/LICENSE"],
    "engineering/backend": ["files/alpha/agents/backend-reviewer.md"],
    "testing/security": ["files/beta/skills/test-security/SKILL.md"],
    "codebase/impact-analysis": ["files/beta/skills/impact/SKILL.md"],
}


def make_bundle(home: Path, bundle_id="fixturebundle"):
    bundle = home / "bundles" / bundle_id
    files = {}
    for rel, text in FILES.items():
        path = bundle / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        data = text.encode("utf-8")
        cap = next(c for c, ps in CAPABILITIES.items() if rel in ps)
        files[rel] = {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(), "capability": cap}
    (bundle / "index.json").write_text(json.dumps({"bundle_id": bundle_id, "capabilities": CAPABILITIES,
                                                   "files": files}), encoding="utf-8")
    current = home / "bundles" / "current"
    if current.is_symlink() or current.exists():
        current.unlink()
    current.symlink_to(bundle_id)
    return bundle


def make_project(base: Path, name="proj", origin="git@github.com:Example/Proj.git"):
    root = base / name
    (root / ".git").mkdir(parents=True)
    (root / ".git" / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")
    (root / ".git" / "config").write_text(f'[core]\n\tbare = false\n[remote "origin"]\n\turl = {origin}\n',
                                          encoding="utf-8")
    return root
