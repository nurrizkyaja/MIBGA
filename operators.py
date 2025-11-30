from typing import Tuple, TYPE_CHECKING
import random

if TYPE_CHECKING:
    from path_solution import PathSolution
    from graph_handler import GraphHandler

def lfpc_crossover(parent_A: 'PathSolution', parent_B: 'PathSolution', graph_handler: 'GraphHandler') -> Tuple['PathSolution', 'PathSolution']:
    """
    Implements Loop-Free Path-Composer (LFPC) Crossover.
    Does NOT rely on common nodes. Bridges a random node in A to a random node in B.
    """
    # Import lokal untuk menghindari circular import saat runtime
    from path_solution import PathSolution

    # 1. Select random node R(A) and R(B)
    if len(parent_A.nodes) < 2 or len(parent_B.nodes) < 2:
         return parent_A, parent_B

    idx_a = random.randint(0, len(parent_A.nodes) - 2) 
    idx_b = random.randint(1, len(parent_B.nodes) - 1)
    
    node_a = parent_A.nodes[idx_a]
    node_b = parent_B.nodes[idx_b]

    # 2. Create partial route (bridge) from R(A) to R(B)
    bridge_path = PathSolution.create_random_path(node_a, node_b, graph_handler)
    
    # --- PERBAIKAN: Cek jika bridging gagal ---
    if bridge_path is None:
        # Gagal menyambung, kembalikan parent asli (abort crossover ini)
        return parent_A, parent_B
    # ------------------------------------------

    # 3. Stitch: S->R(A) + Bridge + R(B)->T
    new_nodes = parent_A.nodes[:idx_a] + bridge_path.nodes + parent_B.nodes[idx_b+1:]
    
    child_1 = PathSolution(new_nodes, graph_handler)
    child_1.mend_path() 

    # Generate second child (symmetric or random bridge B->A)
    bridge_back = PathSolution.create_random_path(node_b, node_a, graph_handler)
    
    # --- PERBAIKAN: Cek jika bridging balik gagal ---
    if bridge_back is None:
        # Jika anak kedua gagal, kita bisa kembalikan parent_B aslinya
        child_2 = parent_B
    else:
        new_nodes_2 = parent_B.nodes[:idx_b] + bridge_back.nodes + parent_A.nodes[idx_a+1:]
        child_2 = PathSolution(new_nodes_2, graph_handler)
        child_2.mend_path()
    # ------------------------------------------------

    return child_1, child_2

def lfpc_mutation(parent_A: 'PathSolution', parent_B: 'PathSolution', graph_handler: 'GraphHandler') -> Tuple['PathSolution', 'PathSolution']:
    """
    Implements LFPC with Mutation.
    Mutates R(A) to a neighbor R(C) before bridging.
    """
    from path_solution import PathSolution

    # 1. Check valid length
    if len(parent_A.nodes) < 3:
        # Fallback if path too short for mutation logic
        return lfpc_crossover(parent_A, parent_B, graph_handler)

    idx_a = random.randint(1, len(parent_A.nodes) - 2) # Ensure predecessor exists
    if len(parent_B.nodes) < 2:
        idx_b = 0
    else:
        idx_b = random.randint(1, len(parent_B.nodes) - 1)

    node_preceding = parent_A.nodes[idx_a - 1]
    node_b = parent_B.nodes[idx_b]

    # 2. Select R(C): A random neighbor of the node preceding R(A)
    neighbors = graph_handler.get_neighbors(node_preceding)
    if not neighbors:
        return lfpc_crossover(parent_A, parent_B, graph_handler)
        
    node_c = random.choice(neighbors) # Replaces original R(A)

    # 3. Create Bridge R(C) -> R(B)
    bridge_path = PathSolution.create_random_path(node_c, node_b, graph_handler)

    # --- PERBAIKAN: Cek jika bridging mutation gagal ---
    if bridge_path is None:
        # Jika mutasi gagal (jalan buntu), lakukan crossover biasa sebagai fallback
        return lfpc_crossover(parent_A, parent_B, graph_handler)
    # ---------------------------------------------------

    # 4. Stitch: S...Preceding + Bridge(starts with C) + ...T
    new_nodes = parent_A.nodes[:idx_a] + bridge_path.nodes + parent_B.nodes[idx_b+1:]
    
    child_1 = PathSolution(new_nodes, graph_handler)
    child_1.mend_path()

    # Child 2: Return a standard crossover or mutation on B to maintain API
    child_2, _ = lfpc_crossover(parent_B, parent_A, graph_handler)
    
    return child_1, child_2