import argparse
import networkx as nx
import matplotlib.pyplot as plt
import os
from graph_handler import GraphHandler
from mibga import MIBGA

def visualize_paths(graph_handler, paths, S, T, show_background=True):
    G = graph_handler.graph
    if hasattr(graph_handler, 'pos') and graph_handler.pos:
        pos = graph_handler.pos
    else:
        pos = nx.spring_layout(G, seed=42)
    
    plt.figure(figsize=(10, 10))
    if G.number_of_nodes() > 1000 and show_background:
        print(f"Warning: Graph has {G.number_of_nodes()} nodes. Disabling background edges for performance.")
        show_background = False

    if show_background:
        nx.draw_networkx_edges(G, pos, edge_color='lightgray', alpha=0.5, width=0.5)
    else:
        nx.draw_networkx_nodes(G, pos, nodelist=[S, T], node_size=0, alpha=0) 

    colors = ['r', 'b', 'g', 'c', 'm', 'y']
    for i, path in enumerate(paths):
        color = colors[i % len(colors)]
        edge_list = list(zip(path.nodes[:-1], path.nodes[1:]))
        nx.draw_networkx_edges(G, pos, edgelist=edge_list, edge_color=color, width=3.0, label=f"Path {i+1}")
        # Gambar node kecil di sepanjang jalur
        nx.draw_networkx_nodes(G, pos, nodelist=path.nodes, node_size=20, node_color=color)

    # Highlight Start & Target
    nx.draw_networkx_nodes(G, pos, nodelist=[S], node_color='lime', node_size=200, label="Start")
    nx.draw_networkx_nodes(G, pos, nodelist=[T], node_color='black', node_size=200, label="Target")
    
    plt.title(f"MIBGA Result: K={len(paths)} Diverse Paths")
    plt.legend()
    plt.axis('off')
    plt.show()

def main():
    parser = argparse.ArgumentParser(description="MIBGA Application")
    parser.add_argument("graph_file", type=str, help="Path to Excel (.xlsx) or edgelist file")
    
    # Parameter optional
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

    # 2. LOGIKA MODE INSPEKSI (Jika user tidak isi -S atau -T)
    if args.start is None or args.target is None:
        filename = os.path.basename(args.graph_file)
        print("\n" + "="*50)
        print(f" INFO GRAF: {filename}")
        print("="*50)
        print(f"Total Nodes : {gh.graph.number_of_nodes()}")
        print(f"Total Edges : {gh.graph.number_of_edges()}")
        
        # Tampilkan sampel data jika ada mapping (Excel)
        if hasattr(gh, 'node_mapping') and gh.node_mapping:
            print("\n[SAMPEL NODE ID]")
            print("-" * 65)
            print(f"{'Koordinat (X, Y)':<45} | {'Node ID':<10}")
            print("-" * 65)
            
            count = 0
            # Ambil contoh Node ID pertama dan ke-6 untuk saran command
            sample_ids = list(gh.node_mapping.values())
            example_s = sample_ids[0] if len(sample_ids) > 0 else 0
            example_t = sample_ids[5] if len(sample_ids) > 5 else (sample_ids[-1] if sample_ids else 0)

            for coord, nid in gh.node_mapping.items():
                # Format koordinat 2 desimal agar rapi
                coord_str = f"({coord[0]:.2f}, {coord[1]:.2f})"
                print(f"{coord_str:<45} | {nid:<10}")
                
                count += 1
                if count >= 10: break
            print("-" * 65)
            
            print(f"\nTIP: Gunakan Node ID di atas.")
            print(f"Contoh Command: python main.py {args.graph_file} -S {example_s} -T {example_t}")
        else:
            print("\n[INFO] File Edgelist terdeteksi.")
            print("Node ID adalah angka integer yang ada di dalam file Anda.")
        
        return # Berhenti di sini, jangan jalankan algoritma

    # 3. LOGIKA MODE EKSEKUSI (Jika -S dan -T diisi)
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

    final_paths = mibga.run()

    print("\n--- MIBGA Run Complete ---")
    if not final_paths:
        print("No paths found meeting criteria.")
    else:
        visualize_paths(gh, final_paths, args.start, args.target)

if __name__ == "__main__":
    main()