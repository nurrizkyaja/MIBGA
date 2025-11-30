import argparse
import networkx as nx
import plotly.graph_objects as go
import os
import random
from graph_handler import GraphHandler
from mibga import MIBGA

def visualize_paths_plotly(graph_handler, final_paths, candidate_paths, S, T):
    """
    Visualisasi Interaktif menggunakan Plotly.
    """
    G = graph_handler.graph
    pos = graph_handler.pos if graph_handler.pos else nx.spring_layout(G, seed=42)
    
    fig = go.Figure()

    # --- 1. Background Edges (Semua Jalan) ---
    edge_x = []
    edge_y = []
    # Agar ringan, jika node > 2000, gambar background sebagian atau tipis
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    fig.add_trace(go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#e0e0e0'),
        hoverinfo='none',
        mode='lines',
        name='Road Network'
    ))

    # --- 2. Candidate Paths (Swarm - Optional) ---
    # Sample untuk mengurangi beban rendering
    sample_cands = random.sample(candidate_paths, min(len(candidate_paths), 50))
    cand_x = []
    cand_y = []
    for p in sample_cands:
        nodes = p.nodes
        for i in range(len(nodes)-1):
            x0, y0 = pos[nodes[i]]
            x1, y1 = pos[nodes[i+1]]
            cand_x.extend([x0, x1, None])
            cand_y.extend([y0, y1, None])
            
    fig.add_trace(go.Scatter(
        x=cand_x, y=cand_y,
        line=dict(width=1, color='rgba(150, 150, 150, 0.3)'),
        hoverinfo='none',
        mode='lines',
        name='Candidate Paths (Sample)'
    ))

    # --- 3. Final K-Most Diverse Paths ---
    colors = ['#EF553B', '#636EFA', '#00CC96', '#AB63FA', '#FFA15A', '#19D3F3']
    
    for i, path in enumerate(final_paths):
        path_x = []
        path_y = []
        nodes = path.nodes
        for node in nodes:
            path_x.append(pos[node][0])
            path_y.append(pos[node][1])
            
        color = colors[i % len(colors)]
        
        # Gambar Garis Jalur
        fig.add_trace(go.Scatter(
            x=path_x, y=path_y,
            line=dict(width=4, color=color),
            mode='lines+markers',
            marker=dict(size=4),
            name=f'Path {i+1} (Len: {path.length:.2f})',
            hoverinfo='name+text',
            text=[f"Node {n}" for n in nodes]
        ))

    # --- 4. Start & Target Nodes ---
    start_pos = pos[S]
    target_pos = pos[T]
    
    fig.add_trace(go.Scatter(
        x=[start_pos[0], target_pos[0]],
        y=[start_pos[1], target_pos[1]],
        mode='markers',
        marker=dict(size=15, color=['green', 'black'], symbol='star'),
        text=['START', 'TARGET'],
        hoverinfo='text',
        name='Endpoints'
    ))

    fig.update_layout(
        title=f"MIBGA Result: {len(final_paths)} Most Diverse Near-Shortest Paths",
        showlegend=True,
        plot_bgcolor='white',
        hovermode='closest',
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
    )
    
    fig.show()

def main():
    parser = argparse.ArgumentParser(description="MIBGA Application")
    parser.add_argument("graph_file", type=str, help="Path to Excel (.xlsx), CSV (.csv) or edgelist file")
    
    parser.add_argument("-S", "--start", type=int, required=False, help="Source Node ID")
    parser.add_argument("-T", "--target", type=int, required=False, help="Target Node ID")
    parser.add_argument("-K", "--k_paths", type=int, default=3, help="K paths")
    parser.add_argument("-e", "--epsilon", type=float, default=0.2, help="Epsilon threshold")
    
    args = parser.parse_args()

    if not os.path.exists(args.graph_file):
        print(f"\n[ERROR] File tidak ditemukan: {args.graph_file}")
        return

    # 1. Load Graph
    try:
        gh = GraphHandler(args.graph_file)
    except Exception as e:
        print(f"Error loading graph: {e}")
        return

    # 2. LOGIKA MODE INSPEKSI (Jika user tidak memberi argumen S dan T)
    if args.start is None or args.target is None:
        filename = os.path.basename(args.graph_file)
        print("\n" + "="*50)
        print(f" INFO GRAF: {filename}")
        print("="*50)
        print(f"Total Nodes : {gh.graph.number_of_nodes()}")
        print(f"Total Edges : {gh.graph.number_of_edges()}")
        
        if hasattr(gh, 'node_mapping') and gh.node_mapping:
            print("\n[SAMPEL NODE ID]")
            print("-" * 65)
            print(f"{'Koordinat (X, Y)':<45} | {'Node ID':<10}")
            print("-" * 65)
            
            count = 0
            sample_ids = list(gh.node_mapping.values())
            example_s = sample_ids[0] if len(sample_ids) > 0 else 0
            example_t = sample_ids[5] if len(sample_ids) > 5 else (sample_ids[-1] if sample_ids else 0)

            for coord, nid in gh.node_mapping.items():
                coord_str = f"({coord[0]:.2f}, {coord[1]:.2f})"
                print(f"{coord_str:<45} | {nid:<10}")
                count += 1
                if count >= 10: break
            print("-" * 65)
            
            print(f"\nTIP: Gunakan Node ID di atas.")
            print(f"Contoh Command: python main.py \"{args.graph_file}\" -S {example_s} -T {example_t}")
        else:
            print("\n[INFO] File Edgelist terdeteksi.")
            print("Node ID adalah angka integer yang ada di dalam file Anda.")
        return

    # 3. LOGIKA MODE EKSEKUSI
    all_nodes = gh.get_all_nodes()
    if args.start not in all_nodes:
        print(f"[ERROR] Start Node ID ({args.start}) tidak ditemukan di dalam data.")
        return
    if args.target not in all_nodes:
        print(f"[ERROR] Target Node ID ({args.target}) tidak ditemukan di dalam data.")
        return

    print(f"\n[RUNNING] Menjalankan MIBGA dari Node {args.start} ke {args.target}...")
    
    mibga = MIBGA(
        graph_handler=gh,
        S_node=args.start,
        T_node=args.target,
        K_paths=args.k_paths,
        epsilon_threshold=args.epsilon
    )

    all_candidates, final_paths = mibga.run()

    print("\n--- MIBGA Run Complete ---")
    if not final_paths:
        print("No paths found meeting criteria.")
    else:
        # Panggil Visualisasi Plotly
        visualize_paths_plotly(gh, final_paths, all_candidates, args.start, args.target)

if __name__ == "__main__":
    main()