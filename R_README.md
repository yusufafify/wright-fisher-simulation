# WrightFisherSim R Package

R interface for the Wright-Fisher population genetics simulator with mutation support.

---

## Installation (Simple 3-Step Process)

### Step 1: Install from GitHub

```r
# Install devtools if needed
install.packages("devtools")

# Install WrightFisherSim
devtools::install_github("yusufafify/wright-fisher-simulation")
```

### Step 2: Setup Python (In Fresh R Session)

**Restart R first**, then:

```r
# Install Python dependencies
reticulate::py_install(c("demes", "matplotlib", "numpy"), pip = TRUE)
```

### Step 3: Restart R and Use

**Restart R again**, then:

```r
library(WrightFisherSim)

# Run a simulation
results <- wright_fisher_sim(
  demes_file = system.file("dev/deme_test.yml", package = "WrightFisherSim"),
  initial_frequency = 0.8,
  mutation_rate = 0.001,
  seed = 42
)

print(results)
plot_wright_fisher(results)
```

---

## Expected Output

When everything is working correctly, you'll see:

```
✓ Python environment initialized successfully
Simulation running from generation 100 to 0...
Gen initialized: Ancestral (Size: 100)
Gen initialized: Pop_A (Size: 100)
Gen initialized: Pop_B (Size: 100)
✓ Simulation complete
```

---

## Quick Reference

### Basic Usage

```r
library(WrightFisherSim)

# Pure drift (no mutations)
results <- wright_fisher_sim(
  demes_file = "path/to/model.yml",
  initial_frequency = 0.5,
  mutation_rate = 0.0,
  seed = 42
)

# With mutations
results <- wright_fisher_sim(
  demes_file = "path/to/model.yml",
  initial_frequency = 0.9,
  mutation_rate = 0.005,
  wild_type = 0,
  seed = 123
)

# Visualize
plot_wright_fisher(results, title = "My Simulation")

# Save plot
library(ggplot2)
p <- plot_wright_fisher(results)
ggsave("output.png", p, width = 10, height = 6)
```

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'demes'"

This means Python packages aren't installed.

**Fix:**
1. Restart R
2. Run: `reticulate::py_install(c("demes", "matplotlib", "numpy"), pip = TRUE)`
3. Restart R again
4. Try again

### "cannot change value of locked binding"

This was fixed in recent versions.

**Fix:**
1. Update to latest version: `devtools::install_github("yusufafify/wright-fisher-simulation", force = TRUE)`
2. Restart R

### Can't find test file

```r
# Check installation
system.file(package = "WrightFisherSim")

# Use local file
results <- wright_fisher_sim(
  demes_file = "dev/deme_test.yml",  # or full path
  initial_frequency = 0.8,
  mutation_rate = 0.001
)
```

---

## Installation Order (Important!)

**Correct order:**
1. Install R package
2. **Restart R**
3. Install Python packages
4. **Restart R**
5. Use package

**Common mistakes:**
- Installing Python packages after loading the library
- Not restarting R between steps
- Trying to use immediately after Python install

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
