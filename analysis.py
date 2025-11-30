from typing import List
import itertools
from path_solution import PathSolution

def calculate_dissimilarity(path_A: PathSolution, path_B: PathSolution) -> float:
    edges_A = set(zip(path_A.nodes[:-1], path_A.nodes[1:]))
    edges_B = set(zip(path_B.nodes[:-1], path_B.nodes[1:]))
    
    g = path_A.graph
    
    len_intersect = sum(g.get_edge_length(u, v) for u, v in edges_A.intersection(edges_B))
    len_union = sum(g.get_edge_length(u, v) for u, v in edges_A.union(edges_B))
    
    if len_union == 0: return 0.0
    return 1.0 - (len_intersect / len_union)

def calculate_set_diversity(path_set: List[PathSolution]) -> float:
    if len(path_set) < 2: return 1.0
    min_dissimilarity = float('inf')
    
    for path_A, path_B in itertools.combinations(path_set, 2):
        dis = calculate_dissimilarity(path_A, path_B)
        if dis < min_dissimilarity:
            min_dissimilarity = dis
            
    return min_dissimilarity

def find_kmdnsp(all_paths: List[PathSolution], k: int, shortest_path_len: float, epsilon: float) -> List[PathSolution]:
    # Step 1: Filter near-shortest
    max_allowed = shortest_path_len * (1.0 + epsilon)
    valid_paths = [p for p in all_paths if p.length <= max_allowed and p.length != float('inf')]
    
    # Hapus duplikat berdasarkan hash
    unique_map = {p.get_hash(): p for p in valid_paths}
    unique_paths = list(unique_map.values())

    if len(unique_paths) <= k:
        return unique_paths

    # Step 2: Brute force combinations (KMDNSP)
    best_set = []
    max_diversity = -1.0
    
    search_space = unique_paths if len(unique_paths) < 20 else sorted(unique_paths, key=lambda x: x.fitness, reverse=True)[:20]

    for combo in itertools.combinations(search_space, k):
        div = calculate_set_diversity(list(combo))
        if div > max_diversity:
            max_diversity = div
            best_set = list(combo)
            
    return best_set