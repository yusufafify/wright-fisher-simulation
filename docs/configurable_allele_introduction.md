# Configurable Allele Introduction

This guide explains how to introduce new alleles at specific generations and populations during a Wright–Fisher simulation, with minimal code examples and focus on concepts and use cases.

---

## Table of Contents
1. [Concept Overview](#1-concept-overview)
2. [YAML Configuration Schema](#2-yaml-configuration-schema)
3. [Implementation Details](#3-implementation-details)
4. [Usage Examples](#4-usage-examples)
5. [Expected Output](#5-expected-outputs)
6. [Advanced Patterns](#6-advanced-patterns)
7. [Common Pitfalls](#7-common-pitfalls)
8. [Testing & Validation](#8-testing-and-validation)
9. [Literature References](#9-literature-references)

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

Create a YAML file (e.g., `config.yml`) with the structure:

```yaml
new_alleles:
  - allele: "D"              # unique identifier (string or int)
    population: "Pop_A"      # target deme name
    start_time: 45           # generation (backward) when introduced
    initial_frequency: 0.2   # fraction of individuals, default 0.05

  - allele: "C"
    population: "Pop_B"
    start_time: 30
    initial_frequency: 0.3
```

**Rules:**
- `allele`, `population`, `start_time` are required.
- The allele must also be listed in the `alleles=[...]` parameter of `WrightFisherSim()`.
- `initial_frequency` is the fraction of the population to convert; at least 1 individual is always injected.
- If the target population doesn't exist at that generation, the introduction is skipped silently.---

## 3. Implementation Details

All logic lives in `dev/simulator.py` within `WrightFisherSim`.

### 3.1 Initialization (active vs future alleles)

```python
all_potential_alleles = alleles if alleles else [0, 1]
self.new_alleles_config = self.config.get("new_alleles", [])
future_alleles_set = set()

for entry in self.new_alleles_config:
		required_fields = {"allele", "population", "start_time"}
		if not required_fields.issubset(entry):
				raise ValueError(...)
		if entry["allele"] not in all_potential_alleles:
				raise ValueError("Allele ... not in alleles array")
		t = int(entry["start_time"])
		self.alleles_by_time.setdefault(t, []).append(entry)
		future_alleles_set.add(entry["allele"])

self.alleles = [a for a in all_potential_alleles if a not in future_alleles_set]
```

- **Active set**: `self.alleles` starts with all alleles minus future ones. This prevents premature appearance.
- **Fitness precomputation**: Fitness values are computed for active **and** future alleles (`self.fitness`), so selection works immediately upon introduction.

### 3.2 Generation loop order

For each generation `t` (from `start_generation` down to `0`):
1. Births / deme initialization
2. **New allele introduction** (`_handle_new_alleles(t)`)
3. Selection (fitness-weighted sampling)
4. Mutation (forward/backward)
5. Migration and pulses
6. Census / frequency recording

### 3.3 Allele injection logic

```python
def _handle_new_alleles(self, generation):
		if generation not in self.alleles_by_time:
				return
		for entry in self.alleles_by_time[generation]:
				pop = entry["population"]
				allele = entry["allele"]
				freq = entry.get("initial_frequency", 0.05)
				if pop not in self.current_populations:
						continue
				pop_alleles = self.current_populations[pop]
				if len(pop_alleles) == 0:
						continue
				if allele not in self.alleles:
						self.alleles.append(allele)
				N = max(1, int(len(pop_alleles) * freq))
				indices = random.sample(range(len(pop_alleles)), N)
				for i in indices:
						pop_alleles[i] = allele
```

Notes:
- If the allele already exists in that population, individuals are overwritten; a warning is printed.
- Injection happens **before** selection/mutation/migration in that generation, so the new allele immediately participates in those processes.

---

## 4. Usage Examples

### 4.1 Minimal example (single new allele)

**Demography** (`dev/deme_test.yml` excerpt):
```yaml
demes:
	- name: Ancestral
		start_time: .inf
		epochs: [{start_size: 100, end_time: 50}]
	- name: Pop_A
		ancestors: [Ancestral]
		start_time: 50
		epochs: [{start_size: 100, end_size: 500}]
```

**Allele schedule** (`dev/config_structure.yml` excerpt):
```yaml
new_alleles:
	- allele: "D"
		population: "Pop_A"
		start_time: 45
		initial_frequency: 0.2
```

**Python**:
```python
from evolutionary_simulator.core import WrightFisherSim

sim = WrightFisherSim(
		demes_file_path="dev/deme_test.yml",
		config_file_path="dev/config_structure.yml",
		alleles=["A", "B", "D"],            # include all potential alleles
		initial_allele_frequency={"A": 0.7, "B": 0.3},
		mutation_rate=0.0,
		wild_type="A",
		seed=7,
		selection_coefficients={"A": 0.0, "B": 0.0, "D": -0.01}
)

history = sim.run()

# Inspect Pop_A at generation 45 (after introduction)
gen45_idx = sim.graph["Pop_A"].start_time - 45
print(history["Pop_A"][gen45_idx])
```

**Expected behavior**:
- Before gen 45: allele `D` frequency in `Pop_A` is 0.0.
- At gen 45: ~20% of individuals become `D` (at least one individual).
- After gen 45: `D` experiences selection (slightly deleterious here) and drift.

### 4.2 Multiple demes and staggered introductions

**Demography** (`dev/deme_test.yml` full) includes `Pop_A`, `Pop_B`, and migration from `Pop_A` to `Pop_B`.

**Allele schedule** (same file):
```yaml
new_alleles:
	- allele: "D"
		population: "Pop_A"
		start_time: 45
		initial_frequency: 0.2
	- allele: "C"
		population: "Pop_B"
		start_time: 30
		initial_frequency: 0.3
```

**Python**:
```python
sim = WrightFisherSim(
		demes_file_path="dev/deme_test.yml",
		config_file_path="dev/config_structure.yml",
		alleles=["A", "B", "C", "D"],
		initial_allele_frequency={"A": 0.7, "B": 0.3},
		selection_coefficients={"C": 0.02, "D": -0.01},
		seed=11
)
history = sim.run()

# Check Pop_B at its introduction generation (30)
gen30_idx = sim.graph["Pop_B"].start_time - 30
print(history["Pop_B"][gen30_idx])

# Migration can carry D from Pop_A into Pop_B after gen 40
```

**Expected behavior**:
- `D` appears in `Pop_A` at gen 45, can migrate to `Pop_B` (rate 0.05) before `C` is introduced in `Pop_B` at gen 30.
- At gen 30, `C` is injected into `Pop_B` (~30% of individuals), immediately subject to selection `s=0.02`.

### 4.3 Human Out-of-Africa style schedule

Using `dev/human_out_of_africa_config.yml` with multiple alleles introduced in different populations and times:
```yaml
new_alleles:
	- allele: "A"  # ancient in Africa
		population: "YRI"
		start_time: 9000
		initial_frequency: 0.05
	- allele: "B"  # after CEU split
		population: "CEU"
		start_time: 5000
		initial_frequency: 0.10
	- allele: "C"  # East Asian specific
		population: "CHB"
		start_time: 600
		initial_frequency: 0.15
	- allele: "D"  # late recent in Europe
		population: "CEU"
		start_time: 300
		initial_frequency: 0.05
```

**Python skeleton**:
```python
sim = WrightFisherSim(
		demes_file_path="dev/human_out_of_africa.yml",
		config_file_path="dev/human_out_of_africa_config.yml",
		alleles=["A", "B", "C", "D", "WT"],
		initial_allele_frequency={"WT": 1.0},
		wild_type="WT",
		selection_coefficients={"A": 0.0, "B": 0.01, "C": 0.015, "D": 0.005},
		seed=1234
)
history = sim.run()
```

**Expected behavior**:
- Each allele appears only in its specified population/time.
- Migration and pulses can spread alleles across demes after introduction.
- Selection acts immediately according to the provided coefficients.

---

## 5. Expected Outputs

`run()` returns a dict: `population -> list[freq_dict]`, ordered from `start_generation` down to `0`.

Example snippet after introductions:
```python
{
	"Pop_A": [
		{"A": 0.70, "B": 0.30},             # at start_generation
		...,
		{"A": 0.55, "B": 0.25, "D": 0.20}, # at generation 45
		...
	],
	"Pop_B": [
		{"A": 0.70, "B": 0.30},
		...,
		{"A": 0.40, "B": 0.30, "C": 0.30}, # at generation 30
		...
	]
}
```

Properties:
- Frequencies per population sum to 1.0 over known alleles; absent alleles get 0.0.
- Extinct populations log all-zero frequency dicts for alignment.
- Alleles remain tracked even if they drift to 0 later.

---

## 6. Advanced Patterns

- **Repeated introductions of the same allele**: Allowed across demes or times; each event overwrites a fresh random subset.
- **Mutation interplay**: With `mutation_rate > 0`, introduced alleles can mutate back to `wild_type` (backward) or from `wild_type` to other mutants (forward) depending on the active set.
- **Selection immediately applied**: Fitness weights are precomputed for future alleles, so they are subject to selection the generation they appear.
- **Pulses and migration**: Pulses/migration run after introduction and selection in that generation, so newly introduced alleles can move instantly if events coincide.
- **Dynamic active set**: `self.alleles` expands when a future allele first appears, ensuring it is included in frequency tracking thereafter.

---

## 7. Common Pitfalls

- **Allele not listed in `alleles`**: Initialization fails. Always list every potential allele (active + future).
- **Population not yet born**: If `start_time` precedes the deme’s start, the event is skipped; align timings with demography.
- **Tiny populations**: `int(N * freq)` then `max(1, ...)` may inject a larger-than-expected fraction when `N` is small.
- **Backward-time intuition**: Higher `start_time` = earlier; generation 0 = present.
- **Zero-length populations**: If size is 0 at that generation, introduction is skipped; ensure demographic sizes are >0 where needed.

---

## 8. Testing and Validation

### 8.1 Deterministic presence/absence checks
Run with `seed` set. Verify that before `start_time`, the allele frequency is exactly 0.0; at `start_time`, it jumps to ~`initial_frequency` (rounded by `max(1, int(N*freq)) / N`).

### 8.2 Interaction with selection
Give the introduced allele a strong `s` (positive or negative) and confirm immediate trajectory change in the next census.

### 8.3 Migration propagation
Place introduction in a source deme and verify appearance in a destination deme only after migration windows open.

### 8.4 Edge: extinct populations
Force a deme to size 0 at introduction time; ensure no crash and frequency logs remain all-zero.

---

## 9. Literature References

- Crow, J.F. & Kimura, M. (1970). *An Introduction to Population Genetics Theory*. Harper & Row. — Classical Wright–Fisher with mutation/selection.
- Ewens, W.J. (2004). *Mathematical Population Genetics: I. Theoretical Introduction* (2nd ed.). Springer. — Allele frequency dynamics and drift.
- Wakeley, J. (2008). *Coalescent Theory: An Introduction*. Roberts & Company. — Backward-time framing and demographic histories.
- Hudson, R.R. (1990). "Gene genealogies and the coalescent process." *Oxford Surveys in Evolutionary Biology* 7:1–44. — Demography and allele histories.
- Gower, G. et al. (2022). "Demes: a standard format for demographic models." *Genetics* 222(3): iyac131. — Demes specification underpinning demographic inputs.


