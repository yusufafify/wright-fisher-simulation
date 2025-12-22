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

## 2. Active vs Future Alleles

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
