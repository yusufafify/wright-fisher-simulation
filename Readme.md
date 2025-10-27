# Wright-Fisher Model Simulation of Genetic Drift

This project provides a simple Python simulation of **genetic drift** using the Wright-Fisher model. The script visualizes how the frequency of an allele can change randomly over several generations in a small population.



## Description

Genetic drift is a fundamental evolutionary mechanism where allele frequencies in a population change over generations due to random chance. This effect is most pronounced in small populations.

This script simulates this process by:
1.  **Initializing a population** of a fixed size with two alleles, 'A' and 'a', at a specified starting frequency.
2.  **Simulating generations** by creating each new generation through random sampling (with replacement) from the previous one. This means some individuals might not reproduce, while others might reproduce multiple times, purely by chance.
3.  **Tracking and plotting** the frequency of allele 'A' over time to show how it "drifts" towards either fixation (frequency of 1.0) or loss (frequency of 0.0).

---

## Prerequisites to Run the Simulation

Make sure you have Python and the `matplotlib` library installed. If you don't have `matplotlib`, you can install it using pip:

    pip install matplotlib
---

## Modifying Parameters

You can easily change the simulation's parameters by editing these variables at the top of the script:

* `population_size`: The total number of individuals in the population for each generation.
* `number_of_generations`: How many generations the simulation will run for.
* `initial_allele_A_frequency`: The starting frequency (from 0.0 to 1.0) of allele 'A'.

---

## Team Members

| Name      | ID        |
| :-------- | :-------- |
| *Youssef Ahmed Afify* | *1200883* |
| *Hamza Ayman* | *1210218* |
| *Hamsa Saber* | *1210359* |
| *Salsabeel Mostafa* | *1210171* |