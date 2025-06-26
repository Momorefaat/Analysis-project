import time
from graph_utils import DisjointSet, validate_mst

def kruskal(G):
    start_time = time.perf_counter()
    ds = DisjointSet(len(G.nodes))
    edges = sorted(G.edges(data=True), key=lambda x: x[2].get('weight', 1.0))
    mst_edges = []

    for u, v, data in edges:
        if ds.union(u, v):
            mst_edges.append((u, v))

    is_valid, total_cost = validate_mst(G, mst_edges)
    execution_time = time.perf_counter() - start_time

    return {
        'edges': mst_edges,
        'total_cost': total_cost,
        'execution_time': execution_time,
        'is_valid': is_valid
    }