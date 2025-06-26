import time
import networkx as nx
from graph_utils import DisjointSet, validate_mst

def reverse_delete(G):
    start_time = time.perf_counter()
    edges = sorted(G.edges(data=True), key=lambda x: x[2].get('weight', 1.0), reverse=True)
    mst = G.copy()
    mst_edges = list(mst.edges())

    for u, v, data in edges:
        mst.remove_edge(u, v)
        components = list(nx.connected_components(mst))
        if len(components) > 1:
            mst.add_edge(u, v, weight=data.get('weight', 1.0))
        else:
            mst_edges.remove((u, v) if (u, v) in mst_edges else (v, u))

    is_valid, total_cost = validate_mst(G, mst_edges)
    execution_time = time.perf_counter() - start_time

    return {
        'edges': mst_edges,
        'total_cost': total_cost,
        'execution_time': execution_time,
        'is_valid': is_valid
    }