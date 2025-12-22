# Multiple Allele Support

This simulator extends the classical Wright–Fisher model by supporting
any number of alleles, including alleles that are
introduced dynamically during the simulation.

The implementation is designed to remain biologically consistent with
Wright–Fisher assumptions while supporting demographic events defined
using `demes`.

---

## 1. Allele Representation

Alleles are represented as **hashable identifiers** (e.g. integers or strings).
Each individual in a population carries exactly **one allele**.

Internally, each population is stored as a list:

```python
self.current_populations[pop_name] = [allele_1, allele_2, ..., allele_N]
```
where N is the population size at that generation.

This representation allows:
* Efficient sampling
* Straightforward mutation and migration
* Arbitrary allele identities

---
## 2. Allele Introduction
1. Declaring Alleles Explicitly
Alleles are passed using the alleles argument:

```python
sim = WrightFisherSim(
    demes_file_path="model.yml",
    config_file_path="config_structure.yml",
    alleles=["A", "B", "C", "D", "E"]
)
```
This tells the simulator:
* All alleles that may ever exist
* Including alleles introduced later during the simulation

2. Initial Allele Frequencies
Initial allele frequencies apply only to active alleles.
* Uniform frequencies (default)
```python
alleles=["A", "B", "C"]
```
Initial frequencies become:
```ini
A = 1/3, B = 1/3, C = 1/3
```

* User-defined frequencies
```python
initial_allele_frequency = {
    "A": 0.7,
    "B": 0.3
}
```
3. Introducing Alleles During the Simulation
New alleles are introduced dynamically using the configuration file:

```yaml
new_alleles:
  - allele: C
    population: popA
    start_time: 60
    initial_frequency: 0.1

```

## 3. Active vs Future Alleles

The simulator distinguishes between:
* Active alleles: alleles present at the start of the simulation
* Future alleles: alleles introduced at specific generations

This distinction prevents alleles from appearing before their
biologically defined introduction time.

```python
self.alleles = [
    a for a in all_potential_alleles
    if a not in future_alleles_set
]
```
Future alleles are excluded from the initial population and introduced
only when specified.

---

## 4. Allele Frequency Tracking
At each generation, allele frequencies are recorded as:

```python
freqs = {
    allele: count / population_size
    for allele in self.alleles
}
```
Alleles not present in a population automatically receive frequency 0.0.

This guarantees:
∑ f_i = 1  (summed over all alleles i)
for every population and generation.

---

## 5. Plotting Considerations
Allele frequencies are plotted **only within the lifespan of a population**.

Alleles are shown only after their introduction time, with missing values
represented as `NaN` to avoid biologically invalid curves.
```python
if allele in gen:
    allele_freqs.append(gen[allele])
else:
    allele_freqs.append(math.nan)
```

## 6. Mutation with Multiple Alleles
Mutation supports both:
* Forward mutation: wild-type → mutant allele
* Backward mutation: mutant → wild-type

```python
if current_allele == self.wild_type:
    population[i] = random.choice(mutant_alleles)
else:
    population[i] = self.wild_type
```

---

## 7. Interaction with Migration
Migration moves individuals, not allele frequencies.
As a result:
* Alleles can be introduced into new populations via migration
* Allele frequencies change indirectly
* No assumptions are made about allele compatibility between populations

Migration therefore interacts naturally with multiple alleles without special handling.

---

## 8. Edge Cases and Safegaurds 
The implementation safely handles:
1. Extinct populations

```python
if not pop_data:
    self.history[pop_name].append(zero_freqs.copy())
```

```python
if current_size <= 0:
        self.current_populations[pop_name] = []
    continue
```

**Explanation**
When a population goes extinct:
* It is stored as an empty list
* Its allele frequencies are recorded as all zeros
* The simulation continues without crashing

This ensures extinct populations remain aligned in time with others.

2. Alleles with zero frequency

```python
zero_freqs = {a: 0.0 for a in self.alleles}
```

**Explanation**
It creates a dictionary where:
* Keys → every allele currently known to the simulator (`self.alleles`)
* Values → 0.0 for each allele

Example:
```python
self.alleles = [0, 1, 2]

zero_freqs = {
    0: 0.0,
    1: 0.0,
    2: 0.0
}
```

```python
counts = Counter(pop_data)
freqs = {a: counts.get(a, 0) / len(pop_data) for a in self.alleles}
```
**Explanation**
`Counter` counts how many times each allele appears in pop_data.
For every allele in self.alleles:
* counts.get(a, 0)
    * Returns the count of allele a
    * Returns 0 if the allele is absent (no KeyError)
* len(pop_data)
    * Total number of individuals in the population
* Division computes the allele frequency

3. Migration between populations with different allele sets

```python
migrants = [random.choice(source_pop) for _ in range(num_migrants)]
for m in migrants:
    random_idx = random.randint(0, len(dest_pop) - 1)
    dest_pop[random_idx] = m
```