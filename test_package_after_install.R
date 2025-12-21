# Test R Package Installation
# Run this after: devtools::install_github("yusufafify/wright-fisher-simulation")

library(WrightFisherSim)

# Test file path
test_file <- system.file("dev/deme_test.yml", package = "WrightFisherSim")

cat("Test file path:", test_file, "\n")
cat("File exists:", file.exists(test_file), "\n\n")

# Run simulation
cat("Running simulation...\n")
results <- wright_fisher_sim(
    demes_file = test_file,
    initial_frequency = 0.8,
    mutation_rate = 0.005,
    seed = 42
)

cat("\nSimulation complete!\n\n")

# Print results
print(results)

cat("\n")
summary(results)

# Create and save plot
cat("\nCreating plot...\n")
p <- plot_wright_fisher(results)

ggsave("test_output.png", p, width = 10, height = 6)
cat("Plot saved to: test_output.png\n")

cat("\n✓ All tests passed!\n")
