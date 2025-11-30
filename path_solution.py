from __future__ import annotations
from typing import List, Optional
import random

class PathSolution:
    def __init__(self, nodes: List[int], graph_handler):
        self.graph = graph_handler
        self.nodes = nodes
        self.length = 0.0
        self.fitness = 0.0

    def mend_path(self) -> None:
        # Implementasi Mending Function
        if not self.nodes:
            return
            
        new_path = []
        visited = {} # Node -> Index di new_path
        
        for node in self.nodes:
            if node in visited:
                # Loop terdeteksi, potong path kembali ke kemunculan pertama node ini
                cut_index = visited[node]
                new_path = new_path[:cut_index+1]
                # Update visited map karena kita memotong elemen
                visited = {n: i for i, n in enumerate(new_path)}
            else:
                new_path.append(node)
                visited[node] = len(new_path) - 1
        
        self.nodes = new_path

    def calculate_length(self) -> None:
        total_len = 0.0
        for i in range(len(self.nodes) - 1):
            dist = self.graph.get_edge_length(self.nodes[i], self.nodes[i+1])
            total_len += dist
        self.length = total_len

    def calculate_fitness(self) -> None:
        # Fitness (Eq. 4)
        if self.length > 0 and self.length != float('inf'):
            self.fitness = 1.0 / self.length
        else:
            self.fitness = 0.0

    def get_hash(self) -> str:
        return "-".join(map(str, self.nodes))

    @staticmethod
    def create_random_path(S: int, T: int, graph_handler) -> Optional[PathSolution]:
        # Random Initialization
        current_node = S
        path = [S]
        # Safety break: Mencegah loop tak berujung
        max_steps = graph_handler.graph.number_of_nodes() * 2 
        
        steps = 0
        reached_target = False

        while steps < max_steps:
            if current_node == T:
                reached_target = True
                break

            neighbors = graph_handler.get_neighbors(current_node)
            if not neighbors:
                break # Dead end (jalan buntu)
            
            # Simple heuristic: Jangan langsung balik ke node sebelumnya jika ada opsi lain
            if len(path) > 1 and len(neighbors) > 1:
                prev_node = path[-2]
                if prev_node in neighbors:
                    # Buat copy list agar tidak merusak graph asli
                    neighbors = list(neighbors)
                    neighbors.remove(prev_node)

            current_node = random.choice(neighbors)
            path.append(current_node)
            steps += 1
            
        if not reached_target:
            return None # Gagal menemukan jalan ke T

        new_sol = PathSolution(path, graph_handler)
        new_sol.mend_path() # Wajib dimending
        return new_sol