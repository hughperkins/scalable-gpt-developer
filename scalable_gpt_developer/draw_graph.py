import json
import argparse
import networkx as nx
import matplotlib.pyplot as plt


def draw_dependency_graph(filepath):
    with open(filepath, "r") as file:
        data = json.load(file)

    G = nx.DiGraph()

    for component, info in data.items():
        G.add_node(component, description=info["description"])

        for dependency in info["uses"]:
            G.add_edge(component, dependency)

    # other layouts:
    # `circular_layout`, `random_layout`, `shell_layout`, and `spectral_layout`, `spring_layout`
    pos = nx.spring_layout(G)
    plt.figure(figsize=(12, 8))

    nx.draw(G, pos, with_labels=True, font_weight="bold", node_size=1000, node_color="skyblue", font_size=10)
    nx.draw_networkx_edge_labels(G, pos, font_size=8, edge_labels={(u, v): "uses" for u, v in G.edges()})

    plt.savefig("dependency_graph.png")
    plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--file-path', type=str, required=True)
    args = parser.parse_args()
    draw_dependency_graph(args.file_path)
