# Mutations Feature Documentation

## Table of Contents

- [Overview](#overview)
- [Mutation Model](#mutation-model)
- [Parameters](#parameters)
- [API Reference](#api-reference)
- [Usage Examples](#usage-examples)
  - [Python](#python-examples)
  - [R](#r-examples)
- [Scientific Background](#scientific-background)
- [Implementation Details](#implementation-details)
- [Expected Behavior](#expected-behavior)
- [Best Practices](#best-practices)
- [Testing](#testing)

---

## Overview

The Wright-Fisher Simulator implements **bidirectional mutations** as a core evolutionary force. Mutations introduce genetic variation into populations and, in combination with genetic drift, shape the evolutionary trajectory of allele frequencies.

Key capabilities:
- **Forward mutations**: Wild-type alleles mutate to mutant alleles
- **Backward mutations**: Mutant alleles revert to wild-type
- **Equal-rate bidirectionality**: Both directions occur at the same per-generation probability
- **Multi-allele support**: Works with two-allele and multi-allele systems

---

## Mutation Model

The simulator uses a symmetric, bidirectional mutation model:

```
        μ (forward)
Wild-type ⟷ Mutant
        μ (backward)
```

### Mutation Process (Per Generation)

For each individual in the population:
1. A random number is drawn from `[0, 1)`
2. If the number is less than `mutation_rate`:
   - If the individual carries the **wild-type** allele → mutates to a **mutant** allele (randomly selected if multiple mutants exist)
   - If the individual carries a **mutant** allele → reverts to the **wild-type** allele

### Mathematical Formulation

Given:
- `μ` = mutation rate (per individual, per generation)
- `N` = population size
- `p` = wild-type allele frequency

Expected mutational change per generation:
- Forward mutations: `μ × p × N` individuals
- Backward mutations: `μ × (1-p) × N` individuals

---

## Parameters

### Core Mutation Parameters

| Parameter       | Type    | Default | Range        | Description                                         |
| --------------------- | ----------| ------- | ------------ | --------------------------------------------------- |
| `mutation_rate` | `float` | `0.0`   | `[0.0, 1.0]` | Per-individual, per-generation mutation probability |
| `wild_type`     | `int`   | `0`     | Any integer  | Identifier for the wild-type (reference) allele     |

### Related Parameters

| Parameter                  | Type              | Description                                 |
| -------------------------- | ----------------- | ------------------------------------------- |
| `alleles`                  | `list[int]`       | Set of possible alleles (default: `[0, 1]`) |
| `initial_allele_frequency` | `float` or `dict` | Starting frequency of allele(s)             |

---

## API Reference

### Python: `WrightFisherSim`

```python
from evolutionary_simulator.core import WrightFisherSim

sim = WrightFisherSim(
    demes_file_path='population_model.yml',
    initial_allele_frequency=0.8,      # 80% wild-type
    mutation_rate=0.001,               # 0.1% mutation rate per generation
    wild_type=0,                       # Allele 0 is wild-type
    seed=42                            # For reproducibility
)

results = sim.run()
```

### R: `wright_fisher_sim()`

```r
library(WrightFisherSim)

results <- wright_fisher_sim(
  demes_file = "population_model.yml",
  initial_frequency = 0.8,     # 80% wild-type
  mutation_rate = 0.001,       # 0.1% mutation rate
  wild_type = 0L,              # Allele 0 is wild-type
  seed = 42L
)
```

### Internal Method: `_handle_mutations()`

```python
def _handle_mutations(self, pop_name):
    """
    Apply mutations to a population.
    
    Args:
        pop_name (str): Name of the population to mutate
    
    Process:
        1. Skip if mutation_rate <= 0
        2. Identify mutant alleles (all alleles except wild-type)
        3. Iterate through each individual
        4. Apply forward or backward mutation based on current allele
    """
```

---

## Usage Examples

### Python Examples

#### Example 1: Pure Genetic Drift (No Mutations)

```python
from evolutionary_simulator.core import WrightFisherSim, plot_results

sim = WrightFisherSim(
    demes_file_path='dev/deme_test.yml',
    initial_allele_frequency=0.5,
    mutation_rate=0.0,  # No mutations - pure drift
    seed=42
)

results = sim.run()
plot_results(results)
```

**Expected behavior**: Allele frequencies drift randomly toward fixation (1.0) or loss (0.0).

#### Example 2: Mutation-Drift Balance

```python
sim = WrightFisherSim(
    demes_file_path='dev/deme_test.yml',
    initial_allele_frequency=0.8,
    mutation_rate=0.005,  # 0.5% mutation rate
    wild_type=0,
    seed=42
)

results = sim.run()
plot_results(results)
```

**Expected behavior**: Variation maintained at intermediate frequencies due to mutation-drift equilibrium.

#### Example 3: Low Mutation Rate (Realistic Scenario)

```python
sim = WrightFisherSim(
    demes_file_path='dev/deme_test.yml',
    initial_allele_frequency=0.99,  # 99% wild-type
    mutation_rate=0.0001,           # 0.01% mutation rate
    wild_type=0,
    seed=42
)

results = sim.run()
```

**Biological interpretation**: Models slow accumulation of mutations in the absence of selection.

#### Example 4: Multi-Allele Mutations

```python
from evolutionary_simulator.core import WrightFisherSim

sim = WrightFisherSim(
    demes_file_path='dev/deme_test.yml',
    alleles=[0, 1, 2, 3],           # Wild-type + 3 mutants
    initial_allele_frequency={
        0: 0.7,   # Wild-type: 70%
        1: 0.15,  # Mutant 1: 15%
        2: 0.1,   # Mutant 2: 10%
        3: 0.05   # Mutant 3: 5%
    },
    mutation_rate=0.005,
    wild_type=0,
    seed=123
)

results = sim.run()
```

**Note**: In multi-allele systems, forward mutations randomly select among available mutant alleles.

---

### R Examples

#### Basic Simulation with Mutations

```r
library(WrightFisherSim)
library(ggplot2)

# Simulation with mutations
results <- wright_fisher_sim(
  demes_file = system.file("dev/deme_test.yml", package = "WrightFisherSim"),
  initial_frequency = 0.8,
  mutation_rate = 0.005,
  seed = 123
)

# View summary
summary(results)

# Visualize
p <- plot_wright_fisher(
  results,
  title = "Wright-Fisher with Mutations (μ=0.005)",
  show_params = TRUE
)
print(p)

# Save plot
ggsave("mutation_simulation.png", p, width = 10, height = 6)
```

#### Comparing Drift vs Mutation

```r
# Pure drift (no mutations)
no_mutation <- wright_fisher_sim(
  demes_file = system.file("dev/deme_test.yml", package = "WrightFisherSim"),
  initial_frequency = 0.5,
  mutation_rate = 0.0,
  seed = 456
)

# With mutations
with_mutation <- wright_fisher_sim(
  demes_file = system.file("dev/deme_test.yml", package = "WrightFisherSim"),
  initial_frequency = 0.5,
  mutation_rate = 0.01,
  seed = 456
)

# Compare plots
p1 <- plot_wright_fisher(no_mutation, title = "Pure Drift")
p2 <- plot_wright_fisher(with_mutation, title = "Drift + Mutation (μ=0.01)")
```

---

## Scientific Background

### Mutation-Drift Equilibrium

At equilibrium under mutation and genetic drift:

| Model                | Expected Heterozygosity (H)          | Notes                         |
| -------------------- | ------------------------------------ | ----------------------------- |
| **Two alleles**      | `H = 4Nμ / (1 + 4Nμ)`                | N = population size, μ = rate |
| **Infinite alleles** | `θ = 4Nμ` (population mutation rate) | Determines genetic diversity  |

### Recommended Mutation Rates

| Organism   | Per-base Rate (μ) | Effective Rate (per locus) |
| ---------- | ----------------- | -------------------------- |
| Bacteria   | 10⁻⁹ – 10⁻⁸       | 10⁻⁶ – 10⁻⁴                |
| Yeast      | 10⁻¹⁰             | 10⁻⁷ – 10⁻⁵                |
| Drosophila | 10⁻⁹              | 10⁻⁶ – 10⁻⁴                |
| Humans     | 10⁻⁸              | 10⁻⁶ – 10⁻⁴                |

**Guidance for simulations**:
- For demonstration: `0.001 – 0.01`
- For realistic modeling: `0.0001 – 0.001`
- For equilibrium studies: `1 / (4N)` where N = population size

### Biological Significance

Mutations in the Wright-Fisher model:
1. **Introduce variation**: Generate new alleles in the population
2. **Counteract drift**: Prevent complete fixation/loss of alleles
3. **Enable adaptation**: Provide raw material for natural selection
4. **Reach equilibrium**: Balance between mutation and drift leads to stable diversity

---

## Implementation Details

### Algorithm (Pseudocode)

```python
def _handle_mutations(self, pop_name):
    if mutation_rate <= 0:
        return  # No mutations to apply
    
    population = current_populations[pop_name]
    mutant_alleles = [a for a in alleles if a != wild_type]
    
    if not mutant_alleles:
        return  # No mutant alleles defined
    
    for i in range(len(population)):
        if random() < mutation_rate:
            current_allele = population[i]
            
            if current_allele == wild_type:
                # Forward mutation: wild-type → random mutant
                population[i] = random.choice(mutant_alleles)
            else:
                # Backward mutation: mutant → wild-type
                population[i] = wild_type
```

### Timing in Simulation Loop

Mutations are applied at a specific point in each generation:

```
Generation t:
├── 1. Population births/initialization
├── 2. New allele introduction (from config)
├── 3. Selection (fitness-weighted sampling)
├── 4. MUTATION ← Applied here
├── 5. Migration and pulse events
└── 6. Census (frequency recording)
```

### Key Design Decisions

1. **Post-selection timing**: Mutations occur after selection, allowing neutral or deleterious mutations to persist for at least one generation.

2. **Symmetric rates**: Forward and backward mutation rates are equal (`μ_forward = μ_backward = μ`). This ensures a stable equilibrium can be reached.

3. **Random mutant selection**: In multi-allele systems, forward mutations select uniformly among mutant alleles.

4. **Stochastic application**: Each individual mutates independently with probability `μ`.

---

## Expected Behavior

| Scenario          | `mutation_rate` | Expected Pattern                                 |
| ----------------- | --------------- | ------------------------------------------------ |
| Pure drift        | `0.0`           | Frequencies drift to 0 or 1 (fixation/loss)      |
| Low mutation      | `0.0001`        | Slow variation introduction; drift dominates     |
| Moderate mutation | `0.001 – 0.01`  | Mutation-drift balance; intermediate frequencies |
| High mutation     | `> 0.1`         | Rapid equilibration; frequencies near 0.5        |

### Equilibrium Frequency

For a two-allele system with symmetric mutation:
- **Expected equilibrium**: `p* = 0.5` (equal forward/backward rates)
- **Approach time**: Depends on `4Nμ` (population mutation parameter)

---

## Best Practices

### Choosing Mutation Rates

```python
# For teaching/demonstration
mutation_rate = 0.01  # Visible effects within ~100 generations

# For realistic modeling
population_size = 1000
mutation_rate = 1 / (4 * population_size)  # ≈ 0.00025

# For mutation-drift equilibrium
mutation_rate = 0.001  # Balances drift in moderate populations
```

### Validation Checks

```python
# Verify mutation rate is applied
assert sim.mutation_rate == expected_rate, "Mutation rate not set correctly"

# Confirm wild-type definition
assert sim.wild_type == 0, "Wild-type allele not configured"

# Check result structure
for pop_name, freq_history in results.items():
    assert len(freq_history) > 0, f"No history for {pop_name}"
```

### Interpretation Tips

1. **Short simulations** (< 50 generations): Mutation effects may not be visible
2. **Small populations** (N < 50): Drift overwhelms mutation
3. **Compare with/without**: Always run control simulations with `mutation_rate=0.0`

---

## Testing

### Running the Test Script

```bash
# From project root
python dev/test_mutation.py

# Or from dev directory
cd dev
python test_mutation.py
```

### Expected Output

```
Parameters initialized correctly
Simulation running from generation 100 to 0...
Gen initialized: Ancestral (Size: 100)
Gen initialized: Pop_A (Size: 100)
Gen initialized: Pop_B (Size: 100)
Simulation completed successfully
✓ Population 'Ancestral': 51 generations recorded
✓ Population 'Pop_A': 51 generations recorded
✓ Population 'Pop_B': 51 generations recorded

Running simulation without mutations (control)...
Simulation running from generation 100 to 0...
Control simulation completed successfully
All tests passed!
```

### Test Cases

| Test                        | Purpose                                     |
| --------------------------- | ------------------------------------------- |
| Parameter initialization    | Verify `mutation_rate` and `wild_type` set  |
| Simulation execution        | Confirm simulation completes without errors |
| Control comparison          | Run without mutations for baseline          |
| Result structure validation | Check frequency histories are populated     |

---

## See Also

- [Selection Documentation](selection.md) - Fitness-weighted reproduction
- [Multiple Alleles](multiple_alleles.md) - Multi-allele systems
- [Configurable Allele Introduction](configurable_allele_introduction.md) - Dynamic allele introduction
- [Migrations](migrations.md) - Gene flow between populations

---

## References

1. Fisher, R.A. (1930). *The Genetical Theory of Natural Selection*
2. Wright, S. (1931). Evolution in Mendelian Populations. *Genetics*, 16(2), 97–159.
3. Kimura, M. (1983). *The Neutral Theory of Molecular Evolution*
4. Ewens, W.J. (2004). *Mathematical Population Genetics*
