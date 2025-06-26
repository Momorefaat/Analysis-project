import os
import imageio
import networkx as nx
from graph_utils import get_dataset_files, load_graph
from kruskal import kruskal
from prim import prim
from boruvka import boruvka
from reverse_delete import reverse_delete
from karger import karger
from visualize import visualize_mst_incremental
from performance import plot_performance
import traceback
from multiprocessing import Lock
from concurrent.futures import ProcessPoolExecutor, as_completed
from tqdm import tqdm
import random
import pickle
import threading
import time
import sys

tqdm_lock = Lock()

def spinner(msg, stop_event):
    import itertools
    spinner_cycle = itertools.cycle(['|', '/', '-', '\\'])
    start_time = time.time()
    while not stop_event.is_set():
        elapsed = int(time.time() - start_time)
        sys.stdout.write(f'\r{msg} {next(spinner_cycle)} Elapsed: {elapsed}s')
        sys.stdout.flush()
        time.sleep(0.2)
    sys.stdout.write('\r' + ' ' * 80 + '\r')

def run_algorithm(algo, G, dataset_name, algo_name, output_dir, num_nodes, num_edges, position, pos, complexity):
    """Run an algorithm and visualize its result, returning result data."""
    try:
        print(f'Running {algo_name} on {dataset_name}...')
        result = algo(G)
        if result is None:
            print(f"Error: {algo_name} on {dataset_name} returned None")
            return None
        if algo_name == 'Karger':
            print(f"{algo_name} - Cut Size: {result['total_cost']:.2f}, Time: {result['execution_time']:.4f}s")
        else:
            print(f"{algo_name} - Valid MST: {result['is_valid']}, Total Cost: {result['total_cost']:.2f}, Time: {result['execution_time']:.4f}s")
        visualize_mst_incremental(G, result['edges'], dataset_name, algo_name, output_dir, position, pos=pos, execution_time=result['execution_time'], complexity=complexity)
        return {'algo_name': algo_name, 'result': result, 'num_nodes': num_nodes, 'num_edges': num_edges}
    except Exception as e:
        print(f"Error running {algo_name} on {dataset_name}: {str(e)}")
        traceback.print_exc()
        return None

def main():
    data_dir = 'data'
    output_dir = 'visualizations'
    complexities = {
        'Kruskal': 'O(m log m)',
        'Prim': 'O(m log n)',
        'Boruvka': 'O(m log n)',
        'Reverse Delete': 'O(m (n + m))',
        'Karger': 'O(m)'
    }
    algorithms = [
        ('Kruskal', kruskal),
        ('Prim', prim),
        ('Boruvka', boruvka),
        ('Reverse Delete', reverse_delete),
        ('Karger', karger)
    ]
    algorithm_names = [name for name, _ in algorithms]

    # Load or initialize results for performance persistence
    results_file = os.path.join(output_dir, 'results.pkl')
    if os.path.exists(results_file):
        with open(results_file, 'rb') as f:
            results_by_algo = pickle.load(f)
    else:
        results_by_algo = {name: [] for name in algorithm_names}

    dataset_files = list(get_dataset_files(data_dir))

    # Maintain order: smallest to largest based on your datasets
    preferred_order = [
        "web-edu",      
        "web-spam",   
        "inf-euroroad",     
        "power-US-Grid",    
        "power-bcspwr10"    
    ]
    def dataset_sort_key(path):
        base = os.path.basename(path).split('.')[0]
        try:
            return preferred_order.index(base)
        except ValueError:
            return len(preferred_order)  # Put unknowns at the end

    dataset_files.sort(key=dataset_sort_key)

    with tqdm(total=len(dataset_files), desc="Processing datasets", unit="dataset") as dataset_pbar:
        for dataset in dataset_files:
            dataset_name = os.path.basename(dataset).split('.')[0]
            print(f'\nProcessing {dataset_name}...')
            G = load_graph(dataset)
            num_nodes = len(G.nodes)
            num_edges = len(G.edges)
            print(f"{dataset_name}: Nodes={num_nodes}, Edges={num_edges}")

            # Load or compute layout with caching and error handling
            pos_file = os.path.join(output_dir, f'{dataset_name}_pos.pkl')
            pos = None
            if os.path.exists(pos_file):
                try:
                    with open(pos_file, 'rb') as f:
                        pos = pickle.load(f)
                    print(f"Loaded cached layout for {dataset_name}")
                except (EOFError, pickle.UnpicklingError) as e:
                    print(f"Error loading {pos_file}: {e}. Recomputing layout...")
                    pos = None

            if pos is None:
                print("Calculating layout (kamada_kawai_layout)...")
                stop_event = threading.Event()
                t = threading.Thread(target=spinner, args=("Calculating layout", stop_event))
                t.start()
                start = time.time()
                # Compute initial positions with spring_layout for speed
                init_pos = nx.spring_layout(G, iterations=10, seed=42)
                # Refine with Kamada-Kawai
                pos = nx.kamada_kawai_layout(G, pos=init_pos)
                stop_event.set()
                t.join()
                print(f"Layout done in {time.time() - start:.1f} seconds.")
                with open(pos_file, 'wb') as f:
                    pickle.dump(pos, f)
                print(f"Saved layout to {pos_file}")

            with tqdm_lock:
                layout_pbar = tqdm(total=1, desc=f"Layout for {dataset_name}", unit="step", position=1, leave=False)
                layout_pbar.update(1)
                layout_pbar.close()

            # Run algorithms with progress bar
            with tqdm(total=len(algorithms), desc=f"Algorithms for {dataset_name}", unit="algo", position=2, leave=False) as algo_pbar:
                futures = {}
                with ProcessPoolExecutor(max_workers=4) as executor:
                    for i, (algo_name, algo) in enumerate(algorithms):
                        mp4_path = os.path.join(output_dir, f"{dataset_name}_{algo_name}.mp4")
                        png_path = os.path.join(output_dir, f"{dataset_name}_{algo_name}_final.png")
                        if os.path.exists(mp4_path) and os.path.exists(png_path):
                            print(f"Skipping {algo_name} on {dataset_name} (MP4 and PNG already exist).")
                            # Check if result exists in results_by_algo
                            existing = [r for r in results_by_algo[algo_name] if r[0] == num_nodes and r[1] == num_edges]
                            if not existing:
                                print(f"Running {algo_name} to collect missing performance data...")
                                G_copy = nx.Graph(G)
                                future = executor.submit(
                                    run_algorithm, algo, G_copy, dataset_name, algo_name, output_dir, num_nodes, num_edges, i, pos, complexities[algo_name]
                                )
                                futures[future] = algo_name
                            else:
                                algo_pbar.update(1)
                                continue
                        else:
                            G_copy = nx.Graph(G)
                            future = executor.submit(
                                run_algorithm, algo, G_copy, dataset_name, algo_name, output_dir, num_nodes, num_edges, i, pos, complexities[algo_name]
                            )
                            futures[future] = algo_name

                    for future in as_completed(futures):
                        algo_name = futures[future]
                        result_data = future.result()
                        if result_data and result_data['result']:
                            results_by_algo[algo_name].append((
                                result_data['num_nodes'],
                                result_data['num_edges'],
                                result_data['result']['execution_time']
                            ))
                            print(f"Stored result for {algo_name} on {dataset_name}: Nodes={num_nodes}, Edges={num_edges}, Time={result_data['result']['execution_time']:.4f}s")
                        else:
                            print(f"No result stored for {algo_name} on {dataset_name}")
                        with tqdm_lock:
                            algo_pbar.update(1)

            G.clear()
            with tqdm_lock:
                dataset_pbar.update(1)

    # Save performance results with progress
    print("\nGenerating performance plot...")
    with tqdm(total=1, desc="Generating performance plot", unit="step") as plot_pbar:
        with open(results_file, 'wb') as f:
            pickle.dump(results_by_algo, f)
        print("Results before plotting:", {k: len(v) for k, v in results_by_algo.items()})
        plot_performance(results_by_algo, output_dir)
        plot_pbar.update(1)

    print("\nAll datasets processed.")

if __name__ == '__main__':
    main()