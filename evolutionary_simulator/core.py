import demes
import random
import math
import matplotlib.pyplot as plt
import yaml
from collections import Counter


class WrightFisherSim:
    def __init__(self, demes_file_path, config_file_path=None, alleles=None, initial_allele_frequency=0.5, 
                 mutation_rate=0.0, wild_type=0, seed=None, selection_coefficients=None):

        # Load the graph using demes library
        self.graph = demes.load(demes_file_path)
        
        if seed is not None:
            random.seed(seed)
            
        # 1. Capture ALL potential alleles passed by the user
        all_potential_alleles = alleles if alleles else [0, 1]

        # 2. Parse Config
        self.config = {}
        self.new_alleles_config = []
        self.alleles_by_time = {}
        
        # Identify which alleles are "Future/New"
        future_alleles_set = set()

        if config_file_path:
            with open(config_file_path, 'r') as file:
                self.config = yaml.safe_load(file)
            self.new_alleles_config = self.config.get("new_alleles", [])
            
            for entry in self.new_alleles_config:
                required_fields = {"allele", "population", "start_time"}
                if not required_fields.issubset(entry):
                    raise ValueError(f"New allele entry missing required fields: {required_fields}")
                
                # Validate that the allele in config is in the alleles array
                config_allele = entry["allele"]
                if config_allele not in all_potential_alleles:
                    raise ValueError(
                        f"Error: Allele '{config_allele}' is defined in the config file but not in the alleles array. "
                        f"Please add '{config_allele}' to the alleles parameter when creating the simulator.\n"
                        f"Current alleles: {all_potential_alleles}"
                    )
                
                t = int(entry["start_time"])
                self.alleles_by_time.setdefault(t,[]).append(entry)
                future_alleles_set.add(entry["allele"])


        # 3. Define ACTIVE alleles (Start Gen) vs Future Alleles
        # We remove future alleles from the active list so they aren't generated at Gen 100
        self.alleles = [a for a in all_potential_alleles if a not in future_alleles_set]
        
        # Validation: Ensure we still have at least one allele (Wild Type)
        if not self.alleles:
             if wild_type in all_potential_alleles:
                 self.alleles = [wild_type]
             else:
                 self.alleles = [0]

        # 4. Pre-calculate Fitness for EVERYONE (Active + Future)
        self.selection_coefficients = selection_coefficients if selection_coefficients else {}
        self.fitness = {}
        for allele in all_potential_alleles:
            s = self.selection_coefficients.get(allele, 0.0)
            self.fitness[allele] = max(0.0, 1.0 + s)

        # 5. Set Initial Frequencies (Only for Active Alleles)
        if initial_allele_frequency is not None:
            if isinstance(initial_allele_frequency, dict):
                 self.initial_freqs = {k: v for k, v in initial_allele_frequency.items() if k in self.alleles}
            else:
                if len(self.alleles) != 2:
                    if len(self.alleles) == 1:
                        self.initial_freqs = {self.alleles[0]: 1.0}
                    else:
                        self.initial_freqs = {a: 1.0 / len(self.alleles) for a in self.alleles}
                else:
                    self.initial_freqs = {
                        self.alleles[0]: initial_allele_frequency,
                        self.alleles[1]: 1.0 - initial_allele_frequency
                    }
        else:
            self.initial_freqs={a: 1.0 / len(self.alleles) for a in self.alleles}
        
        # Validate sums
        total = sum(self.initial_freqs.values())
        if not math.isclose(total, 1.0):
             factor = 1.0 / total
             self.initial_freqs = {k: v*factor for k,v in self.initial_freqs.items()}

        self.mutation_rate = mutation_rate
        self.wild_type = wild_type
        self.current_populations = {}
        self.history = {}

        print("loaded new alleles config:")
        for c in self.new_alleles_config:
            print(f"  {c['allele']} in {c['population']} at {c['start_time']}")

    def _handle_new_alleles(self, generation):
        """
        Introduce new alleles at specific generations and populations
        """
        if generation not in self.alleles_by_time:
            return
        for entry in self.alleles_by_time[generation]:
            pop = entry["population"]
            allele = entry["allele"]
            freq = entry.get("initial_frequency", 0.05)
            if pop in self.current_populations:
                pop_alleles = self.current_populations[pop]
                if len(pop_alleles)==0:
                    continue
            else:
                continue    
            if allele not in self.alleles:
                self.alleles.append(allele)
            else:
                print(f"Warning: Allele {allele} already exists in population {pop}. Overwriting individuals.")    
            # Number of indviduals to convert
            N = max(1, int(len(pop_alleles)*freq))
            indices = random.sample(range(len(pop_alleles)),N)
            for i in indices:
                pop_alleles[i]= allele    

    def _initialize_population(self, pop_name, population_size, ancestors=None, proportions=None):
        """
        This dunder function is responsible for creating a new population.
        If it has ancestors (split or merge), sample from them based on proportions.
        Otherwise, use initial_frequency.
        """
        new_pop_alleles = []
        
        # Check for split or merge event (Ancestry exists)
        if ancestors:
            # If proportions not provided, divide equally among ancestors
            if not proportions:
                proportions = [1.0 / len(ancestors)] * len(ancestors)
            
            # Iterate through ancestors and sample based on proportions
            for ancestor, prop in zip(ancestors, proportions):
                if ancestor in self.current_populations:
                    source_pop = self.current_populations[ancestor]
                    
                    # Calculate how many to take from this ancestor
                    count = int(population_size * prop)
                    
                    # Safety check to prevent crashing on empty ancestors
                    if not source_pop:
                        # --- FIX: Use self.wild_type instead of hardcoded 0 ---
                        new_pop_alleles.extend([self.wild_type] * count)
                    else:
                        new_pop_alleles.extend([random.choice(source_pop) for _ in range(count)])
            
            # Fix any rounding errors by filling the rest from the first ancestor
            while len(new_pop_alleles) < population_size:
                # Fallback to first ancestor if we are short a few individuals
                primary_source = self.current_populations[ancestors[0]]
                if primary_source:
                    new_pop_alleles.append(random.choice(primary_source))
                else:
                    new_pop_alleles.append(random.choice(self.alleles))
            
            # Shuffle so the alleles aren't ordered by ancestor
            random.shuffle(new_pop_alleles)

        else:
            # Create de novo population
            new_pop_alleles = random.choices(
                population=list(self.initial_freqs.keys()),
                weights=list(self.initial_freqs.values()),
                k=int(population_size)
            )
        
        self.current_populations[pop_name] = new_pop_alleles
        self.history[pop_name] = [] 
        print(f"Gen initialized: {pop_name} (Size: {len(new_pop_alleles)})")

    def _handle_migration(self, generation):
            """
            Applies migration rules.
            """
            if not self.graph.migrations:
                return

            for migration in self.graph.migrations:
                if migration.end_time <= generation <= migration.start_time:
                    source = migration.source
                    dest = migration.dest
                    rate = migration.rate

                    if source in self.current_populations and dest in self.current_populations:
                        dest_pop = self.current_populations[dest]
                        source_pop = self.current_populations[source]
                        
                        if len(source_pop) == 0 or len(dest_pop) == 0:
                            continue

                        # Calculate expected migrants
                        expected_migrants = len(dest_pop) * rate
                        
                        # Get the guaranteed integer part
                        num_migrants = int(expected_migrants)
                        
                        # Check the fractional remainder against a random number
                        # e.g., if expected is 0.3, there is a 30% chance num_migrants becomes 1
                        remainder = expected_migrants - num_migrants
                        if random.random() < remainder:
                            num_migrants += 1
                        
                        # Only proceed if we actually have migrants to move
                        if num_migrants > 0:
                            migrants = [random.choice(source_pop) for _ in range(num_migrants)]
                            for m in migrants:
                                random_idx = random.randint(0, len(dest_pop) - 1)
                                dest_pop[random_idx] = m

    def _handle_pulses(self, generation):
        """
        This dunder function used to apply pulse events (instant migration) for the generation
        """
        if not self.graph.pulses:
            return

        for pulse in self.graph.pulses:
            # Check if the pulse happens at this specific generation
            if int(pulse.time) == generation:
                source = pulse.source
                dest = pulse.dest
                proportion = pulse.proportion
                
                # Only proceed if both populations are active
                if source in self.current_populations and dest in self.current_populations:
                    dest_pop = self.current_populations[dest]
                    source_pop = self.current_populations[source]
                    
                    if len(source_pop) == 0 or len(dest_pop) == 0:
                        continue
                        
                    num_migrants = int(len(dest_pop) * proportion)
                    
                    # Select migrants and overwrite random individuals in dest
                    migrants = [random.choice(source_pop) for _ in range(num_migrants)]
                    
                    for m in migrants:
                        random_idx = random.randint(0, len(dest_pop) - 1)
                        dest_pop[random_idx] = m

    def _handle_mutations(self, pop_name):
        """
        Apply mutations to a population.
        Supports:
        - Forward mutations: wild-type -> mutant alleles
        - Backward mutations: mutant alleles -> wild-type
        """
        if self.mutation_rate <= 0:
            return
        
        population = self.current_populations[pop_name]
        mutant_alleles = [a for a in self.alleles if a != self.wild_type]
        
        if not mutant_alleles:
            return
        
        for i in range(len(population)):
            if random.random() < self.mutation_rate:
                current_allele = population[i]
                
                if current_allele == self.wild_type:
                    # Forward mutation: wild-type -> mutant
                    population[i] = random.choice(mutant_alleles)
                else:
                    # Backward mutation: mutant -> wild-type
                    population[i] = self.wild_type

    def run(self):
            start_times = [p.start_time for p in self.graph.demes]
            finite_times = [t for t in start_times if not math.isinf(t)]
            
            if not finite_times:
                start_generation = 100 
            else:
                start_generation = int(max(finite_times) + 50)
            
            print(f"Simulation running from generation {start_generation} to 0...")

            for t in range(start_generation, -1, -1):
                
                # --- 1. Update Zero Frequencies (Critical for dynamic alleles) ---
                zero_freqs = {a: 0.0 for a in self.alleles}

                # --- 2. Handle Births (Demes logic) ---
                for pop in self.graph.demes:
                    is_finite_start = (not math.isinf(pop.start_time)) and (int(pop.start_time) == t)
                    is_root_start = math.isinf(pop.start_time) and (t == start_generation)
                    
                    if is_finite_start or is_root_start:
                        if pop.name not in self.current_populations:
                            initial_size = pop.epochs[0].start_size
                            ancestors = pop.ancestors
                            proportions = pop.proportions
                            self._initialize_population(pop.name, initial_size, ancestors, proportions)

                # --- 3. Introduce New Alleles (Config) ---
                self._handle_new_alleles(t)

                # --- 4. EVOLUTION LOOP (Selection & Mutation) ---
                for pop_name in list(self.current_populations.keys()):
                    
                    query_time = max(0, t - 1e-5)
                    current_size = int(self.graph[pop_name].size_at(query_time))
                    
                    # Check for extinction or empty size
                    if current_size <= 0:
                        self.current_populations[pop_name] = []
                        # We do NOT append history here anymore to avoid double counting.
                        # The 'Stats Loop' below handles the logging.
                        continue

                    old_alleles = self.current_populations[pop_name]
                    
                    if not old_alleles:
                        continue

                    # A. Selection
                    weights = [self.fitness[allele] for allele in old_alleles]
                    
                    if sum(weights) == 0:
                        self.current_populations[pop_name] = []
                        continue

                    new_alleles = random.choices(
                        population=old_alleles,
                        weights=weights,
                        k=current_size
                    )
                    self.current_populations[pop_name] = new_alleles
                    
                    # B. Mutation
                    self._handle_mutations(pop_name)

                # --- 5. MIGRATION LOOP (Applied to the new generation) ---
                # Moves individuals between populations BEFORE we take the census
                self._handle_migration(t)
                self._handle_pulses(t)

                # --- 6. STATS LOOP (Census) ---
                # Record the final state of the population for this generation
                for pop_name in list(self.current_populations.keys()):
                    pop_data = self.current_populations[pop_name]
                    
                    # Handle empty/extinct populations safely
                    if not pop_data:
                        self.history[pop_name].append(zero_freqs.copy())
                    else:
                        counts = Counter(pop_data)
                        freqs = {a: counts.get(a, 0) / len(pop_data) for a in self.alleles}
                        self.history[pop_name].append(freqs)

            return self.history
    

def plot_results(results):
    """
    Visualizes the simulation results.
    
    Args:
        results (dict): The dictionary returned by sim.run() containing
                        population names and their allele frequency lists.
    """
    plt.figure(figsize=(14, 7))
    total_generations = max(len(v) for v in results.values())

    for pop_name, freq_history in results.items():
        if not freq_history:
            continue

        start_generation = total_generations - len(freq_history)
        # Correct biological generation axis
        generations = range(start_generation, total_generations)

        # Collect all alleles ever seen
        all_alleles = set()
        for gen in freq_history:
            all_alleles.update(gen.keys())

        for allele in sorted(all_alleles):
            allele_freqs = []
            allele_started = False

            for gen in freq_history:
                if allele in gen:
                    allele_started = True
                    allele_freqs.append(gen[allele])
                else:
                    allele_freqs.append(math.nan)

            plt.plot(
                generations,
                allele_freqs,
                label=f"{pop_name} – allele {allele}",
                linewidth=2
            )

    plt.title("Wright–Fisher Simulation  (Mutltiple Alleles)")
    plt.xlabel("Generation (past → present)")
    plt.ylabel("Allele Frequency")
    plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()
