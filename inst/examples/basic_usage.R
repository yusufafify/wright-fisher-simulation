# Wright-Fisher Simulation Examples in R

library(WrightFisherSim)
library(ggplot2) # For saving plots with ggsave

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

# Save plot
ggsave("example1_drift.png", p1, width = 10, height = 6)
cat("✓ Saved plot to example1_drift.png\n")


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

# Save plot
ggsave("example2_mutation.png", p2, width = 10, height = 6)
cat("✓ Saved plot to example2_mutation.png\n")


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
p_no_mut <- plot_wright_fisher(no_mut, title = "No Mutations")
p_with_mut <- plot_wright_fisher(with_mut, title = "With Mutations (μ=0.01)")

# Display plots side by side (requires gridExtra package)
if (require(gridExtra, quietly = TRUE)) {
    combined_plot <- grid.arrange(p_no_mut, p_with_mut, ncol = 2)
    ggsave("example3_comparison.png", combined_plot, width = 16, height = 6)
    cat("✓ Saved comparison plot to example3_comparison.png\n")
} else {
    cat("Note: Install gridExtra package to create comparison plots\n")
    cat("  install.packages('gridExtra')\n")
}


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

cat("\n✓ All examples completed!\n")
cat("Check the current directory for saved plots.\n")
