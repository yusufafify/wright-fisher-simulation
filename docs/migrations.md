# Migrations

This document describes how migration events are modeled and applied in the Wright–Fisher simulation framework.
Migration allows individuals (and therefore alleles) to move between populations over time, enabling gene flow across demes.

Migration is defined using the **Demes specification** and is applied during the simulation run according to:
* Source population
* Destination population
* Migration rate
* Active time interval

Migration is applied after reproduction and mutation, but before allele frequencies are recorded for a generation.

---

## 1. Migration Model

At a given generation, migration is applied if:
* The migration event is active at time _t_
* Both source and destination populations exist and are non-empty

The expected number of migrants is:
```python
expected_migrants = N_dest × migration_rate
```
Where:
* `N_dest` is the current size of the destination population
* `migration_rate` is the proportion of migrants per generation

---

## 2. Stochastic Migration
Migration is stochastic, not deterministic.
* The integer part of `expected_migrants` is always applied
* The fractional part is applied probabilistically

Example:
* If expected_migrants = 3.4
    * 3 migrants are guaranteed
    * A 40% chance exists to add a 4th migrant
This ensures realistic population-level randomness.

---

## 3. Implementation Details
Migration is implemented in the `_handle_migration()` function:

```python
    def _handle_migration(self, generation):
            if not self.graph.migrations:
                return

            for migration in self.graph.migrations:
                if migration.end_time <= generation <= migration.start_time:
                    source = migration.source
                    dest = migration.dest
                    rate = migration.rate
```
Key steps:
* Check if migration is activ at current gen
* Sample migrants from source population
* Overwrite randomly selected individuals in the destination population
This approach preserves population size while changing allele composition

---

## 4. Pulse Migration Events
In addition to continuous migration, the simulator supports pulse events:
* Occur at a single generation
* Transfer a fixed proportion of individuals instantly
* Defined in the Demes file

Pulse migration is handled separately in `_handle_pulses()`.