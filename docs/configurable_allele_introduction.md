# Configurable Allele Introduction

This guide explains how to introduce new alleles at specific generations and populations during a WrightFisher simulation, with minimal code examples and focus on concepts and use cases.

---

## Table of Contents
1. [Concept Overview](#1-concept-overview)
2. [YAML Configuration Schema](#2-yaml-configuration-schema)
3. [How It Works](#3-how-it-works)
4. [Usage Examples](#4-usage-examples)
5. [Expected Output](#5-expected-output)
6. [Pitfalls and Best Practices](#6-pitfalls-and-best-practices)
7. [Literature](#7-literature)

---

## 1. Concept Overview

**Problem**: Real populations don't start with all alleles present. New mutations, invasive species, or population mixing introduce novel alleles over time.

**Solution**: Declare future alleles in a YAML config file, and the simulator automatically injects them at specified generations and populations.

### Key Ideas
- **Absence then presence**: Future alleles are NOT generated at the starting generation; they appear only when their scheduled time arrives.
- **Per-population targeting**: Each allele introduction targets one specific deme.
- **Immediate interaction**: Once introduced, the allele is subject to selection, mutation, migration, and genetic drift in the same generation.
- **Backward time**: Higher generation numbers = further past. Generation 0 = present.

---

## 2. YAML Configuration Schema

Create a YAML file (e.g., config.yml) with the structure:

\\\yaml
new_alleles:
  - allele: "D"              # unique identifier (string or int)
    population: "Pop_A"      # target deme name
    start_time: 45           # generation (backward) when introduced
    initial_frequency: 0.2   # fraction of individuals, default 0.05

  - allele: "C"
    population: "Pop_B"
    start_time: 30
    initial_frequency: 0.3
\\\

**Rules:**
- \allele\, \population\, \start_time\ are required.
- The allele must also be listed in the \alleles=[...]\ parameter of \WrightFisherSim()\.
- \initial_frequency\ is the fraction of the population to convert; at least 1 individual is always injected.
- If the target population doesn't exist at that generation, the introduction is skipped silently.

---

## 3. How It Works

**Simulator Setup:**
1. Read config file.
2. Future alleles (in \
new_alleles\) are **removed from the initial active set**.
3. Only "active" alleles appear in generation 0.
4. Fitness precomputed for active and future alleles.

**Example:**
\\\python
from evolutionary_simulator.core import WrightFisherSim

sim = WrightFisherSim(
    demes_file_path="demo.yml",
    config_file_path="config.yml",
    alleles=["A", "B", "C", "D"],
    initial_allele_frequency={"A": 0.7, "B": 0.3},
    selection_coefficients={"C": 0.02, "D": -0.01},
    seed=42
)
\\\

At init: \C\ and \D\ are future; active set is \["A", "B"]\.

**Generation Loop (backward in time):**
1. Initialize new demes
2. **Inject new alleles**  alleles for this generation appear here
3. Selection
4. Mutation
5. Migration & pulses
6. Record frequencies

New alleles replace a random subset. They immediately participate in selection and drift.

---

## 4. Usage Examples

### 4.1 Single Allele (Beneficial Mutation)

**config.yml:**
\\\yaml
new_alleles:
  - allele: "mut"
    population: "Pop_A"
    start_time: 50
    initial_frequency: 0.01
\\\

**Python:**
\\\python
sim = WrightFisherSim(
    demes_file_path="simple.yml",
    config_file_path="config.yml",
    alleles=["WT", "mut"],
    initial_allele_frequency={"WT": 1.0},
    selection_coefficients={"WT": 0.0, "mut": 0.05},
    seed=123
)
history = sim.run()
# 'mut' appears at gen 50, sweeps upward
\\\

### 4.2 Multiple Populations (Out-of-Africa)

**config.yml:**
\\\yaml
new_alleles:
  - allele: "var_A"
    population: "YRI"
    start_time: 5000
    initial_frequency: 0.05
  - allele: "var_B"
    population: "CEU"
    start_time: 2000
    initial_frequency: 0.10
  - allele: "var_C"
    population: "CHB"
    start_time: 1000
    initial_frequency: 0.08
\\\

Each variant arises in its population; migration spreads them.

### 4.3 With Mutation and Selection

\\\python
sim = WrightFisherSim(
    demes_file_path="simple.yml",
    config_file_path="config.yml",
    alleles=["WT", "del"],
    initial_allele_frequency={"WT": 1.0},
    mutation_rate=0.001,
    wild_type="WT",
    selection_coefficients={"WT": 0.0, "del": -0.02},
    seed=456
)
history = sim.run()
# 'del' introduced, selection removes it, mutation re-introduces  balance
\\\

---

## 5. Expected Output

\sim.run()\ returns frequencies per population per generation:

\\\python
{
    "Pop_A": [
        {"A": 0.70, "B": 0.30},               # start
        ...
        {"A": 0.60, "B": 0.20, "D": 0.20},   # after D intro at gen 45
        ...
    ],
    "Pop_B": [
        {"A": 0.50, "B": 0.20, "C": 0.30}    # after C intro at gen 30
    ]
}
\\\

- Before intro: future allele frequency = 0.0
- At intro: frequency  \initial_frequency\
- After: evolves under selection, drift, migration

---

## 6. Pitfalls and Best Practices

| Issue | Fix |
|-------|-----|
| Allele not in \alleles=[]\ | List all alleles (active + future). Init will error. |
| Population not born yet | Check deme \start_time\ vs intro \start_time\. Skipped silently. |
| Tiny deme + small frequency | \max(1, int(N*freq))\ injected; may exceed expected %. |
| Backward time confusion | Higher gen = further past. Gen 0 = present. |

**Best practices:**
- Test demes and config files separately first.
- Use \seed\ for reproducibility.
- Document why each allele is introduced.

---

## 7. Literature

- **Crow & Kimura (1970)**. *An Introduction to Population Genetics Theory*. WrightFisher basics.
- **Wakeley (2008)**. *Coalescent Theory*. Backward-time perspective.
- **Ewens (2004)**. *Mathematical Population Genetics*. Allele dynamics and drift.
- **Hudson (1990)**. "Gene genealogies and the coalescent process." Demographic events.
- **Gower et al. (2022)**. "Demes: a standard format." Demes specification.

---

## Summary

**Schedule new alleles** in a YAML config:
\\\yaml
new_alleles:
  - allele: X
    population: Pop
    start_time: T
    initial_frequency: F
\\\

**Pass to simulator:**
\\\python
sim = WrightFisherSim(..., config_file_path="config.yml", alleles=[...])
history = sim.run()
\\\

Allele \X\ appears in \Pop\ at generation \T\ with ~\F\ initial frequency. It then evolves naturally.

**Use for:** adaptive mutations, invasive species, admixture, robustness testing.
