import time
import random
from graph_utils import DisjointSet
from tqdm import tqdm
import networkx as nx
from multiprocessing import Lock

tqdm_lock = Lock()

def karger(G, seed=None):
    """Karger's algorithm for min-cut, optimized with progress tracking."""
    start_time = time.perf_counter()
    if seed is not None:
        random.seed(seed)

    if not G.edges:
        return {
            'edges': [],
            'total_cost': 0.0,
            'execution_time': time.perf_counter() - start_time,
            'is_valid': False
        }

    best_cut_size = float('inf')
    best_cut_edges = []
    num_runs = 5

    with tqdm_lock:
        pbar = tqdm(total=num_runs, desc="Running Karger", unit="iteration", position=0, leave=True, ascii=True)

    for _ in range(num_runs):
        H = G.copy()
        ds = DisjointSet(len(H.nodes))
        num_nodes = len(H.nodes)

        while num_nodes > 2:
            valid_edges = [(u, v) for u, v in H.edges() if ds.find(u) != ds.find(v)]
            if not valid_edges:
                break
            u, v = random.choice(valid_edges)
            ds.union(u, v)
            for neighbor in list(H.neighbors(v)):
                if neighbor != u:
                    weight = H[v][neighbor].get('weight', 1.0)
                    if H.has_edge(u, neighbor):
                        H[u][neighbor]['weight'] = H[u][neighbor].get('weight', 1.0) + weight
                    else:
                        H.add_edge(u, neighbor, weight=weight)
            H.remove_node(v)
            num_nodes -= 1

        components = {}
        for node in G.nodes():
            root = ds.find(node)
            if root not in components:
                components[root] = []
            components[root].append(node)

        if len(components) != 2:
            pbar.update(1)
            continue

        set1, set2 = list(components.values())
        cut_edges = []
        cut_size = 0.0
        for u in set1:
            for v in G.neighbors(u):
                if v in set2:
                    cut_edges.append((u, v))
                    cut_size += G[u][v].get('weight', 1.0)

        # Accept negative cut_size as best if it's the minimum found
        if best_cut_edges == [] or cut_size < best_cut_size:
            best_cut_size = cut_size
            best_cut_edges = cut_edges

        pbar.update(1)

    pbar.close()
    execution_time = time.perf_counter() - start_time

    return {
        'edges': best_cut_edges,
        'total_cost': best_cut_size,  # Always show the actual cut size, even if negative
        'execution_time': execution_time,
        'is_valid': bool(best_cut_edges)
    }