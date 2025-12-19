import random
import matplotlib.pyplot as plt

population_size = 20
number_of_generations = 50
initial_allele_A_frequency = 0.5

# We represent the 'A' allele as 1 and the 'a' allele as 0.
current_population_alleles = [
    1 if random.random() < initial_allele_A_frequency else 0
    for _ in range(population_size)
]

allele_A_frequencies_over_time = [sum(current_population_alleles) / population_size]

for _ in range(number_of_generations):
    # The next generation's alleles are randomly sampled from the current generation.
    next_generation_alleles = [
        random.choice(current_population_alleles) for _ in range(population_size)
    ]
    
    current_population_alleles = next_generation_alleles
    
    current_allele_A_frequency = sum(current_population_alleles) / population_size
    allele_A_frequencies_over_time.append(current_allele_A_frequency)

# Plot the frequency of allele 'A' across generations.
generation_numbers = range(number_of_generations + 1)
plt.plot(generation_numbers, allele_A_frequencies_over_time)

plt.xlabel("Generation")
plt.ylabel("Frequency of allele A")
plt.title("Simple Wright–Fisher Simulation of Genetic Drift")
plt.grid(True)
plt.show()