import time
import random
import math
from typing import List, Dict
from graph_handler import GraphHandler
from path_solution import PathSolution
from island import Island
from analysis import find_kmdnsp

class MIBGA:
    def __init__(self, graph_handler: GraphHandler, S_node: int, T_node: int, K_paths: int, epsilon_threshold: float):
        self.graph = graph_handler
        self.S_node = S_node
        self.T_node = T_node
        self.K_paths = K_paths
        self.epsilon = epsilon_threshold
        
        # Parameter sesuai Paper Section 4.3
        self.pop_size = 250 
        self.selection_threshold = 0.10 # E% (Top 10%)
        self.min_island_size = 5
        self.max_island_size = 15
        self.mutation_prob = 0.05
        self.timeout = 120 # Seconds
        
        self.start_time = 0.0
        self.shortest_path_len = 0.0
        self.initial_population: List[PathSolution] = []
        self.islands: List[Island] = []
        self.all_found_paths: Dict[str, PathSolution] = {}

    def _initialize_population(self):
        print(f"Initializing population ({self.pop_size})...")
        attempts = 0
        # Limit attempts to avoid infinite loops if graph is disconnected
        while len(self.initial_population) < self.pop_size and attempts < self.pop_size * 50:
            p = PathSolution.create_random_path(self.S_node, self.T_node, self.graph)
            
            # --- PERBAIKAN: Handle None return ---
            if p is None:
                attempts += 1
                continue
            # -------------------------------------

            p.calculate_length()
            p.calculate_fitness()
            
            # Pastikan valid dan belum ada di populasi
            if p.length != float('inf') and p.get_hash() not in self.all_found_paths:
                self.initial_population.append(p)
                self.all_found_paths[p.get_hash()] = p
            attempts += 1
            
        if len(self.initial_population) == 0:
            print("[CRITICAL] Could not create any valid path. Start/Target might be disconnected or too far for random walk.")

    def _island_formation(self):
        """
        Implements Algorithm 1: Island Formation Strategy.
        Dynamically chunks population into islands of variable sizes.
        """
        # 1. Sort Population by Fitness
        sorted_pop = sorted(self.initial_population, key=lambda x: x.fitness, reverse=True)
        
        cutoff_idx = int(len(sorted_pop) * self.selection_threshold)
        superior_pool = sorted_pop[:cutoff_idx]
        central_pool = list(sorted_pop) # Copy of all
        
        self.islands = []
        
        while len(central_pool) > 0:
            current_size = random.randint(self.min_island_size, self.max_island_size)
            
            sp_count = max(1, int(current_size * self.selection_threshold))
            cp_count = current_size - sp_count
            
            if len(central_pool) < current_size:
                if self.islands:
                    last_island = self.islands[-1]
                    last_island.P_cp.extend(central_pool)
                    if superior_pool:
                        last_island.P_sp.extend(superior_pool)
                central_pool = []
                superior_pool = []
                break
            
            island_sp = []
            for _ in range(sp_count):
                if superior_pool:
                    idx = random.randint(0, len(superior_pool)-1)
                    island_sp.append(superior_pool.pop(idx))
                elif central_pool:
                    island_sp.append(central_pool[0])
            
            island_cp = []
            for _ in range(cp_count):
                if central_pool:
                    idx = random.randint(0, len(central_pool)-1)
                    island_cp.append(central_pool.pop(idx))
            
            self.islands.append(Island(island_sp, island_cp))

        print(f"Formed {len(self.islands)} islands.")

    def _migration(self):
        """
        Implements Algorithm 2: Migration Strategy.
        Swaps P_sp groups between islands based on random permutation.
        """
        if len(self.islands) < 2:
            return

        indices = list(range(len(self.islands)))
        random.shuffle(indices)
        
        original_sps = [island.P_sp for island in self.islands]
        
        for i, island in enumerate(self.islands):
            source_idx = indices[i]
            island.P_sp = original_sps[source_idx]

    def _selection_avgislandfit(self, all_offspring_by_island: List[List[PathSolution]]):
        """
        Implements AvgIslandFit: A multi-step selection process.
        """
        new_islands = []

        for i, island in enumerate(self.islands):
            offspring = all_offspring_by_island[i]
            
            island_parents = island.P_sp + island.P_cp
            if not island_parents:
                avg_island_fit = 0
            else:
                avg_island_fit = sum(p.fitness for p in island_parents) / len(island_parents)
            
            valid_offspring = [o for o in offspring if o.fitness >= avg_island_fit]

            combined_pool = island.P_sp + island.P_cp + valid_offspring
            
            unique_map = {p.get_hash(): p for p in combined_pool}
            unique_pool = list(unique_map.values())
            
            sorted_pool = sorted(unique_pool, key=lambda x: x.fitness, reverse=True)
            
            limit = self.max_island_size * 2
            if len(sorted_pool) > limit:
                sorted_pool = sorted_pool[:limit]

            if not sorted_pool:
                new_islands.append(island) 
                continue

            sp_count = max(1, int(len(sorted_pool) * self.selection_threshold))
            new_P_sp = sorted_pool[:sp_count]
            new_P_cp = sorted_pool[sp_count:]
            
            if new_P_sp:
                avg_sp = sum(p.fitness for p in new_P_sp) / len(new_P_sp)
                new_P_sp = [p for p in new_P_sp if p.fitness >= avg_sp]
            
            if new_P_cp:
                avg_cp = sum(p.fitness for p in new_P_cp) / len(new_P_cp)
                new_P_cp = [p for p in new_P_cp if p.fitness >= avg_cp]

            if not new_P_sp and sorted_pool: 
                new_P_sp = [sorted_pool[0]]
            
            if len(new_P_cp) > 5:
                max_remove = max(1, len(new_P_cp) // 5)
                num_to_remove = random.randint(1, max_remove)
                new_P_cp = new_P_cp[:-num_to_remove]

            island.P_sp = new_P_sp
            island.P_cp = new_P_cp
            new_islands.append(island)

        self.islands = new_islands

    def _check_termination(self) -> bool:
        return (time.time() - self.start_time) > self.timeout

    def run(self) -> List[PathSolution]:
        self.start_time = time.time()
        
        self.shortest_path_len = self.graph.get_shortest_path_length(self.S_node, self.T_node)
        print(f"Shortest Path Length: {self.shortest_path_len}")
        if self.shortest_path_len == float('inf'):
            print("Target unreachable.")
            return []

        self._initialize_population()
        self._island_formation()

        generation = 0
        while not self._check_termination():
            self._migration()
            
            all_offspring_by_island = []
            for island in self.islands:
                offspring = island.generate_offspring(self.graph, self.mutation_prob)
                
                valid_offspring = []
                for child in offspring:
                    child.calculate_length()
                    child.calculate_fitness()
                    if child.length != float('inf'):
                        self.all_found_paths[child.get_hash()] = child
                        valid_offspring.append(child)
                all_offspring_by_island.append(valid_offspring)
            
            self._selection_avgislandfit(all_offspring_by_island)
            
            generation += 1
            if generation % 10 == 0:
                print(f"Gen {generation} | Unique Paths: {len(self.all_found_paths)} | Islands: {len(self.islands)}")

        print("Analyzing K-Most Diverse...")
        final_paths = find_kmdnsp(
            all_paths=list(self.all_found_paths.values()),
            k=self.K_paths,
            shortest_path_len=self.shortest_path_len,
            epsilon=self.epsilon
        )
        return final_paths