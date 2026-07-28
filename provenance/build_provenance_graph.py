import json
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent

OUTPUT_FILE = (
    ROOT_DIR
    / "provenance"
    / "provenance_graph.json"
)


TARGETS = [
    "runs",
    "manifests",
    "telemetry",
    "analytics",
    "snapshots",
    "failure_atlas"
]


def collect_nodes():

    nodes = []

    for target in TARGETS:

        target_path = ROOT_DIR / target

        if not target_path.exists():
            continue

        for item in target_path.rglob("*"):

            if item.is_file():

                node = {
                    "id": str(item.relative_to(ROOT_DIR)),
                    "type": target,
                    "path": str(item)
                }

                nodes.append(node)

    return nodes


def build_edges(nodes):

    edges = []

    for node in nodes:

        if "manifest" in node["id"]:

            edges.append({
                "source": node["id"],
                "target": "runs",
                "relationship": "describes"
            })

        if "snapshot" in node["id"]:

            edges.append({
                "source": node["id"],
                "target": "execution_history",
                "relationship": "captures"
            })

        if "report" in node["id"]:

            edges.append({
                "source": node["id"],
                "target": "analytics",
                "relationship": "analyzes"
            })

    return edges


def save_graph(nodes, edges):

    graph = {
        "nodes": nodes,
        "edges": edges
    }

    with open(OUTPUT_FILE, "w") as f:
        json.dump(graph, f, indent=4)


def main():

    print("=" * 60)
    print("GLI-FLOW Provenance Graph Engine")
    print("=" * 60)

    nodes = collect_nodes()

    edges = build_edges(nodes)

    save_graph(nodes, edges)

    print(f"[NODES] {len(nodes)}")
    print(f"[EDGES] {len(edges)}")

    print("\n========================================")
    print("[SUCCESS] Provenance graph generated")
    print("========================================")


if __name__ == "__main__":
    main()
