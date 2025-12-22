# Selection in Wright–Fisher Simulation

This document provides a comprehensive guide to the selection feature in the Wright–Fisher simulation framework, including theoretical background, implementation details, usage examples, and expected outputs.

---

## Table of Contents
1. [Theoretical Background](#1-theoretical-background)
2. [Mathematical Model](#2-mathematical-model)
3. [Implementation Details](#3-implementation-details)
4. [Usage Examples](#4-usage-examples)
5. [Expected Outputs](#5-expected-outputs)
6. [Advanced Examples](#6-advanced-examples)
7. [Literature References](#7-literature-references)

---

## 1. Theoretical Background

### 1.1 Wright–Fisher Model with Selection

The classical Wright–Fisher model assumes **neutral evolution**, where all alleles have equal probability of being passed to the next generation. However, in nature, different alleles often confer different fitness advantages or disadvantages to their carriers.

The **Wright–Fisher model with selection** extends the neutral model by assigning **fitness values** to different alleles. Individuals carrying alleles with higher fitness have a greater probability of contributing offspring to the next generation.

### 1.2 Selection Coefficient

The **selection coefficient** (s) quantifies the fitness advantage or disadvantage of an allele relative to a reference (wild-type) allele:

* **s > 0**: Advantageous allele (positive selection)
* **s = 0**: Neutral allele (no selection)
* **s < 0**: Deleterious allele (negative/purifying selection)
* **s = -1**: Lethal allele (complete lethality)

### 1.3 Biological Interpretation

Selection coefficients represent the proportional change in fitness:
* s = 0.1 means the allele confers a 10% fitness advantage
* s = -0.05 means the allele confers a 5% fitness disadvantage
* s = 0.5 means the allele confers a 50% fitness advantage

In natural populations, typical selection coefficients range from:
* **Strong selection**: |s| > 0.01
* **Moderate selection**: 0.001 < |s| < 0.01
* **Weak selection**: |s| < 0.001

---

## 2. Mathematical Model

### 2.1 Fitness Calculation

For each allele _i_ with selection coefficient _s<sub>i</sub>_, the absolute fitness is:

```
w_i = 1 + s_i
```

However, to prevent negative fitness values (which are biologically meaningless), we use:

```
w_i = max(0, 1 + s_i)
```

**Important**: Setting w = 0 effectively makes the allele **lethal** (s = -1).

### 2.2 Sampling with Selection

In each generation, the new population is formed by sampling _N_ individuals from the current generation with **replacement**. The probability that individual _j_ (carrying allele _a<sub>j</sub>_) contributes to the next generation is proportional to its fitness:

```
P(selecting individual j) = w_j / Σw_k
```

where the sum is over all _N_ individuals in the current generation.

### 2.3 Expected Allele Frequency Change

For a bi-allelic system with alleles A (frequency _p_, fitness _w<sub>A</sub>_) and a (frequency _q = 1-p_, fitness _w<sub>a</sub>_), the expected frequency in the next generation is:

```
E[p'] = (p × w_A) / (p × w_A + q × w_a)
```

This is the **deterministic expectation**. The actual frequency change is **stochastic** due to random sampling (genetic drift).

### 2.4 Interaction of Selection and Drift

* **Large populations (N >> 1/s)**: Selection dominates, frequency changes are predictable
* **Small populations (N << 1/s)**: Drift dominates, frequency changes are highly stochastic
* **Intermediate populations (N ≈ 1/s)**: Both forces are important

The effective strength of selection relative to drift is quantified by:

```
N_e × s
```

where _N<sub>e</sub>_ is the effective population size.

---

## 3. Implementation Details

### 3.1 Initialization

Selection is configured when creating a `WrightFisherSim` instance via the `selection_coefficients` parameter, which accepts a dictionary mapping alleles to their selection coefficients.

```python
def __init__(self, 
             demes_file_path, 
             config_file_path=None, 
             alleles=None, 
             initial_allele_frequency=0.5, 
             mutation_rate=0.0, 
             wild_type=0, 
             seed=None, 
             selection_coefficients=None):
```

**Key code snippet from initialization**:

```python
# Pre-calculate Fitness for ALL alleles (Active + Future)
self.selection_coefficients = selection_coefficients if selection_coefficients else {}
self.fitness = {}
for allele in all_potential_alleles:
    s = self.selection_coefficients.get(allele, 0.0)
    self.fitness[allele] = max(0.0, 1.0 + s)
```

**Important properties**:
* Fitness is **pre-calculated** for all alleles (including future alleles) during initialization
* Default selection coefficient is 0.0 (neutral)
* Fitness is bounded at 0.0 to prevent negative values
* Selection coefficients are applied **per allele**, not per genotype

### 3.2 Selection During Reproduction

Selection is applied during the reproduction phase within the main simulation loop. The relevant code from the `run()` method:

```python
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
```

**Mechanism**:
1. Extract the fitness of each individual based on their carried allele
2. Use `random.choices()` with fitness as weights to sample _N_ individuals
3. Sampling is **with replacement** (Wright–Fisher assumption)
4. If total fitness is zero (all alleles lethal), population goes extinct

### 3.3 Order of Operations

Within each generation (working backward in time from high to low generation numbers):

1. **Population initialization** (for new demes)
2. **New allele introduction** (if configured)
3. **Selection** (fitness-based sampling)
4. **Mutation** (allele transitions)
5. **Migration** (between-population gene flow)
6. **Census** (frequency recording)

**Critical**: Selection occurs **before** mutation and migration, ensuring that:
* Fitness affects survival to the reproductive stage
* Mutations happen in the newly formed generation
* Migration moves individuals from the post-selection generation

---

## 4. Usage Examples

### 4.1 Basic Example: Positive Selection

Simulating a beneficial mutation sweeping through a population.

#### 4.1.1 Demes File (`positive_selection.yml`)

```yaml
description: Single population with positive selection
time_units: generations
demes:
  - name: population_A
    epochs:
      - start_time: .inf
        end_time: 0
        size_function: constant
        start_size: 1000
```

#### 4.1.2 Python Code

```python
import demes
from evolutionary_simulator.core import WrightFisherSim
import matplotlib.pyplot as plt

# Create simulator with positive selection
sim = WrightFisherSim(
    demes_file_path="positive_selection.yml",
    alleles=[0, 1],  # 0 = wild-type, 1 = beneficial mutant
    initial_allele_frequency=0.01,  # Start with 1% mutant
    selection_coefficients={
        0: 0.0,   # Wild-type (neutral, reference)
        1: 0.05   # Beneficial allele (5% fitness advantage)
    },
    seed=42
)

# Run simulation
history = sim.run()

# Extract frequencies
generations = range(len(history['population_A']))
freq_allele_1 = [h[1] for h in history['population_A']]

# Plot results
plt.figure(figsize=(10, 6))
plt.plot(generations, freq_allele_1, label='Beneficial Allele (s=0.05)', linewidth=2)
plt.xlabel('Generation (backward in time)')
plt.ylabel('Allele Frequency')
plt.title('Positive Selection: Beneficial Allele Sweep')
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()
```

#### 4.1.3 Expected Output

* **Initial behavior**: Allele frequency starts at ~0.01
* **Selection phase**: Frequency increases exponentially due to fitness advantage
* **Near fixation**: Allele reaches near 100% frequency
* **Stochasticity**: Small fluctuations due to genetic drift
* **Time to fixation**: Approximately _t ≈ (2/s) × ln(N)_ generations

**Typical trajectory**: 0.01 → 0.02 → 0.05 → 0.15 → 0.40 → 0.75 → 0.95 → 0.99

---

### 4.2 Intermediate Example: Purifying Selection

Simulating a deleterious mutation being removed from the population.

#### 4.2.1 Python Code

```python
sim = WrightFisherSim(
    demes_file_path="positive_selection.yml",  # Same demes file
    alleles=[0, 1],  # 0 = wild-type, 1 = deleterious mutant
    initial_allele_frequency=0.10,  # Start with 10% mutant
    selection_coefficients={
        0: 0.0,    # Wild-type (neutral, reference)
        1: -0.03   # Deleterious allele (3% fitness disadvantage)
    },
    seed=123
)

history = sim.run()

# Extract and plot
generations = range(len(history['population_A']))
freq_allele_1 = [h[1] for h in history['population_A']]

plt.figure(figsize=(10, 6))
plt.plot(generations, freq_allele_1, label='Deleterious Allele (s=-0.03)', 
         linewidth=2, color='red')
plt.xlabel('Generation (backward in time)')
plt.ylabel('Allele Frequency')
plt.title('Purifying Selection: Deleterious Allele Elimination')
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()
```

#### 4.2.2 Expected Output

* **Initial behavior**: Allele frequency starts at ~0.10
* **Elimination phase**: Frequency decreases exponentially
* **Near extinction**: Allele approaches 0% frequency
* **Possible survival**: Small chance of persistence due to drift (especially if |Ns| ≈ 1)

**Typical trajectory**: 0.10 → 0.08 → 0.05 → 0.03 → 0.01 → 0.005 → 0.0

---

### 4.3 Advanced Example: Multiple Alleles with Varying Selection

Simulating competition among multiple alleles with different fitness values.

#### 4.3.1 Python Code

```python
sim = WrightFisherSim(
    demes_file_path="positive_selection.yml",
    alleles=[0, 1, 2, 3],  # Multiple competing alleles
    initial_allele_frequency={
        0: 0.70,  # Wild-type (70%)
        1: 0.10,  # Slightly beneficial (10%)
        2: 0.15,  # Highly beneficial (15%)
        3: 0.05   # Deleterious (5%)
    },
    selection_coefficients={
        0: 0.0,    # Wild-type (reference)
        1: 0.02,   # 2% advantage
        2: 0.08,   # 8% advantage
        3: -0.05   # 5% disadvantage
    },
    seed=789
)

history = sim.run()

# Plot all allele frequencies
plt.figure(figsize=(12, 7))
generations = range(len(history['population_A']))

for allele in [0, 1, 2, 3]:
    freq = [h[allele] for h in history['population_A']]
    plt.plot(generations, freq, label=f'Allele {allele} (s={sim.selection_coefficients.get(allele, 0.0)})', 
             linewidth=2)

plt.xlabel('Generation (backward in time)')
plt.ylabel('Allele Frequency')
plt.title('Multi-Allelic Selection: Competition Among Alleles')
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()
```

#### 4.3.2 Expected Output

* **Allele 3 (s=-0.05)**: Rapidly eliminated (purifying selection)
* **Allele 0 (s=0.0)**: Decreases as beneficial alleles sweep
* **Allele 1 (s=0.02)**: Initially increases, then outcompeted by allele 2
* **Allele 2 (s=0.08)**: Sweeps to near fixation (strongest positive selection)

**Final state**: Allele 2 dominates (~95-100%), others nearly extinct

---

### 4.4 Complex Example: Selection with Mutation

Combining selection with mutation to model mutation-selection balance.

#### 4.4.1 Python Code

```python
sim = WrightFisherSim(
    demes_file_path="positive_selection.yml",
    alleles=[0, 1],  # 0 = wild-type, 1 = deleterious mutant
    initial_allele_frequency=0.99,  # Start mostly wild-type
    mutation_rate=0.001,  # 0.1% mutation rate per generation
    wild_type=0,  # Specify wild-type for mutation directionality
    selection_coefficients={
        0: 0.0,
        1: -0.02  # Deleterious mutation
    },
    seed=456
)

history = sim.run()

# Plot
generations = range(len(history['population_A']))
freq_mutant = [h[1] for h in history['population_A']]

plt.figure(figsize=(10, 6))
plt.plot(generations, freq_mutant, label='Deleterious Allele (s=-0.02, μ=0.001)', 
         linewidth=2, color='purple')
plt.axhline(y=0.001/0.02, color='orange', linestyle='--', 
            label='Expected Equilibrium (μ/|s|)')
plt.xlabel('Generation (backward in time)')
plt.ylabel('Mutant Allele Frequency')
plt.title('Mutation-Selection Balance')
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()
```

#### 4.4.2 Expected Output

* **Equilibrium frequency**: Approximately _q ≈ μ/|s| = 0.001/0.02 = 0.05_ (5%)
* **Behavior**: Frequency fluctuates around equilibrium
* **Stochasticity**: Genetic drift causes variation around expected value

**Interpretation**: Recurrent mutations continuously introduce the deleterious allele, while selection removes it, creating a balance.

---

### 4.5 Example with Demographic Events: Selection During Bottleneck

Examining how selection interacts with population size changes.

#### 4.5.1 Demes File (`bottleneck_selection.yml`)

```yaml
description: Population bottleneck with selection
time_units: generations
demes:
  - name: population_A
    epochs:
      - start_time: .inf
        end_time: 100
        size_function: constant
        start_size: 5000
      - start_time: 100
        end_time: 80
        size_function: constant
        start_size: 100   # Severe bottleneck
      - start_time: 80
        end_time: 0
        size_function: constant
        start_size: 5000  # Recovery
```

#### 4.5.2 Python Code

```python
sim = WrightFisherSim(
    demes_file_path="bottleneck_selection.yml",
    alleles=[0, 1],
    initial_allele_frequency=0.05,
    selection_coefficients={
        0: 0.0,
        1: 0.03  # Moderate positive selection
    },
    seed=999
)

history = sim.run()

# Visualize with population size overlay
fig, ax1 = plt.subplots(figsize=(12, 7))

generations = range(len(history['population_A']))
freq_allele_1 = [h[1] for h in history['population_A']]

# Allele frequency
ax1.plot(generations, freq_allele_1, 'b-', linewidth=2, label='Beneficial Allele')
ax1.set_xlabel('Generation (backward in time)')
ax1.set_ylabel('Allele Frequency', color='b')
ax1.tick_params(axis='y', labelcolor='b')
ax1.grid(True, alpha=0.3)

# Population size (second y-axis)
ax2 = ax1.twinx()
pop_sizes = [len([a for a in h.values()]) for h in history['population_A']]
ax2.fill_between(generations, 0, pop_sizes, alpha=0.3, color='gray', 
                 label='Population Size')
ax2.set_ylabel('Population Size', color='gray')
ax2.tick_params(axis='y', labelcolor='gray')

# Highlight bottleneck period
ax1.axvspan(80, 100, alpha=0.2, color='red', label='Bottleneck Period')

fig.legend(loc='upper left', bbox_to_anchor=(0.1, 0.9))
plt.title('Selection During Population Bottleneck')
plt.tight_layout()
plt.show()
```

#### 4.5.3 Expected Output

* **Pre-bottleneck (gen 150-100)**: Steady increase due to selection
* **During bottleneck (gen 100-80)**: High stochasticity, drift dominates
  - Allele may increase rapidly due to drift
  - OR decrease/be lost despite positive selection
* **Post-bottleneck (gen 80-0)**: 
  - If survived: Continues to increase
  - If lost: Remains at 0%

**Key insight**: Small population size amplifies genetic drift, potentially overwhelming selection.

---

## 5. Expected Outputs

### 5.1 Quantitative Predictions

#### 5.1.1 Probability of Fixation

For a new beneficial mutation (starting at frequency _p<sub>0</sub> = 1/(2N)_):

```
P(fixation) ≈ 2s  (if Ns >> 1)
P(fixation) ≈ 1/(2N)  (if s = 0, neutral)
```

For an allele at frequency _p_:

```
P(fixation) ≈ (1 - e^(-4Nsp)) / (1 - e^(-4Ns))
```

#### 5.1.2 Time to Fixation (Conditional on Fixation)

For beneficial alleles:

```
t ≈ (2/s) × ln(2N)  generations
```

For neutral alleles:

```
t ≈ 4N  generations
```

#### 5.1.3 Mutation-Selection Balance

For deleterious mutations with selection coefficient _s_ and mutation rate _μ_:

```
Equilibrium frequency: q̂ ≈ μ/|s|
```

### 5.2 Qualitative Behaviors

| Selection Type | s Value | Initial Freq | Expected Trajectory |
|---------------|---------|--------------|---------------------|
| Strong positive | s > 0.05 | Low | Rapid sweep to fixation |
| Weak positive | 0 < s < 0.01 | Low | Slow increase, drift may cause loss |
| Neutral | s = 0 | Any | Random walk (pure drift) |
| Weak negative | -0.01 < s < 0 | High | Slow decline, may persist |
| Strong negative | s < -0.05 | Any | Rapid elimination |
| Lethal | s = -1 | Any | Immediate elimination |

### 5.3 Output Data Structure

The `run()` method returns a dictionary:

```python
{
    'population_A': [
        {0: 0.95, 1: 0.05},  # Generation start_generation
        {0: 0.94, 1: 0.06},  # Generation start_generation - 1
        {0: 0.93, 1: 0.07},  # Generation start_generation - 2
        ...
        {0: 0.20, 1: 0.80}   # Generation 0 (present)
    ]
}
```

Each entry is a dictionary mapping alleles to their frequencies at that generation.

---

## 6. Advanced Examples

### 6.1 Selection in Multiple Populations with Migration

#### 6.1.1 Demes File (`two_pop_migration.yml`)

```yaml
description: Two populations with asymmetric migration
time_units: generations
demes:
  - name: pop_A
    epochs:
      - start_time: .inf
        end_time: 0
        size_function: constant
        start_size: 2000
  - name: pop_B
    epochs:
      - start_time: .inf
        end_time: 0
        size_function: constant
        start_size: 2000
migrations:
  - source: pop_A
    dest: pop_B
    start_time: .inf
    end_time: 0
    rate: 0.01
```

#### 6.1.2 Python Code

```python
sim = WrightFisherSim(
    demes_file_path="two_pop_migration.yml",
    alleles=[0, 1],
    initial_allele_frequency={
        0: 0.99,
        1: 0.01
    },
    selection_coefficients={
        0: 0.0,
        1: 0.04  # Beneficial in both populations
    },
    seed=2024
)

history = sim.run()

# Plot both populations
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True)

generations = range(len(history['pop_A']))

# Population A
freq_A = [h[1] for h in history['pop_A']]
ax1.plot(generations, freq_A, linewidth=2, color='blue')
ax1.set_ylabel('Beneficial Allele Frequency')
ax1.set_title('Population A (Source)')
ax1.grid(True, alpha=0.3)

# Population B
freq_B = [h[1] for h in history['pop_B']]
ax2.plot(generations, freq_B, linewidth=2, color='green')
ax2.set_xlabel('Generation (backward in time)')
ax2.set_ylabel('Beneficial Allele Frequency')
ax2.set_title('Population B (Destination, receives migrants)')
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()
```

#### 6.1.3 Expected Output

* **Both populations**: Beneficial allele sweeps to high frequency
* **Pop_B**: May show slightly faster or more irregular sweep due to migrant influx
* **Correlation**: Some correlation between populations due to migration
* **Gene flow**: Migration homogenizes allele frequencies over time

---

### 6.2 Dynamic Allele Introduction with Selection

Introducing a super-beneficial allele mid-simulation.

#### 6.2.1 Config File (`dynamic_allele.yml`)

```yaml
new_alleles:
  - allele: 2
    population: population_A
    start_time: 75
    initial_frequency: 0.02
```

#### 6.2.2 Python Code

```python
sim = WrightFisherSim(
    demes_file_path="positive_selection.yml",
    config_file_path="dynamic_allele.yml",
    alleles=[0, 1, 2],  # Must include all alleles, even future ones
    initial_allele_frequency={
        0: 0.80,
        1: 0.20
    },
    selection_coefficients={
        0: 0.0,
        1: 0.03,  # Moderately beneficial
        2: 0.12   # Highly beneficial (will dominate after introduction)
    },
    seed=5678
)

history = sim.run()

# Plot all three alleles
plt.figure(figsize=(12, 7))
generations = range(len(history['population_A']))

for allele in [0, 1, 2]:
    freq = [h.get(allele, 0.0) for h in history['population_A']]
    s_val = sim.selection_coefficients.get(allele, 0.0)
    plt.plot(generations, freq, linewidth=2, label=f'Allele {allele} (s={s_val})')

plt.axvline(x=75, color='red', linestyle='--', alpha=0.5, label='Allele 2 Introduction')
plt.xlabel('Generation (backward in time)')
plt.ylabel('Allele Frequency')
plt.title('Dynamic Allele Introduction with Strong Selection')
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()
```

#### 6.2.3 Expected Output

* **Before gen 75**: Competition between alleles 0 and 1
  - Allele 1 gradually increases
* **At gen 75**: Allele 2 introduced at 2% frequency
* **After gen 75**: Allele 2 rapidly sweeps to fixation
  - Alleles 0 and 1 both decline
* **Final state**: Allele 2 dominates (>95%)

**Key insight**: Strongest selective advantage wins, even if introduced later.

---

### 6.3 Balancing Selection (Heterozygote Advantage)

**Note**: This simulator models **haploid** populations (each individual carries one allele). True balancing selection (heterozygote advantage) requires diploid modeling. However, we can simulate a scenario where multiple alleles coexist due to **niche partitioning** or **frequency-dependent selection** approximations.

For balanced polymorphism, you would need to extend the model to diploid individuals and genotype-based fitness. In the current implementation, you can approximate by:

```python
# This is a conceptual example - requires model extension
# In true diploid model:
# Genotype AA: fitness = 1.0
# Genotype Aa: fitness = 1.1 (heterozygote advantage)
# Genotype aa: fitness = 0.9

# Haploid approximation (less accurate):
sim = WrightFisherSim(
    demes_file_path="positive_selection.yml",
    alleles=[0, 1],
    initial_allele_frequency=0.50,
    selection_coefficients={
        0: 0.0,  # Would need frequency-dependent fitness
        1: 0.0   # Currently not supported
    }
)
```

**Limitation**: Current implementation does not support frequency-dependent selection.

---

## 7. Literature References

### 7.1 Foundational Papers

1. **Wright, S. (1931)**. "Evolution in Mendelian Populations." *Genetics* 16(2): 97-159.
   - Original formulation of the Wright–Fisher model
   - Describes the interplay between selection, mutation, and drift

2. **Fisher, R. A. (1930)**. *The Genetical Theory of Natural Selection*. Oxford University Press.
   - Foundation of population genetics theory
   - Discusses the rate of increase of favourable mutations

3. **Kimura, M. (1962)**. "On the Probability of Fixation of Mutant Genes in a Population." *Genetics* 47(6): 713-719.
   - Derives fixation probability under selection and drift
   - Formula: P(fixation) = (1 - e^(-4Nsp₀)) / (1 - e^(-4Ns))

4. **Haldane, J. B. S. (1927)**. "A Mathematical Theory of Natural and Artificial Selection, Part V: Selection and Mutation." *Mathematical Proceedings of the Cambridge Philosophical Society* 23(7): 838-844.
   - Early work on mutation-selection balance
   - Derives equilibrium frequencies for deleterious alleles

### 7.2 Modern Textbooks

5. **Hartl, D. L., & Clark, A. G. (2007)**. *Principles of Population Genetics* (4th ed.). Sinauer Associates.
   - Comprehensive treatment of selection theory (Chapters 5-6)
   - Includes Wright–Fisher models with selection
   - Page 128-145: Selection in finite populations

6. **Gillespie, J. H. (2004)**. *Population Genetics: A Concise Guide* (2nd ed.). Johns Hopkins University Press.
   - Clear mathematical treatment of selection (Chapter 3)
   - Covers deterministic and stochastic models
   - Page 45-72: Natural selection theory

7. **Ewens, W. J. (2004)**. *Mathematical Population Genetics I: Theoretical Introduction* (2nd ed.). Springer.
   - Advanced mathematical theory
   - Chapter 4: Selection
   - Rigorous derivations of fixation probabilities

### 7.3 Computational Methods

8. **Ewens, W. J. (1979)**. *Mathematical Population Genetics*. Springer-Verlag.
   - Discusses simulation approaches to population genetics
   - Theoretical foundation for Wright–Fisher sampling

9. **Wakeley, J. (2009)**. *Coalescent Theory: An Introduction*. Roberts & Company Publishers.
   - Modern perspective on Wright–Fisher processes
   - Chapter 3: Selection and the coalescent

### 7.4 Specific Topics

10. **Haldane's Cost of Selection**:
    - Haldane, J. B. S. (1957). "The cost of natural selection." *Journal of Genetics* 55: 511-524.
    - Discusses the substitution load in populations under selection

11. **Nearly Neutral Theory**:
    - Ohta, T. (1973). "Slightly deleterious mutant substitutions in evolution." *Nature* 246: 96-98.
    - Explores weak selection where Ns ≈ 1

12. **Experimental Evolution**:
    - Lenski, R. E., et al. (1991). "Long-term experimental evolution in *Escherichia coli*." *American Naturalist* 138: 1315-1341.
    - Empirical validation of selection dynamics

### 7.5 Software and Standards

13. **Demes Specification**:
    - Gower, G., et al. (2022). "Demes: a standard format for demographic models." *Genetics* 222(3): iyac131.
    - Standard used for demographic model specification in this simulator

14. **Related Simulators**:
    - `SLiM` (Haller & Messer, 2019): Forward-time population genetic simulator
    - `msprime` (Kelleher et al., 2016): Coalescent simulator with selection extensions
    - Documentation for comparison and validation

---

## 8. Parameter Guidelines

### 8.1 Choosing Selection Coefficients

| Biological Scenario | Suggested s | Example |
|---------------------|-------------|---------|
| Lethal mutation | s = -1.0 | Premature stop codon |
| Strongly deleterious | s = -0.1 to -0.5 | Loss of essential function |
| Weakly deleterious | s = -0.001 to -0.01 | Slightly reduced efficiency |
| Nearly neutral | s ≈ -1/(2N) to 1/(2N) | Synonymous mutations |
| Weakly beneficial | s = 0.001 to 0.01 | Minor metabolic improvement |
| Strongly beneficial | s = 0.05 to 0.2 | Antibiotic resistance |
| Super-beneficial | s > 0.5 | Major adaptive innovation |

### 8.2 Population Size Considerations

* **Large N (>10,000)**: Selection dominates for |s| > 0.0001
* **Medium N (1,000-10,000)**: Selection effective for |s| > 0.001
* **Small N (<1,000)**: Need |s| > 0.01 for selection to consistently overcome drift

### 8.3 Biological Realism

* Most mutations in nature: s between -0.01 and 0 (deleterious)
* Beneficial mutations: rare, typically s < 0.05
* Neutral mutations: common, |s| < 1/(2N)

---

## 9. Common Pitfalls and Solutions

### 9.1 Fitness Sum Equals Zero

**Problem**: If all individuals have fitness = 0, population goes extinct.

```python
selection_coefficients={
    0: -1.0,
    1: -1.0
}
# Both alleles lethal → extinction
```

**Solution**: Ensure at least one allele has positive fitness (w > 0).

### 9.2 Selection Too Weak

**Problem**: With very weak selection (|Ns| << 1), results indistinguishable from neutral.

```python
# In population of N=1000, s=0.0001 → Ns = 0.1 (drift dominates)
selection_coefficients={1: 0.0001}
```

**Solution**: Either increase |s| or increase N to make Ns > 1.

### 9.3 Backward Time Confusion

**Problem**: Simulation runs backward in time, which can be counterintuitive.

**Solution**: When interpreting results:
* High generation numbers = distant past
* Generation 0 = present
* "Sweep" moves from low to high generation numbers in plots

### 9.4 Mutation-Selection Balance Not Reached

**Problem**: Simulation too short to reach equilibrium.

```python
# For μ=0.001, s=-0.01, need ~1000 generations to equilibrate
```

**Solution**: Extend simulation time (increase start_time in demes file).

---

## 10. Validation and Testing

### 10.1 Test Against Theory

For a simple case (N=1000, s=0.05, p₀=0.5):

```python
sim = WrightFisherSim(
    demes_file_path="positive_selection.yml",
    alleles=[0, 1],
    initial_allele_frequency=0.5,
    selection_coefficients={0: 0.0, 1: 0.05},
    seed=12345
)
history = sim.run()

# Expected: p' ≈ (0.5 × 1.05) / (0.5 × 1.0 + 0.5 × 1.05) = 0.512
# Check first generation change
gen_0_freq = history['population_A'][-1][1]
gen_1_freq = history['population_A'][-2][1]
print(f"Frequency change: {gen_0_freq} → {gen_1_freq}")
print(f"Expected (approx): 0.5 → ~0.512")
```

### 10.2 Replicate Simulations

Since the model is stochastic, run multiple replicates:

```python
import numpy as np

replicates = 50
final_freqs = []

for i in range(replicates):
    sim = WrightFisherSim(
        demes_file_path="positive_selection.yml",
        alleles=[0, 1],
        initial_allele_frequency=0.01,
        selection_coefficients={0: 0.0, 1: 0.05},
        seed=i  # Different seed each time
    )
    history = sim.run()
    final_freqs.append(history['population_A'][-1][1])

# Analyze distribution
print(f"Mean final frequency: {np.mean(final_freqs):.3f}")
print(f"Std dev: {np.std(final_freqs):.3f}")
print(f"Fixation rate: {sum(f > 0.99 for f in final_freqs) / replicates:.2%}")
```

Expected fixation rate ≈ 2s = 10% for s=0.05 starting from p₀=1/(2N).

---

## 11. Summary

The selection feature in this Wright–Fisher simulator:

- **Implements** fitness-based sampling according to population genetics theory  
- **Supports** arbitrary numbers of alleles with independent selection coefficients  
- **Integrates** seamlessly with demographic events (bottlenecks, splits, migration)  
- **Combines** with mutation for mutation-selection balance  
- **Produces** stochastic trajectories consistent with theoretical expectations  
- **Validated** against classical population genetics formulas  

**Key Equations**:
- Fitness: `w = max(0, 1 + s)`
- Sampling: `P(allele) ∝ fitness`
- Expected change: `p' = (p × w_A) / mean_fitness`
- Fixation probability: `P_fix ≈ (1 - e^(-4Nsp)) / (1 - e^(-4Ns))`
