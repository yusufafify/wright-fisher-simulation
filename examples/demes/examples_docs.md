# Demes Example Files

This directory contains example Demes YAML files for various population genetics scenarios.

## Quick Usage

### Python
```python
from evolutionary_simulator.core import WrightFisherSim, plot_results

# Use any example file
sim = WrightFisherSim(
    demes_file_path='examples/demes/03_population_split.yml',
    initial_allele_frequency=0.5,
    mutation_rate=0.001,
    seed=42
)

results = sim.run()
plot_results(results)
```

### R
```r
library(WrightFisherSim)

# Use any example file
results <- wright_fisher_sim(
  demes_file = "examples/demes/03_population_split.yml",
  initial_frequency = 0.5,
  mutation_rate = 0.001,
  seed = 42
)

plot_wright_fisher(results)
```

---

## Available Scenarios

### 1. Single Population (`01_single_population.yml`)
**Scenario**: Constant-size population  
**Size**: 1,000 individuals  
**Best for**: Basic drift simulations, testing mutation-drift balance

**Example use**:
```r
# Study pure genetic drift
results <- wright_fisher_sim(
  demes_file = "examples/demes/01_single_population.yml",
  initial_frequency = 0.5,
  mutation_rate = 0.0,  # No mutations
  seed = 42
)
```

---

### 2. Population Bottleneck (`02_bottleneck.yml`)
**Scenario**: Population undergoes severe reduction then recovers  
**Timeline**:
- Generations 200-100: Size 10,000 (ancestral)
- Generations 100-50: Size 50 (bottleneck)
- Generations 50-0: Size 1,000 (recovery)

**Best for**: Loss of genetic variation, founder effects

**Example use**:
```r
# See how bottlenecks reduce diversity
results <- wright_fisher_sim(
  demes_file = "examples/demes/02_bottleneck.yml",
  initial_frequency = 0.5,
  mutation_rate = 0.0001,
  seed = 42
)
```

---

### 3. Population Split (`03_population_split.yml`)
**Scenario**: Single population splits into two at generation 200  
**Populations**: Ancestral → Pop_A + Pop_B  
**Best for**: Speciation, divergence, isolation

**Example use**:
```r
# Model divergence between populations
results <- wright_fisher_sim(
  demes_file = "examples/demes/03_population_split.yml",
  initial_frequency = 0.8,
  mutation_rate = 0.001,
  seed = 42
)
```

---

### 4. Migration (`04_migration.yml`)
**Scenario**: Two populations with continuous bidirectional gene flow  
**Migration rate**: 1% per generation in each direction  
**Best for**: Gene flow effects, isolation-with-migration

**Example use**:
```r
# Study migration-drift equilibrium
results <- wright_fisher_sim(
  demes_file = "examples/demes/04_migration.yml",
  initial_frequency = 0.3,
  mutation_rate = 0.0005,
  seed = 42
)
```

---

### 5. Population Expansion (`05_expansion.yml`)
**Scenario**: Population grows exponentially from 100 to 10,000  
**Growth period**: 200 generations  
**Best for**: Range expansion, colonization

**Example use**:
```r
# Model population expansion effects
results <- wright_fisher_sim(
  demes_file = "examples/demes/05_expansion.yml",
  initial_frequency = 0.1,  # Rare allele
  mutation_rate = 0.0,
  seed = 42
)
```

---

### 6. Admixture (`06_admixture.yml`)
**Scenario**: Two populations with pulse admixture event  
**Event**: 20% of Pop_A from Pop_B at generation 100  
**Best for**: Hybridization, introgression

**Example use**:
```r
# Study admixture effects
results <- wright_fisher_sim(
  demes_file = "examples/demes/06_admixture.yml",
  initial_frequency = 0.9,
  mutation_rate = 0.0,
  seed = 42
)
```

---

### 7. Island Model (`07_island_model.yml`)
**Scenario**: Three populations with symmetric migration  
**Migration**: 0.5% between all population pairs  
**Best for**: Metapopulation dynamics, structure

**Example use**:
```r
# Model metapopulation structure
results <- wright_fisher_sim(
  demes_file = "examples/demes/07_island_model.yml",
  initial_frequency = 0.5,
  mutation_rate = 0.001,
  seed = 42
)
```

---

### 8. Out-of-Africa (`08_out_of_africa.yml`)
**Scenario**: Simplified human demographic history  
**Populations**: African (ancestral) → Out-of-Africa (expansion)  
**Timeline**:
- Bottleneck 2,000 generations ago
- Exponential growth to present
- Low back-migration

**Best for**: Human evolution, realistic demography

**Example use**:
```r
# Model human-like demographic history
results <- wright_fisher_sim(
  demes_file = "examples/demes/08_out_of_africa.yml",
  initial_frequency = 0.99,  # Ancestral allele
  mutation_rate = 0.0001,
  seed = 42
)
```

---

## Scenario Comparison Table

| File | Populations | Migration | Pulses | Size Changes     | Complexity |
| ---- | ----------- | --------- | ------ | ---------------- | ---------- |
| 01   | 1           | No        | No     | No               | ⭐          |
| 02   | 1           | No        | No     | Yes (bottleneck) | ⭐⭐         |
| 03   | 3           | No        | No     | No               | ⭐⭐         |
| 04   | 3           | Yes       | No     | No               | ⭐⭐⭐        |
| 05   | 1           | No        | No     | Yes (expansion)  | ⭐⭐         |
| 06   | 3           | No        | Yes    | No               | ⭐⭐⭐        |
| 07   | 3           | Yes       | No     | No               | ⭐⭐⭐⭐       |
| 08   | 2           | Yes       | No     | Yes (complex)    | ⭐⭐⭐⭐⭐      |

---

## Creating Custom Scenarios

You can modify these files or create your own. Basic structure:

```yaml
description: My custom scenario
time_units: generations

demes:
  - name: MyPopulation
    start_time: .inf
    epochs:
      - start_size: 1000
        end_time: 0

# Optional: migrations
migrations:
  - source: Pop1
    dest: Pop2
    rate: 0.01
    start_time: 100
    end_time: 0

# Optional: pulses
pulses:
  - source: Pop1
    dest: Pop2
    proportion: 0.1
    time: 50
```

---

## Tips for Using These Files

1. **Start simple**: Use `01_single_population.yml` first
2. **Test mutations**: Try with and without `mutation_rate`
3. **Compare results**: Run same scenario with different seeds
4. **Modify parameters**: Change population sizes to see effects
5. **Combine features**: Add mutations to migration scenarios

---

## References

- [Demes Specification](https://popsim-consortium.github.io/demes-spec-docs/)
- Wright-Fisher model theory
- Population genetics textbooks

---

## Common Patterns

### Testing Drift Strength
```r
# Small population (strong drift)
wright_fisher_sim("examples/demes/01_single_population.yml", ...)

# Large population (weak drift)
# Edit file to change start_size: 100000
```

### Testing Mutation-Drift Balance
```r
# Low mutation
wright_fisher_sim(..., mutation_rate = 0.0001)

# High mutation
wright_fisher_sim(..., mutation_rate = 0.01)
```

### Testing Migration Effects
```r
# With migration
wright_fisher_sim("examples/demes/04_migration.yml", ...)

# Without migration (use 03_population_split.yml)
wright_fisher_sim("examples/demes/03_population_split.yml", ...)
```

---

**All scenarios are ready to use with both Python and R implementations!**
