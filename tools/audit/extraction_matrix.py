#!/usr/bin/env python3
"""Apply extraction-rules.yaml to every upstream file and trace dependency closure (D-006).

Outputs (docs/audit/evidence/):
  extraction-matrix/<repo>.tsv   decision, reason, capability, bytes, path   (one row per tracked file)
  extraction-summary.json        counts/bytes per repo x decision and per capability
  closure-gaps.tsv               bundled file -> referenced repo file that is NOT bundled

Exit code 1 if a rule names an unknown capability/decision, a domain-model capability has no
bundled source (spec: no empty domains), or closure gaps remain that are not explicitly accepted.
Requires PyYAML.
"""
import json
import os
import re
import sys
from collections import defaultdict

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from pathlib import Path  # noqa: E402

from vikhyath.bundle.rules import (BUNDLED, classify, compile_rules, known_capabilities,  # noqa: E402
                                   load_domain_model, load_rules)
from vikhyath.bundle.rules import read_inventory as _read_inventory  # noqa: E402

STAGING = os.path.join(ROOT, ".staging", "upstream")
EVIDENCE = os.path.join(ROOT, "docs", "audit", "evidence")

TEXT_EXT = {".md", ".mdx", ".txt", ".json", ".yaml", ".yml", ".toml", ".py", ".js", ".mjs", ".cjs", ".ts",
            ".tsx", ".sh", ".tmpl", ".html", ".css", ".csv", ".go"}
TRY_EXT = ["", ".md", ".py", ".js", ".mjs", ".cjs", ".ts", ".tmpl", "/index.ts", "/index.js", "/__init__.py", "/SKILL.md"]

REF_PATTERNS = [
    re.compile(r"\]\(([^)\s#?]+)"),                                   # markdown links
    re.compile(r"""(?:from|import)\s+['"](\.{1,2}/[^'"]+)['"]"""),     # JS/TS imports
    re.compile(r"""require\(\s*['"](\.{1,2}/[^'"]+)['"]\s*\)"""),     # CommonJS
    re.compile(r"<skill-dir>/([\w./-]+)"),                            # skill-relative paths
    re.compile(r"(?<![\w/.])((?:\.\.?/)+[\w./-]+\.\w{1,5})"),         # explicit ./ ../ paths
    re.compile(r"(?<![\w/.-])((?:references|templates|scripts|sections|specialists|playbooks|docs|data)/[\w./-]+\.\w{1,5})"),
]
PY_REL_IMPORT = re.compile(r"^\s*from\s+(\.+)([\w.]*)\s+import\s+([\w, ()]+)", re.M)


def read_inventory(repo):
    return _read_inventory(Path(EVIDENCE), repo)


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


def main():
    rules_doc = load_rules()
    caps = known_capabilities(load_domain_model())
    errors = compile_rules(rules_doc, caps)

    os.makedirs(os.path.join(EVIDENCE, "extraction-matrix"), exist_ok=True)
    summary = {"repos": {}, "capabilities": defaultdict(lambda: {"files": 0, "bytes": 0, "sources": set()})}
    gaps = []
    for repo in sorted(rules_doc["repos"]):
        rr = rules_doc["repos"][repo]
        inv = read_inventory(repo)
        files = {p for p, _, _ in inv}
        dirs = {p.rsplit("/", i)[0] for p in files for i in range(1, p.count("/") + 1)}
        decided = {}
        per = defaultdict(lambda: {"files": 0, "bytes": 0})
        with open(os.path.join(EVIDENCE, "extraction-matrix", f"{repo}.tsv"), "w", encoding="utf-8") as out:
            out.write("decision\treason\tcapability\tbytes\tpath\n")
            for path, size, _sha in inv:
                rule = classify(rr, path)
                d, cap = rule["decision"], rule.get("capability", "")
                decided[path] = (d, cap)
                per[d]["files"] += 1
                per[d]["bytes"] += size
                if d in BUNDLED:
                    c = summary["capabilities"][cap]
                    c["files"] += 1
                    c["bytes"] += size
                    c["sources"].add(repo)
                out.write(f"{d}\t{rule['reason']}\t{cap}\t{size}\t{path}\n")
        summary["repos"][repo] = dict(per)

        # dependency closure over bundled text files
        for path, (d, _cap) in decided.items():
            if d not in BUNDLED or os.path.splitext(path)[1].lower() not in TEXT_EXT:
                continue
            fp = os.path.join(STAGING, repo, path)
            if not os.path.isfile(fp) or os.path.getsize(fp) > 2_000_000:
                continue
            with open(fp, encoding="utf-8", errors="ignore") as fh:
                text = fh.read()
            for ref in references(text, path):
                target = resolve(ref, path, files, dirs)
                if target is None:
                    continue
                if target.endswith("/"):
                    members = [p for p in files if p.startswith(target)]
                    if any(decided[p][0] in BUNDLED for p in members):
                        continue
                    tdec = decided[members[0]][0] if members else "?"
                elif decided[target][0] in BUNDLED:
                    continue
                else:
                    tdec = decided[target][0]
                gaps.append((repo, path, ref, target, tdec))

    for cap, meta in caps.items():
        own = summary["capabilities"].get(cap, {}).get("files", 0)
        shared = sum(summary["capabilities"].get(u, {}).get("files", 0) for u in meta.get("uses") or [])
        if own == 0 and shared == 0 and meta.get("origin") != "os-native":
            errors.append(f"empty capability (no bundled source): {cap}")

    accepted = {(a["repo"], a["target"]): a["reason"] for a in rules_doc.get("accepted_gaps", [])}
    open_gaps = 0
    with open(os.path.join(EVIDENCE, "closure-gaps.tsv"), "w", encoding="utf-8") as f:
        f.write("repo\tsource\treference\ttarget\ttarget_decision\tstatus\n")
        for g in sorted(set(gaps)):
            status = "ACCEPTED: " + accepted[(g[0], g[3])] if (g[0], g[3]) in accepted else "OPEN"
            open_gaps += status == "OPEN"
            f.write("\t".join(g) + "\t" + status + "\n")
    if open_gaps:
        errors.append(f"{open_gaps} open closure gaps (see closure-gaps.tsv)")
    caps_out = {k: {"files": v["files"], "bytes": v["bytes"], "est_tokens": v["bytes"] // 4, "sources": sorted(v["sources"])}
                for k, v in sorted(summary["capabilities"].items())}
    with open(os.path.join(EVIDENCE, "extraction-summary.json"), "w", encoding="utf-8") as f:
        json.dump({"repos": summary["repos"], "capabilities": caps_out}, f, indent=1)

    tot = defaultdict(lambda: [0, 0])
    for repo, per in summary["repos"].items():
        for d, v in per.items():
            tot[d][0] += v["files"]
            tot[d][1] += v["bytes"]
        print(f"{repo:11} " + "  ".join(f"{d}={v['files']}" for d, v in sorted(per.items())))
    print("TOTAL      " + "  ".join(f"{d}={n} ({b / 1e6:.1f} MB)" for d, (n, b) in sorted(tot.items())))
    print(f"capabilities with bundled sources: {len(caps_out)} / model: {len(caps)}")
    print(f"closure gaps: {len(set(gaps))} total, {open_gaps} open")
    for e in errors:
        print("ERROR:", e)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
