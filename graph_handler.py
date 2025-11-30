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
        elif file_path.endswith('.csv'):
            self._load_from_csv(file_path)
        else:
            self._load_from_edgelist(file_path)
            
        print(f"Graph loaded: {self.graph.number_of_nodes()} nodes, {self.graph.number_of_edges()} edges.")

    def _process_dataframe(self, df):
        # Helper untuk konversi string angka koma ke float
        def clean_float(val):
            if isinstance(val, str):
                val = val.replace(',', '.')
            return float(val)

        next_node_id = 0
        
        # Deteksi nama kolom (adaptasi untuk variasi format)
        cols = df.columns.str.lower()
        if 'startnode_x' in cols: # Format CSV Arizona
            c_sx, c_sy = 'startnode_x', 'startnode_y'
            c_ex, c_ey = 'endnode_x', 'endnode_y'
            c_dist = 'distance'
        else: # Asumsi kolom index 0-4 (Format Excel default)
            c_sx, c_sy = df.columns[0], df.columns[1]
            c_ex, c_ey = df.columns[2], df.columns[3]
            c_dist = df.columns[4]

        for _, row in df.iterrows():
            try:
                sx, sy = clean_float(row[c_sx]), clean_float(row[c_sy])
                ex, ey = clean_float(row[c_ex]), clean_float(row[c_ey])
                dist = clean_float(row[c_dist])
                
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
                
            except (ValueError, KeyError):
                continue

    def _load_from_excel(self, file_path: str):
        try:
            df = pd.read_excel(file_path, header=0)
            self._process_dataframe(df)
        except Exception as e:
            print(f"Error reading Excel: {e}")

    def _load_from_csv(self, file_path: str):
        try:
            df = pd.read_csv(file_path, header=0)
            self._process_dataframe(df)
        except Exception as e:
            print(f"Error reading CSV: {e}")

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