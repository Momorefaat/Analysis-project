import time
import heapq
from graph_utils import validate_mst

def prim(G):
    start_time = time.perf_counter()
    if not G.nodes:
        return {
            'edges': [],
            'total_cost': 0.0,
            'execution_time': 0.0,
            'is_valid': False
        }

    start_node = next(iter(G.nodes))
    visited = set([start_node])
    edges = []
    mst_edges = []
    total_cost = 0.0

    for v, data in G[start_node].items():
        heapq.heappush(edges, (data.get('weight', 1.0), start_node, v))

    while edges and len(visited) < len(G.nodes):
        weight, u, v = heapq.heappop(edges)
        if v in visited:
            continue
        visited.add(v)
        mst_edges.append((u, v))
        total_cost += weight
        for neighbor, data in G[v].items():
            if neighbor not in visited:
                heapq.heappush(edges, (data.get('weight', 1.0), v, neighbor))

    is_valid, total_cost = validate_mst(G, mst_edges)
    execution_time = time.perf_counter() - start_time

    return {
        'edges': mst_edges,
        'total_cost': total_cost,
        'execution_time': execution_time,
        'is_valid': is_valid
    }