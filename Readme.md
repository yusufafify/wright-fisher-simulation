# Wright-Fisher Model Simulator with Mutation Support

A Python-based population genetics simulator implementing the Wright-Fisher model with support for genetic drift, migration, population splits/merges, and bidirectional mutations.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Core Concepts](#core-concepts)
- [Usage](#usage)
- [API Reference](#api-reference)
- [Examples](#examples)
- [Population Definition Format](#population-definition-format)
- [Implementation Details](#implementation-details)
- [Scientific Background](#scientific-background)
- [Team](#team)

---

## Overview

This simulator models evolutionary dynamics in structured populations using the Wright-Fisher model, a foundational framework in population genetics. The implementation supports complex demographic scenarios including:

- **Genetic drift**: Random sampling effects in finite populations
- **Mutations**: Bidirectional mutations between wild-type and mutant alleles
- **Migration**: Continuous gene flow between populations
- **Admixture**: Pulse migration events
- **Population structure**: Splits, merges, and size changes over time

The simulator uses the [Demes](https://popsim-consortium.github.io/demes-spec-docs/) specification for defining demographic models, enabling standardized and reproducible population genetics simulations.

---

## Features

### Core Functionality
- **Wright-Fisher sampling**: Random reproduction with replacement
- **Bidirectional mutations**: Forward (wild-type → mutant) and backward (mutant → wild-type)
- **Multi-allele support**: Simulate multiple mutant alleles simultaneously
- **Continuous migration**: Population-specific migration rates
- **Pulse events**: Instantaneous admixture between populations
- **Population dynamics**: Size changes, splits, and merges
- **Backward time simulation**: Coalescent-compatible time direction

### Technical Features
- Configurable mutation rates (0.0 to 1.0)
- Random seed control for reproducibility
- Comprehensive frequency tracking
- Built-in visualization tools
- Support for complex demographic scenarios via Demes YAML

---

## Installation

### Prerequisites
- Python 3.7+
- pip package manager

### Quick Installation

**Via pip (from GitHub):**
```bash
pip install git+https://github.com/yusufafify/wright-fisher-simulation.git
```

**Via R devtools:**
```r
devtools::install_github("yusufafify/wright-fisher-simulation")
```

### Development Setup

1. **Clone or download the repository**

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

Required packages:
- `demes` - Demographic model specification
- `matplotlib` - Visualization
- `numpy` - Numerical operations

3. **Install the package** (editable mode for development):
```bash
pip install -e .
```

### R Installation

The simulator is also available as an R package that wraps the Python implementation.

**Installation (3 steps):**

```r
# 1. Install from GitHub
install.packages("devtools")
devtools::install_github("yusufafify/wright-fisher-simulation")

# 2. Restart R, then install Python dependencies
reticulate::py_install(c("demes", "matplotlib", "numpy"), pip = TRUE)

# 3. Restart R again, then use
library(WrightFisherSim)
```

**Usage:**

```r
library(WrightFisherSim)

# Run simulation with mutations
results <- wright_fisher_sim(
  demes_file = system.file("dev/deme_test.yml", package = "WrightFisherSim"),
  initial_frequency = 0.8,
  mutation_rate = 0.001,
  seed = 42
)

# View and plot
print(results)
plot_wright_fisher(results)
```

**Complete documentation**: See `R_README.md`

---

## Core Concepts

### Wright-Fisher Model

The Wright-Fisher model describes genetic drift in an idealized population:
- Fixed population size `N`
- Non-overlapping generations
- Random mating
- Each individual in generation `t+1` is sampled from generation `t` with replacement

### Advanced Features

This simulator supports advanced evolutionary features. For detailed documentation, see the `docs/` directory:

- **[Mutations](docs/mutations.md)**: Bidirectional mutations between wild-type and mutant alleles
- **[Selection](docs/selection.md)**: Fitness-based selection with configurable coefficients
- **[Migration](docs/migrations.md)**: Continuous and pulse migration between populations
- **[Multiple Alleles](docs/multiple_alleles.md)**: Support for arbitrary number of alleles
- **[Configurable Allele Introduction](docs/configurable_allele_introduction.md)**: Dynamic introduction of new alleles

### Simulation Timeline

Each generation follows this sequence:

1. **Wright-Fisher sampling**: Random reproduction (with selection if specified)
2. **Mutation application**: Bidirectional mutations applied
3. **Migration**: Gene flow between populations (if specified)
4. **Pulse events**: Instantaneous admixture (if scheduled)

---

## Usage

### Basic Example

```python
from evolutionary_simulator.core import WrightFisherSim, plot_results

# Initialize simulator
sim = WrightFisherSim(
    demes_file_path='population_model.yml',
    initial_allele_frequency=0.8,
    mutation_rate=0.001,
    wild_type=0,
    seed=42
)

# Run simulation
results = sim.run()

# Visualize results
plot_results(results)
```

### With Mutations

```python
# Enable mutations
sim = WrightFisherSim(
    demes_file_path='population_model.yml',
    initial_allele_frequency=0.9,
    mutation_rate=0.001,  # 0.1% per generation
    wild_type=0,
    seed=42
)

results = sim.run()
```

### Multi-Allele System (Advanced)

```python
from dev.simulator import WrightFisherSim

# Multiple alleles with mutations
sim = WrightFisherSim(
    demes_file_path='population_model.yml',
    alleles=[0, 1, 2, 3],  # Wild-type + 3 mutants
    initial_allele_frequency={
        0: 0.7,  # Wild-type: 70%
        1: 0.1,  # Mutant 1: 10%
        2: 0.1,  # Mutant 2: 10%
        3: 0.1   # Mutant 3: 10%
    },
    mutation_rate=0.005,
    wild_type=0,
    seed=123
)

results = sim.run()
```

---

## API Reference

### WrightFisherSim

#### Class: `evolutionary_simulator.core.WrightFisherSim`

**Constructor Parameters**:

| Parameter                  | Type  | Default    | Description                                     |
| -------------------------- | ----- | ---------- | ----------------------------------------------- |
| `demes_file_path`          | str   | *required* | Path to Demes YAML file                         |
| `config_file_path`         | str   | None       | Path to configuration YAML file (for new alleles, etc.) |
| `alleles`                  | list  | [0, 1]     | List of allele identifiers                      |
| `initial_allele_frequency` | float/dict | 0.5   | Initial frequency of alleles (0.0-1.0) or dict mapping |
| `mutation_rate`            | float | 0.0        | Per-generation mutation probability (0.0-1.0)   |
| `wild_type`                | int   | 0          | Allele identifier for wild-type                 |
| `seed`                     | int   | None       | Random seed for reproducibility                 |
| `selection_coefficients`   | dict  | None       | Dictionary mapping alleles to selection coefficients |

**Methods**:

- `run()`: Execute the simulation
  - **Returns**: `dict` - Population names mapped to frequency histories
  - **Format**: `{population_name: [freq_gen0, freq_gen1, ..., freq_genN]}`

**Private Methods** (internal use):
- `_initialize_population(pop_name, size, ancestors, proportions)`: Create new population
- `_handle_migration(generation)`: Apply continuous migration
- `_handle_pulses(generation)`: Execute pulse events
- `_handle_mutations(pop_name)`: Apply bidirectional mutations

#### Class: `dev.simulator.WrightFisherSim` (Multi-allele)

**Additional Parameters**:

| Parameter                  | Type | Default | Description                               |
| -------------------------- | ---- | ------- | ----------------------------------------- |
| `alleles`                  | list | [0, 1]  | List of allele identifiers                |
| `initial_allele_frequency` | dict | None    | Dictionary mapping alleles to frequencies |

**Returns**: Dictionary with frequency dictionaries for each generation:
```python
{
    'PopulationA': [
        {0: 0.7, 1: 0.2, 2: 0.1},  # Generation 0
        {0: 0.68, 1: 0.22, 2: 0.1}, # Generation 1
        ...
    ]
}
```

### Utility Functions

#### `plot_results(results, title)`

Visualize simulation results. **Available directly when the package is installed** - import it from `evolutionary_simulator.core`.

**Parameters**:
- `results` (dict): Output from `sim.run()`
- `title` (str, optional): Plot title

**Behavior**:
- Creates line plot of allele frequencies over time
- Aligns all populations to end at the present
- Displays legend with population names
- Grid and axis labels included

**Usage after installation**:
```python
from evolutionary_simulator.core import WrightFisherSim, plot_results

results = sim.run()
plot_results(results)  # Directly available!
```

---

## Examples

### Example 1: Basic Drift Simulation

```python
from evolutionary_simulator.core import WrightFisherSim, plot_results

sim = WrightFisherSim(
    demes_file_path='dev/deme_test.yml',
    initial_allele_frequency=0.5,
    mutation_rate=0.0,  # No mutations
    seed=42
)

results = sim.run()
plot_results(results)
```

**Expected behavior**: Allele frequencies drift toward fixation (1.0) or loss (0.0).

### Example 2: Mutation-Drift Balance

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

**Expected behavior**: Variation maintained at intermediate frequencies due to mutation-drift balance.

### Example 3: Deleterious Mutation Accumulation

```python
sim = WrightFisherSim(
    demes_file_path='dev/deme_test.yml',
    initial_allele_frequency=0.99,  # 99% wild-type
    mutation_rate=0.0001,  # Realistic mutation rate
    wild_type=0,
    seed=42
)

results = sim.run()
```

**Biological interpretation**: Models accumulation of deleterious mutations in the absence of selection.

### Running Demo Scripts

```bash
# Test installation
python dev/test_mutation.py
```

---

## Population Definition Format

### Demes YAML Specification

Populations are defined using the [Demes specification](https://popsim-consortium.github.io/demes-spec-docs/). 

**Example**:

```yaml
description: Simple population split
time_units: generations
defaults:
  epoch:
    start_size: 100

demes:
  - name: Ancestral
    start_time: .inf
    epochs:
      - start_size: 100
        end_time: 50
        
  - name: Pop_A
    ancestors: [Ancestral]
    start_time: 50
    epochs:
      - start_size: 100
        end_size: 500
        
  - name: Pop_B
    ancestors: [Ancestral]
    start_time: 50
    epochs:
      - start_size: 100
        end_size: 20

migrations:
  - source: Pop_A
    dest: Pop_B
    rate: 0.05
    start_time: 40
    end_time: 10

pulses:
  - source: Pop_A
    dest: Pop_B
    proportion: 0.1
    time: 25
```

### Key Components

- **`demes`**: Population definitions with size histories
- **`migrations`**: Continuous gene flow between populations
- **`pulses`**: One-time admixture events
- **`start_time`**: Time in the past (backwards, 0 = present)
- **`epochs`**: Periods with specific population sizes

---


## Scientific Background

### Applications

1. **Neutral evolution**: Studying drift and mutation without selection
2. **Mutation load**: Accumulation of deleterious alleles
3. **Molecular clocks**: Mutation accumulation over time
4. **Population structure**: Effects of migration and splits
5. **Conservation genetics**: Loss of variation in small populations


## File Structure

```
wright-fisher-simulation/
├── evolutionary_simulator/       # Main package
│   ├── __init__.py
│   └── core.py                  # Prod Code
├── dev/                         # Development dir 
│   ├── simulator.py            # Dev code
│   ├── deme_test.yml           # Example population 
│   ├── test_mutation.py        # Unit tests
├── setup.py                     # Package configuration
├── requirements.txt             # Dependencies
└── README.md                   
```

---

## Performance Considerations

### Computational Complexity

- **Per generation**: O(N * P)
  - N = total individuals across all populations
  - P = number of populations

- **Total**: O(G * N * P)
  - G = number of generations

### Optimization Tips

1. **Reduce population sizes** for longer timescales
2. **Decrease mutation rate** if not studying mutation-drift balance
3. **Limit number of populations** in complex demographic models
4. **Use random seed** for reproducible debugging

---

## Troubleshooting

### ModuleNotFoundError

```bash
pip install -e .
```

### File path errors

Run scripts from project root:
```bash
python dev/test_mutation.py
```

### Plots not displaying

If running in a non-GUI environment:
```python
import matplotlib
matplotlib.use('Agg')  # Use before importing pyplot
import matplotlib.pyplot as plt

# ... run simulation ...

plt.savefig('output.png')  # Save instead of show
```

---

## Team Members

| Name                | ID      |
| ------------------- | ------- |
| Youssef Ahmed Afify | 1200883 |
| Hamza Ayman         | 1210218 |
| Hamsa Saber         | 1210359 |
| Salsabeel Mostafa   | 1210171 |

---


### References

- Kimura, M. (1964). "Diffusion models in population genetics." *Journal of Applied Probability*, 1(2), 177-232.
- Crow, J. F., & Kimura, M. (1970). *An Introduction to Population Genetics Theory*. Harper & Row.
- Ewens, W. J. (2004). *Mathematical Population Genetics*. Springer.
- Wright, S. (1931). "Evolution in Mendelian populations." *Genetics*, 16(2), 97-159.

---


## License

This project is provided for educational purposes in computational biology.

---

## Acknowledgments

- **Demes specification**: [PopSim Consortium](https://popsim-consortium.github.io/demes-spec-docs/)
- **Wright-Fisher model**: Sewall Wright and Ronald Fisher
- **Population genetics theory**: Motoo Kimura, James Crow, Warren Ewens
