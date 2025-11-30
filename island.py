from typing import List
import random
from path_solution import PathSolution
from operators import lfpc_crossover, lfpc_mutation

class Island:
    def __init__(self, superior_pop: List[PathSolution], central_pop: List[PathSolution]):
        self.P_sp = superior_pop
        self.P_cp = central_pop
        self.all_parents = list(set(superior_pop + central_pop))

    def generate_offspring(self, graph_handler, mutation_prob: float) -> List[PathSolution]:
        new_offspring_list = []
        if not self.P_sp or not self.P_cp:
            return []

        # Hitung weight P_sp
        total_sp_fitness = sum(p.fitness for p in self.P_sp)
        if total_sp_fitness > 0:
            weights = [p.fitness / total_sp_fitness for p in self.P_sp]
        else:
            weights = [1.0/len(self.P_sp) for _ in self.P_sp]

        for parent_B in self.P_cp:
            # Select Parent A (Weighted)
            parent_A = random.choices(self.P_sp, weights=weights, k=1)[0]
            
            if random.random() < mutation_prob:
                c1, c2 = lfpc_mutation(parent_A, parent_B, graph_handler)
            else:
                c1, c2 = lfpc_crossover(parent_A, parent_B, graph_handler)
            
            new_offspring_list.extend([c1, c2])
            
        return new_offspring_list