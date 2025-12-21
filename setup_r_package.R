# Setup script for WrightFisherSim R package
# Run this ONCE after installing the package

cat("Setting up WrightFisherSim R Package\n")
cat("====================================\n\n")

# Step 1: Install Python packages
cat("Step 1: Installing Python dependencies...\n")

required_packages <- c("demes", "matplotlib", "numpy")

for (pkg in required_packages) {
    cat("  Installing", pkg, "...\n")
    tryCatch(
        {
            reticulate::py_install(pkg, pip = TRUE)
            cat("  ✓", pkg, "installed\n")
        },
        error = function(e) {
            cat("  ✗ Failed to install", pkg, "\n")
            cat("    Error:", conditionMessage(e), "\n")
        }
    )
}

cat("\nStep 2: Testing package...\n")

# Restart R session recommended message
cat("\n")
cat("==================================================\n")
cat("IMPORTANT: Restart your R session now!\n")
cat("==================================================\n")
cat("\nAfter restarting R, run:\n")
cat("  library(WrightFisherSim)\n")
cat("  source('test_package_after_install.R')\n")
cat("\nPython packages installed:\n")
for (pkg in required_packages) {
    available <- reticulate::py_module_available(pkg)
    cat("  ", pkg, ":", ifelse(available, "✓ Available", "✗ Not available"), "\n")
}
cat("\n")
