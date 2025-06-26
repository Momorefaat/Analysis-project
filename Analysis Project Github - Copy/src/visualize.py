import os
import imageio
import networkx as nx
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from tqdm import tqdm
import uuid
import random
from multiprocessing import Lock
import sys
import time
import threading
from graph_utils import DisjointSet

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
    sys.stdout.write('\r' + ' ' * 60 + '\r')

def visualize_mst_incremental(G, edges, dataset_name, algo_name, output_dir='visualizations', position=0, pos=None, execution_time=None, complexity=None):
    """Generate an MP4 video showing incremental construction with a clear progress bar."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    temp_file = f'temp_{uuid.uuid4().hex}.png'
    output_path = os.path.join(output_dir, f'{dataset_name}_{algo_name}.mp4')
    
    num_nodes = len(G.nodes)
    num_edges = len(edges)
    
    # Ensure 1000 frames for all videos, unless too few edges
    total_frames = 1000
    fps = 10
    if algo_name == 'Karger':
        contraction_frames = 100  # Show 100 contraction steps
        final_frames = total_frames - contraction_frames
        sampling_rate = 1  # Not used for Karger
        total_frames_to_render = contraction_frames + final_frames
    else:
        # If too few edges, use one frame per edge plus initial/final
        if len(edges) + 2 < total_frames:
            total_frames_to_render = len(edges) + 2
            sampling_rate = 1
        else:
            incremental_frames = total_frames - 2  # 998 frames (initial + final)
            sampling_rate = max(1, len(edges) // incremental_frames) if len(edges) > 0 else 1
            total_frames_to_render = (len(edges) // sampling_rate) + 2 if len(edges) > 0 else 2

    node_size = 5 if num_nodes < 10000 else 1
    dpi = 100 if num_nodes < 10000 else 50

    print(f"\nStarting MP4 generation for {dataset_name}_{algo_name}: nodes={num_nodes}, edges={num_edges}, sampling_rate={sampling_rate}")

    # Use provided pos (Kamada-Kawai from main.py)
    if pos is None:
        print("Layout not provided, using default kamada_kawai_layout...")
        stop_event = threading.Event()
        t = threading.Thread(target=spinner, args=("Calculating fallback layout", stop_event))
        t.start()
        start = time.time()
        pos = nx.kamada_kawai_layout(G)
        stop_event.set()
        t.join()
        print(f"Fallback layout done in {time.time() - start:.1f} seconds.")
    sys.stdout.flush()
    
    if len(G.edges) > 10000:
        bg_edges = random.sample(list(G.edges), min(10000, len(G.edges)))
    else:
        bg_edges = list(G.edges)
    
    writer = imageio.get_writer(output_path, format='FFMPEG', mode='I', fps=fps, codec='libx264', macro_block_size=16)
    
    # Simulate live running time based on execution_time
    execution_time = execution_time if execution_time is not None else 0.0
    complexity_str = f" ({complexity})" if complexity else ""

    # Initial frame
    plt.figure(figsize=(10.08, 8))
    nx.draw_networkx_nodes(G, pos, node_size=node_size, node_color='black')
    nx.draw_networkx_edges(G, pos, edgelist=bg_edges, edge_color='gray', width=0.5)
    title_prefix = "Cut Size" if algo_name == 'Karger' else "Cost"
    plt.title(f"{algo_name}{complexity_str} on {dataset_name}\n{title_prefix}: 0.00, Time: 0.0000s")
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(temp_file, dpi=dpi)
    plt.close()
    writer.append_data(imageio.imread(temp_file, format='PNG-PIL'))

    # Video rendering progress bar
    with tqdm(total=total_frames_to_render, desc=f"Rendering {algo_name} video for {dataset_name}", unit="frame", position=position, leave=True, ascii=True) as video_pbar:

        total_cost = 0
        valid_edges = [(u, v) for u, v in edges if G.has_edge(u, v) or G.has_edge(v, u)]

        if algo_name == 'Karger':
            # Karger's contraction visualization
            H = G.copy()
            ds = DisjointSet(len(H.nodes))
            contraction_steps = contraction_frames
            step = max(1, (len(H.nodes) - 2) // contraction_steps) if len(H.nodes) > 2 else 1
            contractions = 0
            i = 0
            frame_count = 0
            while len(H.nodes) > 2 and contractions < contraction_steps:
                valid_edges_temp = [(u, v) for u, v in H.edges() if ds.find(u) != ds.find(v)]
                if not valid_edges_temp:
                    break
                u, v = random.choice(valid_edges_temp)
                ds.union(u, v)
                for neighbor in list(H.neighbors(v)):
                    if neighbor != u:
                        weight = H[v][neighbor].get('weight', 1.0)
                        if H.has_edge(u, neighbor):
                            H[u][neighbor]['weight'] = H[u][neighbor].get('weight', 1.0) + weight
                        else:
                            H.add_edge(u, neighbor, weight=weight)
                H.remove_node(v)
                i += 1
                if i % step == 0 or len(H.nodes) == 2:
                    contractions += 1
                    frame_count += 1
                    # Simulate live running time
                    live_time = execution_time * (frame_count / total_frames_to_render)
                    plt.figure(figsize=(10.08, 8))
                    nx.draw_networkx_nodes(H, pos, node_size=node_size, node_color='black')
                    nx.draw_networkx_edges(H, pos, edgelist=H.edges(), edge_color='gray', width=0.5)
                    plt.title(f"{algo_name}{complexity_str} on {dataset_name}\nContraction Step {contractions}, Time: {live_time:.4f}s")
                    plt.axis('off')
                    plt.tight_layout()
                    plt.savefig(temp_file, dpi=dpi)
                    plt.close()
                    writer.append_data(imageio.imread(temp_file, format='PNG-PIL'))
                    video_pbar.update(1)
            # Show final min-cut edges for the remaining frames
            for _ in range(final_frames):
                frame_count += 1
                live_time = execution_time * (frame_count / total_frames_to_render)
                plt.figure(figsize=(10.08, 8))
                nx.draw_networkx_nodes(G, pos, node_size=node_size, node_color='black')
                non_edges = [e for e in bg_edges if e not in valid_edges and (e[1], e[0]) not in valid_edges]
                if len(non_edges) > 10000:
                    non_edges = random.sample(non_edges, min(10000, len(non_edges)))
                nx.draw_networkx_edges(G, pos, edgelist=non_edges, edge_color='red', width=0.5)
                nx.draw_networkx_edges(G, pos, edgelist=valid_edges, edge_color='blue', width=1.5)
                total_cost = sum(G[u][v].get('weight', 1.0) for u, v in valid_edges if G.has_edge(u, v))
                plt.title(f"{algo_name}{complexity_str} on {dataset_name}\nFinal {title_prefix}: {total_cost:.2f}, Time: {live_time:.4f}s")
                plt.axis('off')
                plt.tight_layout()
                plt.savefig(temp_file, dpi=dpi)
                plt.close()
                writer.append_data(imageio.imread(temp_file, format='PNG-PIL'))
                video_pbar.update(1)
        else:
            # MST visualization with progressive weight
            frames_added = 0
            for i, (u, v) in enumerate(valid_edges, 1):
                total_cost += G[u][v].get('weight', 1.0) if G.has_edge(u, v) else G[v][u].get('weight', 1.0)
                if i % sampling_rate == 0 or i == len(valid_edges):
                    frames_added += 1
                    # Simulate live running time
                    live_time = execution_time * (frames_added / total_frames_to_render)
                    current_edges = valid_edges[:i]
                    plt.figure(figsize=(10.08, 8))
                    nx.draw_networkx_nodes(G, pos, node_size=node_size, node_color='black')
                    nx.draw_networkx_edges(G, pos, edgelist=bg_edges, edge_color='gray', width=0.5)
                    nx.draw_networkx_edges(G, pos, edgelist=current_edges, edge_color='blue', width=1.5)
                    plt.title(f"{algo_name}{complexity_str} on {dataset_name}\n{title_prefix}: {total_cost:.2f}, Time: {live_time:.4f}s")
                    plt.axis('off')
                    plt.tight_layout()
                    plt.savefig(temp_file, dpi=dpi)
                    plt.close()
                    writer.append_data(imageio.imread(temp_file, format='PNG-PIL'))
                    video_pbar.update(1)

            # If fewer than total_frames_to_render-2 frames, repeat the last frame
            while frames_added < total_frames_to_render - 2:
                frames_added += 1
                live_time = execution_time * (frames_added / total_frames_to_render)
                plt.figure(figsize=(10.08, 8))
                nx.draw_networkx_nodes(G, pos, node_size=node_size, node_color='black')
                nx.draw_networkx_edges(G, pos, edgelist=bg_edges, edge_color='gray', width=0.5)
                nx.draw_networkx_edges(G, pos, edgelist=valid_edges, edge_color='blue', width=1.5)
                plt.title(f"{algo_name}{complexity_str} on {dataset_name}\n{title_prefix}: {total_cost:.2f}, Time: {live_time:.4f}s")
                plt.axis('off')
                plt.tight_layout()
                plt.savefig(temp_file, dpi=dpi)
                plt.close()
                writer.append_data(imageio.imread(temp_file, format='PNG-PIL'))
                video_pbar.update(1)

        # Final frame
        live_time = execution_time  # Final frame shows actual execution time
        plt.figure(figsize=(10.08, 8))
        nx.draw_networkx_nodes(G, pos, node_size=node_size, node_color='black')
        non_edges = [e for e in bg_edges if e not in valid_edges and (e[1], e[0]) not in valid_edges]
        if len(non_edges) > 10000:
            non_edges = random.sample(non_edges, min(10000, len(non_edges)))
        nx.draw_networkx_edges(G, pos, edgelist=non_edges, edge_color='red', width=0.5)
        nx.draw_networkx_edges(G, pos, edgelist=valid_edges, edge_color='blue', width=1.5)
        if algo_name == 'Karger':
            total_cost = sum(G[u][v].get('weight', 1.0) for u, v in valid_edges if G.has_edge(u, v))
        title = f"{algo_name}{complexity_str} Final on {dataset_name}\nFinal {title_prefix}: {total_cost:.2f}, Time: {live_time:.4f}s"
        plt.title(title)
        plt.axis('off')
        plt.tight_layout()
        plt.savefig(temp_file, dpi=dpi)
        final_frame_path = os.path.join(output_dir, f'{dataset_name}_{algo_name}_final.png')
        plt.savefig(final_frame_path, dpi=dpi)
        print(f"Final frame saved: {final_frame_path}")
        plt.close()
        writer.append_data(imageio.imread(temp_file, format='PNG-PIL'))
        video_pbar.update(1)
    
    writer.close()
    os.remove(temp_file)
    
    print(f"MP4 saved: {output_path}")