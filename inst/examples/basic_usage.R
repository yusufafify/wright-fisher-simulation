# Wright-Fisher Simulation Examples in R

library(WrightFisherSim)

# Example 1: Basic simulation without mutations
# ----------------------------------------------
cat("Example 1: Pure genetic drift\n")

results1 <- wright_fisher_sim(
    demes_file = system.file("dev/deme_test.yml", package = "WrightFisherSim"),
    initial_frequency = 0.5,
    mutation_rate = 0.0, # No mutations
    seed = 42
)

print(results1)
summary(results1)

# Plot results
p1 <- plot_wright_fisher(results1, title = "Pure Genetic Drift")
print(p1)


# Example 2: With mutations
# --------------------------
cat("\n\nExample 2: Mutation-drift balance\n")

results2 <- wright_fisher_sim(
    demes_file = system.file("dev/deme_test.yml", package = "WrightFisherSim"),
    initial_frequency = 0.8,
    mutation_rate = 0.005, # 0.5% mutation rate
    seed = 123
)

print(results2)
summary(results2)

# Plot results with custom title
p2 <- plot_wright_fisher(
    results2,
    title = "Wright-Fisher with Mutations",
    show_params = TRUE
)
print(p2)


# Example 3: Comparing scenarios
# -------------------------------
cat("\n\nExample 3: Comparing drift vs mutation\n")


# Run multiple simulations
no_mut <- wright_fisher_sim(
    demes_file = system.file("dev/deme_test.yml", package = "WrightFisherSim"),
    initial_frequency = 0.5,
    mutation_rate = 0.0,
    seed = 456
)

with_mut <- wright_fisher_sim(
    demes_file = system.file("dev/deme_test.yml", package = "WrightFisherSim"),
    initial_frequency = 0.5,
    mutation_rate = 0.01,
    seed = 456
)

# Create comparison plots
library(gridExtra)
p_no_mut <- plot_wright_fisher(no_mut, title = "No Mutations")
p_with_mut <- plot_wright_fisher(with_mut, title = "With Mutations (μ=0.01)")

grid.arrange(p_no_mut, p_with_mut, ncol = 2)


# Example 4: Extracting specific population data
# -----------------------------------------------
cat("\n\nExample 4: Working with population data\n")

# Get frequency trajectory for specific population
ancestral_freqs <- results2$results$Ancestral
cat("Ancestral population frequencies (first 10 generations):\n")
print(head(ancestral_freqs, 10))

# Calculate statistics
cat(sprintf("\nMean frequency: %.4f\n", mean(unlist(ancestral_freqs))))
cat(sprintf("SD frequency: %.4f\n", sd(unlist(ancestral_freqs))))
cat(sprintf("Min frequency: %.4f\n", min(unlist(ancestral_freqs))))
cat(sprintf("Max frequency: %.4f\n", max(unlist(ancestral_freqs))))
