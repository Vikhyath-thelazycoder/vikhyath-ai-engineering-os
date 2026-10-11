"""Runs INSIDE the isolated Graphify venv (`python -I graphify_probe.py`): affected files for changed paths, as JSON.

Uses Graphify's own seed resolution and reverse traversal (graphify.affected); stdlib + graphify only, so it never
imports the agylite package. argv: graph.json root depth path...
"""
import json
import sys
from pathlib import Path

from graphify.affected import DEFAULT_AFFECTED_RELATIONS, affected_nodes, load_graph, resolve_seed


def main(argv):
    graph_path, root, depth, paths = Path(argv[0]), Path(argv[1]), int(argv[2]), argv[3:]
    graph = load_graph(graph_path)
    by_file = {}
    for node_id, data in graph.nodes(data=True):
        by_file.setdefault(str(data.get("source_file") or ""), []).append(str(node_id))
    files, unresolved = {}, []
    for path in paths:
        seeds = by_file.get(path) or [s for s in [resolve_seed(graph, path, root)] if s]
        if not seeds:
            unresolved.append(path)
            continue
        for seed in seeds:
            for hit in affected_nodes(graph, seed, relations=DEFAULT_AFFECTED_RELATIONS, depth=depth):
                src = str(graph.nodes[hit.node_id].get("source_file") or "")
                if not src or src in paths:
                    continue
                prev = files.get(src)
                if prev is None or hit.depth < prev["depth"]:
                    files[src] = {"depth": hit.depth, "relation": hit.via_relation, "via": path,
                                  "location": f"{hit.via_file or src}:{hit.via_location}" if hit.via_location else src}
    json.dump({"nodes": graph.number_of_nodes(), "edges": graph.number_of_edges(), "affected": files,
               "unresolved": unresolved}, sys.stdout)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
