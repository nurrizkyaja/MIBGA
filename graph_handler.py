import networkx as nx
import pandas as pd
import math
from typing import List, Dict, Tuple

class GraphHandler:
    def __init__(self, file_path: str):
        self.graph = nx.Graph()
        self.pos: Dict[int, Tuple[float, float]] = {} # Menyimpan koordinat asli (x,y)
        self.node_mapping: Dict[Tuple[float, float], int] = {} # Mapping (x,y) -> Node ID

        if file_path.endswith('.xlsx') or file_path.endswith('.xls'):
            self._load_from_excel(file_path)
        else:
            self._load_from_edgelist(file_path)
            
        print(f"Graph loaded: {self.graph.number_of_nodes()} nodes, {self.graph.number_of_edges()} edges.")

    def _load_from_excel(self, file_path: str):
        # Load Excel, asumsikan kolom index 0-4 (Start_X, Start_Y, End_X, End_Y, Dist)
        try:
            df = pd.read_excel(file_path, header=0)
        except Exception as e:
            print(f"Error reading Excel: {e}")
            return

        # Helper untuk konversi string angka koma ke float
        def clean_float(val):
            if isinstance(val, str):
                val = val.replace(',', '.')
            return float(val)

        next_node_id = 0
        
        for _, row in df.iterrows():
            try:
                # Ambil data raw
                sx, sy = clean_float(row.iloc[0]), clean_float(row.iloc[1])
                ex, ey = clean_float(row.iloc[2]), clean_float(row.iloc[3])
                dist = clean_float(row.iloc[4])
                
                start_coord = (sx, sy)
                end_coord = (ex, ey)

                # Assign Node ID untuk Start Node
                if start_coord not in self.node_mapping:
                    self.node_mapping[start_coord] = next_node_id
                    self.pos[next_node_id] = start_coord
                    next_node_id += 1
                
                # Assign Node ID untuk End Node
                if end_coord not in self.node_mapping:
                    self.node_mapping[end_coord] = next_node_id
                    self.pos[next_node_id] = end_coord
                    next_node_id += 1
                
                # Tambah Edge
                u = self.node_mapping[start_coord]
                v = self.node_mapping[end_coord]
                
                self.graph.add_edge(u, v, weight=dist)
                
            except ValueError:
                continue # Skip baris yang error/kosong

        # -- UPDATE: Baris ini dikomentari agar tidak print double di main menu --
        # self._save_mapping_info()

    def _save_mapping_info(self):
        # Method ini tetap ada jika sewaktu-waktu dibutuhkan untuk debug internal
        print("\n--- Coordinate to Node ID Mapping ---")
        for i, (coord, nid) in enumerate(self.node_mapping.items()):
            if i >= 5: break
            print(f"Coord {coord} -> Node ID: {nid}")

    def _load_from_edgelist(self, file_path: str):
        try:
            self.graph = nx.read_edgelist(file_path, nodetype=int, data=(("weight", float),))
        except TypeError:
            self.graph = nx.read_edgelist(file_path, nodetype=int)
            for (u, v) in self.graph.edges():
                self.graph[u][v]['weight'] = 1.0

    def get_edge_length(self, node_a: int, node_b: int) -> float:
        try:
            return self.graph[node_a][node_b]['weight']
        except KeyError:
            return float('inf')

    def get_neighbors(self, node: int) -> List[int]:
        return list(self.graph.neighbors(node))
    
    def get_all_nodes(self) -> List[int]:
        return list(self.graph.nodes())

    def get_shortest_path_length(self, S: int, T: int) -> float:
        try:
            return nx.shortest_path_length(self.graph, source=S, target=T, weight='weight')
        except nx.NetworkXNoPath:
            return float('inf')