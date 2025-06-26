import networkx as nx
import os
import random

class DisjointSet:
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n

    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x, y):
        px, py = self.find(x), self.find(y)
        if px == py:
            return False
        if self.rank[px] < self.rank[py]:
            px, py = py, px
        self.parent[py] = px
        if self.rank[px] == self.rank[py]:
            self.rank[px] += 1
        return True

def load_graph(file_path):
    """Load a weighted, undirected graph from .edges or .mtx file with node remapping.
    If weights are missing, assign random weights between 0 and 100."""
    G = nx.Graph()
    node_map = {}
    next_id = 0
    has_negative_weights = False

    if file_path.endswith('.edges'):
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#') or line.startswith('%'):
                    continue
                parts = line.split()
                if len(parts) >= 2:
                    u, v = int(parts[0]), int(parts[1])
                    if len(parts) >= 3:
                        w = float(parts[2])
                    else:
                        w = random.uniform(0, 100)  # Assign random weight if missing
                    if w < 0:
                        w = -w  # Convert negative weights to positive
                        has_negative_weights = True
                    if u not in node_map:
                        node_map[u] = next_id
                        next_id += 1
                    if v not in node_map:
                        node_map[v] = next_id
                        next_id += 1
                    G.add_edge(node_map[u], node_map[v], weight=w)
    elif file_path.endswith('.mtx'):
        with open(file_path, 'r') as f:
            lines = [line.strip() for line in f if line.strip() and not line.startswith('%')]
            if lines:
                for line in lines[1:]:
                    parts = line.split()
                    if len(parts) >= 2:
                        u, v = int(parts[0]), int(parts[1])
                        if len(parts) >= 3:
                            w = float(parts[2])
                        else:
                            w = random.uniform(0, 100)  # Assign random weight if missing
                        if w < 0:
                            w = -w  # Convert negative weights to positive
                            has_negative_weights = True
                        u, v = u - 1, v - 1  # Adjust for 1-indexing
                        if u not in node_map:
                            node_map[u] = next_id
                            next_id += 1
                        if v not in node_map:
                            node_map[v] = next_id
                            next_id += 1
                        G.add_edge(node_map[u], node_map[v], weight=w)

    if has_negative_weights:
        print(f"Warning: Negative weights detected in {file_path}. Converted to positive by multiplying by -1.")

    if not nx.is_connected(G):
        print(f"Warning: Graph from {file_path} is not connected. Using largest component.")
        G = G.subgraph(max(nx.connected_components(G), key=len)).copy()

    G = nx.convert_node_labels_to_integers(G, first_label=0)
    return G

def validate_mst(G, mst_edges):
    """Validate MST by checking if it forms a tree and computing total cost."""
    if not mst_edges:
        return False, 0.0
    mst = nx.Graph()
    mst.add_edges_from(mst_edges)
    total_cost = sum(G[u][v].get('weight', 1.0) for u, v in mst_edges)
    is_tree = nx.is_tree(mst) and len(mst.nodes) == len(G.nodes)
    return is_tree, total_cost

def get_dataset_files(data_dir):
    """Get list of dataset files (.edges or .mtx) in data directory."""
    return [os.path.join(data_dir, f) for f in os.listdir(data_dir) if f.endswith('.edges') or f.endswith('.mtx')]