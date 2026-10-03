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

from vikhyath.bundle.closure import staging_reader, trace_gaps  # noqa: E402


def read_inventory(repo):
    return _read_inventory(Path(EVIDENCE), repo)


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
        gaps += trace_gaps(repo, {p: d for p, (d, _c) in decided.items()},
                           staging_reader(os.path.join(STAGING, repo)), BUNDLED)

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
