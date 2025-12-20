import demes
import random
import math
from collections import Counter

class WrightFisherSim:
    def __init__(self, demes_file_path, alleles=None, initial_allele_frequency=0.5, seed=None):
        # Load the graph using demes library
        self.graph = demes.load(demes_file_path)
        
        if seed is not None:
            random.seed(seed)
            
        self.alleles= alleles if alleles else [0, 1]
        
        if initial_allele_frequency is not None:
            self.initial_freqs = initial_allele_frequency
        else:
            self.initial_freqs={a: 1.0 / len(self.alleles) for a in self.alleles}
        
        total = sum(self.initial_freqs.values())
        if not math.isclose(total, 1.0):
            raise ValueError("Initial allele frequencies must sum to 1.")

        # Track active populations (name -> list of alleles)
        self.current_populations = {}
        
        # Track frequency history for plotting
        self.history = {}

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
                        new_pop_alleles.extend([0] * count)
                    else:
                        new_pop_alleles.extend([random.choice(source_pop) for _ in range(count)])
            
            # Fix any rounding errors by filling the rest from the first ancestor
            while len(new_pop_alleles) < population_size:
                # Fallback to first ancestor if we are short a few individuals
                primary_source = self.current_populations[ancestors[0]]
                if primary_source:
                    new_pop_alleles.append(random.choice(primary_source))
                else:
                    new_pop_alleles.append(0)
            
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

    def run(self):
        # Determine the simulation start time.
        # Demes uses Infinity for root populations, so we need to find the 
        # oldest finite time (e.g. a split) and add a buffer.
        start_times = [p.start_time for p in self.graph.demes]
        finite_times = [t for t in start_times if not math.isinf(t)]
        
        if not finite_times:
            start_generation = 100 
        else:
            # Start 50 generations before the first recorded event
            start_generation = int(max(finite_times) + 50)
        
        print(f"Simulation running from generation {start_generation} to 0...")

        # Iterate backwards from past to present
        for t in range(start_generation, -1, -1):
            
            # Handle population creation (Births)
            for pop in self.graph.demes:
                # Check if the population starts at this specific generation
                is_finite_start = (not math.isinf(pop.start_time)) and (int(pop.start_time) == t)
                # Force the root population to start at the beginning of our sim
                is_root_start = math.isinf(pop.start_time) and (t == start_generation)
                
                if is_finite_start or is_root_start:
                    if pop.name not in self.current_populations:
                        # We use the explicit start_size from the epoch definition
                        # to avoid getting 0 from size_at(t) at the exact boundary.
                        initial_size = pop.epochs[0].start_size
                        
                        # Pass the lists for ancestors and proportions to handle merges
                        ancestors = pop.ancestors
                        proportions = pop.proportions
                        
                        self._initialize_population(pop.name, initial_size, ancestors, proportions)

            # Evolution Step (Wright-Fisher)
            # Iterate over a list of keys to allow dictionary modification if needed
            for pop_name in list(self.current_populations.keys()):
                
                # We query the size slightly inside the interval (t - epsilon)
                # to ensure we get the valid size for the current generation.
                query_time = max(0, t - 1e-5)
                current_size = int(self.graph[pop_name].size_at(query_time))
                
                # Handle extinction or empty populations
                if current_size <= 0:
                    self.current_populations[pop_name] = []
                    self.history[pop_name].append(0)
                    continue

                old_alleles = self.current_populations[pop_name]
                
                if not old_alleles:
                    self.history[pop_name].append(0)
                    continue

                # Random sampling with replacement
                new_alleles = [random.choice(old_alleles) for _ in range(current_size)]
                self.current_populations[pop_name] = new_alleles
                
                # Save frequency data
                counts = Counter(new_alleles)
                freqs = {a: counts.get(a, 0) / len(new_alleles) for a in self.alleles}
                self.history[pop_name].append(freqs)
            # Migration and Pulse Steps
            self._handle_migration(t)
            self._handle_pulses(t)

        return self.history