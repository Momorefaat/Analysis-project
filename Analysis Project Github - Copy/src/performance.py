import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import os
import numpy as np

def plot_performance(results_by_algo, output_dir='visualizations'):
    """Plot computational cost growth in 3D: nodes (x), edges (y), execution time (z)."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    markers = ['o', 's', '^', 'D', 'v']  # Different markers for each algorithm
    colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k']
    for idx, (algo_name, data) in enumerate(results_by_algo.items()):
        if not data:
            print(f"No data for {algo_name}, skipping plot.")
            continue
        dataset_names = [x[0] for x in data]
        nodes = [x[1] for x in data]
        edges = [x[2] for x in data]
        times = [x[3] for x in data]
        print(f"Plotting {algo_name}: {len(nodes)} points, Nodes={nodes}, Edges={edges}, Times={times}")
        # Sort by nodes for line connection
        sorted_indices = sorted(range(len(nodes)), key=lambda i: nodes[i])
        dataset_names_sorted = [dataset_names[i] for i in sorted_indices]
        nodes_sorted = [nodes[i] for i in sorted_indices]
        edges_sorted = [edges[i] for i in sorted_indices]
        times_sorted = [times[i] for i in sorted_indices]
        color = colors[idx % len(colors)]
        ax.scatter(nodes_sorted, edges_sorted, times_sorted, label=algo_name, marker=markers[idx % len(markers)], s=50, color=color)
        # Connect points with a dashed line
        ax.plot(nodes_sorted, edges_sorted, times_sorted, color=color, linewidth=1, linestyle='dashed')
        # Add text labels for dataset names
        for j, txt in enumerate(dataset_names_sorted):
            ax.text(nodes_sorted[j], edges_sorted[j], times_sorted[j] * 1.1, txt, fontsize=8, color=color)

    ax.set_xlabel('Number of Nodes')
    ax.set_ylabel('Number of Edges')
    ax.set_zlabel('Execution Time (seconds)')
    ax.set_zscale('log')  # Log scale for execution time to better visualize differences
    ax.set_title('Computational Cost Growth of Algorithms (3D)')
    if any(data for data in results_by_algo.values()):
        ax.legend()
    ax.grid(True)
    
    output_file = os.path.join(output_dir, 'performance_plot_3d.png')
    plt.savefig(output_file, dpi=300)
    plt.close()
    print(f'3D Performance plot saved: {output_file}')