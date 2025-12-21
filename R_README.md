# WrightFisherSim R Package

R interface for the Wright-Fisher population genetics simulator with mutation support.

## Complete Installation Guide

### Step 1: Install the R Package

```r
# Install devtools if not already installed
install.packages("devtools")

# Install WrightFisherSim from GitHub
devtools::install_github("yusufafify/wright-fisher-simulation")
```

**Or from local source:**

```r
# Navigate to the package directory, then:
devtools::install()
```

### Step 2: Install Python Dependencies

**IMPORTANT**: Do this in a FRESH R session (restart R first)

```r
# Method A: Use the setup script (recommended)
source(system.file("setup_r_package.R", package = "WrightFisherSim"))

# Method B: Manual installation
reticulate::py_install(c("demes", "matplotlib", "numpy"), pip = TRUE)
```

### Step 3: Restart R

**CRITICAL**: You must restart R after installing Python packages.

- In RStudio: `Session -> Restart R`
- Or quit and reopen R

### Step 4: Test the Installation

```r
library(WrightFisherSim)

# Run test
source(system.file("test_package_after_install.R", package = "WrightFisherSim"))
```

---

## Troubleshooting

### Problem: "ModuleNotFoundError: No module named 'demes'"

**Solution**:

1. **Restart R completely** (close and reopen)
2. Install Python packages BEFORE loading the package:
   ```r
   # In fresh R session
   reticulate::py_install(c("demes", "matplotlib", "numpy"), pip = TRUE)
   ```
3. **Restart R again**
4. Load package:
   ```r
   library(WrightFisherSim)
   ```

### Problem: "ephemeral virtual environment" warning

This happens when you try to install Python packages after Python has already initialized.

**Solution**:
1. Restart R
2. Install Python packages FIRST (before any library calls)
3. Then use the package

### Problem: Can't find test file

```r
# Check package installation
system.file(package = "WrightFisherSim")

# Use local file if needed
results <- wright_fisher_sim(
  demes_file = "dev/deme_test.yml",  # Local path
  initial_frequency = 0.8,
  mutation_rate = 0.001,
  seed = 42
)
```

### Correct Installation Order

1. Install R package from GitHub
2. Restart R
3. Install Python packages
4. Restart R again
5. Use the package

### What NOT to Do

- Don't install Python packages after loading the package
- Don't skip restarting R
- Don't try to use the package immediately after installing Python packages


---

## Quick Start

After completing installation and setup:

```r
library(WrightFisherSim)

# Run a basic simulation
results <- wright_fisher_sim(
  demes_file = system.file("dev/deme_test.yml", package = "WrightFisherSim"),
  initial_frequency = 0.8,
  mutation_rate = 0.001,
  seed = 42
)

# View results
print(results)
summary(results)

# Plot
plot_wright_fisher(results)
```

---

## Detailed Usage

### Basic Simulation


```r
# Simulation without mutations (pure drift)
results <- wright_fisher_sim(
  demes_file = "path/to/population_model.yml",
  initial_frequency = 0.5,
  mutation_rate = 0.0,
  seed = 42
)
```

### With Mutations

```r
# Simulation with bidirectional mutations
results <- wright_fisher_sim(
  demes_file = "path/to/population_model.yml",
  initial_frequency = 0.9,
  mutation_rate = 0.005,  # 0.5% mutation rate
  wild_type = 0,
  seed = 123
)
```

### Visualization

```r
# Basic plot
plot_wright_fisher(results)

# Customized plot
plot_wright_fisher(
  results,
  title = "My Wright-Fisher Simulation",
  show_params = TRUE
)
```

### Extracting Data

```r
# Access frequency trajectories
ancestral_frequencies <- results$results$Ancestral

# Get population names
populations <- results$populations

# View parameters
params <- results$parameters

# Summary statistics
summary(results)
```

## Main Functions

### `wright_fisher_sim()`

Run a Wright-Fisher simulation with optional mutations.

**Parameters:**
- `demes_file`: Path to Demes YAML file
- `initial_frequency`: Initial wild-type frequency (0-1)
- `mutation_rate`: Per-generation mutation probability (0-1)
- `wild_type`: Wild-type allele identifier (default: 0)
- `seed`: Random seed for reproducibility

**Returns:** `wright_fisher_results` object containing simulation results

### `plot_wright_fisher()`

Visualize simulation results.

**Parameters:**
- `results`: Output from `wright_fisher_sim()`
- `title`: Plot title
- `show_params`: Show parameters in subtitle

**Returns:** ggplot2 object

### `setup_python()`

Manually configure Python environment (usually not needed).

**Parameters:**
- `python_path`: Optional path to Python executable

## Examples

See `inst/examples/basic_usage.R` for comprehensive examples:

```r
# View example file
file.show(system.file("examples/basic_usage.R", package = "WrightFisherSim"))

# Run examples
source(system.file("examples/basic_usage.R", package = "WrightFisherSim"))
```

## Population Definition (Demes Format)

Define populations using Demes YAML specification:

```yaml
description: Simple population model
time_units: generations
defaults:
  epoch:
    start_size: 100

demes:
  - name: Ancestral
    start_time: .inf
    epochs:
      - start_size: 100
        end_time: 50
        
  - name: Pop_A
    ancestors: [Ancestral]
    start_time: 50
    epochs:
      - start_size: 100
        end_size: 500

migrations:
  - source: Pop_A
    dest: Pop_B
    rate: 0.05
    start_time: 40
    end_time: 10
```

## Troubleshooting

### Python Not Found

```r
# Specify Python path explicitly
setup_python(python_path = "/path/to/python")
```

### Module Not Found

```r
# Reinstall Python packages
reticulate::py_install(c("demes", "matplotlib", "numpy"), pip = TRUE)
```

### Installation from GitHub

If you get authentication errors:

```r
# Use personal access token
devtools::install_github("yusufafify/wright-fisher-simulation", 
                         auth_token = "your_token_here")
```

## Documentation

Access help for any function:

```r
?wright_fisher_sim
?plot_wright_fisher
?setup_python
```

## Team

- Youssef Ahmed Afify (ID: 1200883)
- Hamza Ayman (ID: 1210218)
- Hamsa Saber (ID: 1210359)
- Salsabeel Mostafa (ID: 1210171)

## License

MIT License - see LICENSE file for details.

## Links

- GitHub: https://github.com/yusufafify/wright-fisher-simulation
- Issues: https://github.com/yusufafify/wright-fisher-simulation/issues
