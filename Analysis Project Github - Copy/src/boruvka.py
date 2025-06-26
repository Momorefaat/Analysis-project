import time
from graph_utils import DisjointSet, validate_mst

def boruvka(G):
    start_time = time.perf_counter()
    if not G.nodes:
        return {
            'edges': [],
            'total_cost': 0.0,
            'execution_time': 0.0,
            'is_valid': False
        }

    ds = DisjointSet(len(G.nodes))
    mst_edges = []
    num_components = len(G.nodes)

    while num_components > 1:
        cheapest = {i: None for i in range(len(G.nodes))}
        for u, v, data in G.edges(data=True):
            pu, pv = ds.find(u), ds.find(v)
            if pu != pv:
                weight = data.get('weight', 1.0)
                if cheapest[pu] is None or weight < cheapest[pu][0]:
                    cheapest[pu] = (weight, u, v)
                if cheapest[pv] is None or weight < cheapest[pv][0]:
                    cheapest[pv] = (weight, u, v)

        added = False
        for node in range(len(G.nodes)):
            if cheapest[node] is not None:
                weight, u, v = cheapest[node]
                if ds.union(u, v):
                    mst_edges.append((u, v))
                    num_components -= 1
                    added = True
        if not added:
            break

    is_valid, total_cost = validate_mst(G, mst_edges)
    execution_time = time.perf_counter() - start_time

    return {
        'edges': mst_edges,
        'total_cost': total_cost,
        'execution_time': execution_time,
        'is_valid': is_valid
    }