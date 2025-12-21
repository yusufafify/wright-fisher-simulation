#' Wright-Fisher Simulator
#'
#' @description
#' A Wright-Fisher model simulator for population genetics supporting genetic drift,
#' bidirectional mutations, migration, and complex demographic scenarios.
#'
#' @docType package
#' @name WrightFisherSim-package
#' @aliases WrightFisherSim
#' @import reticulate
#' @importFrom ggplot2 ggplot aes geom_line labs scale_y_continuous theme_minimal theme element_text ggsave
#' @importFrom utils head
NULL

# Declare global variables to avoid R CMD check NOTEs
utils::globalVariables(c("Generation", "Frequency", "Population"))

# Package environment to store Python module reference
.pkg_env <- new.env(parent = emptyenv())
.pkg_env$wright_fisher_py <- NULL

#' @keywords internal
.onLoad <- function(libname, pkgname) {
    .pkg_env$wright_fisher_py <- NULL
}

#' Initialize Python Environment
#'
#' Sets up the Python environment and imports the Wright-Fisher simulator module.
#' This is called automatically when using the simulator functions.
#'
#' @param python_path Optional path to Python executable. If NULL, uses default.
#' @return Invisible NULL
#' @export
#' @examples
#' \dontrun{
#' setup_python()
#' }
setup_python <- function(python_path = NULL) {
    # Configure Python before it initializes
    if (!is.null(python_path)) {
        reticulate::use_python(python_path, required = TRUE)
    }

    # Check and install Python packages BEFORE importing anything
    # This must happen before Python initializes
    required_packages <- c("demes", "matplotlib", "numpy")

    for (pkg in required_packages) {
        if (!reticulate::py_module_available(pkg)) {
            message("Installing Python package: ", pkg)
            tryCatch(
                {
                    reticulate::py_install(pkg, pip = TRUE)
                },
                error = function(e) {
                    warning(
                        "Could not install ", pkg, " automatically. ",
                        "Please install manually:\n",
                        "  reticulate::py_install(c('demes', 'matplotlib', 'numpy'))\n",
                        "Or in Python:\n",
                        "  pip install demes matplotlib numpy"
                    )
                }
            )
        }
    }

    # Get package installation path
    pkg_path <- system.file(package = "WrightFisherSim")

    if (pkg_path == "") {
        # Development mode - use current directory
        pkg_path <- getwd()
    }

    # Import sys and add package path
    sys <- reticulate::import("sys", convert = TRUE)

    # The evolutionary_simulator module is in inst/ which becomes the package root
    if (!pkg_path %in% sys$path) {
        sys$path <- c(pkg_path, sys$path)
    }

    # Try to import the module
    tryCatch(
        {
            # Store in package environment instead of using locked binding
            .pkg_env$wright_fisher_py <- reticulate::import("evolutionary_simulator.core")
            message("✓ Python environment initialized successfully")
        },
        error = function(e) {
            stop(
                "\nFailed to import evolutionary_simulator module.\n\n",
                "Troubleshooting steps:\n",
                "1. Make sure Python packages are installed:\n",
                "   reticulate::py_install(c('demes', 'matplotlib', 'numpy'))\n\n",
                "2. Restart R and try again\n\n",
                "3. Check package installation:\n",
                "   Package path: ", pkg_path, "\n",
                "   Module location: ", pkg_path, "/evolutionary_simulator\n\n",
                "Original error: ", conditionMessage(e)
            )
        }
    )

    invisible(NULL)
}

#' Run Wright-Fisher Simulation
#'
#' @description
#' Simulates genetic drift and mutation in structured populations using the
#' Wright-Fisher model. Supports complex demographic scenarios defined via
#' Demes YAML files.
#'
#' @param demes_file Path to Demes YAML file defining population structure
#' @param initial_frequency Initial frequency of wild-type allele (0-1)
#' @param mutation_rate Per-generation mutation probability (0-1). Default: 0
#' @param wild_type Integer identifier for wild-type allele. Default: 0
#' @param seed Random seed for reproducibility. Default: NULL
#'
#' @return A list containing:
#'   \item{results}{Named list of allele frequency trajectories for each population}
#'   \item{populations}{Vector of population names}
#'   \item{parameters}{List of simulation parameters}
#'
#' @export
#' @examples
#' \dontrun{
#' # Basic simulation
#' results <- wright_fisher_sim(
#'     demes_file = "dev/deme_test.yml",
#'     initial_frequency = 0.8,
#'     mutation_rate = 0.001,
#'     seed = 42
#' )
#'
#' # Plot results
#' plot_wright_fisher(results)
#' }
wright_fisher_sim <- function(demes_file,
                              initial_frequency = 0.5,
                              mutation_rate = 0.0,
                              wild_type = 0L,
                              seed = NULL) {
    # Initialize Python if needed
    if (is.null(.pkg_env$wright_fisher_py)) {
        setup_python()
    }

    # Validate inputs
    if (!file.exists(demes_file)) {
        stop("Demes file not found: ", demes_file)
    }

    if (initial_frequency < 0 || initial_frequency > 1) {
        stop("initial_frequency must be between 0 and 1")
    }

    if (mutation_rate < 0 || mutation_rate > 1) {
        stop("mutation_rate must be between 0 and 1")
    }

    # Convert seed to integer if provided
    if (!is.null(seed)) {
        seed <- as.integer(seed)
    }

    # Create simulator instance
    sim <- .pkg_env$wright_fisher_py$WrightFisherSim(
        demes_file_path = demes_file,
        initial_allele_frequency = initial_frequency,
        mutation_rate = mutation_rate,
        wild_type = as.integer(wild_type),
        seed = seed
    )

    # Run simulation
    results <- sim$run()

    # Convert Python dict to R list
    results_list <- reticulate::py_to_r(results)

    # Return structured results
    structure(
        list(
            results = results_list,
            populations = names(results_list),
            parameters = list(
                demes_file = demes_file,
                initial_frequency = initial_frequency,
                mutation_rate = mutation_rate,
                wild_type = wild_type,
                seed = seed
            )
        ),
        class = "wright_fisher_results"
    )
}

#' Plot Wright-Fisher Simulation Results
#'
#' @description
#' Creates a line plot showing allele frequency trajectories for all populations
#' in the simulation.
#'
#' @param results Output from \code{wright_fisher_sim()}
#' @param title Plot title. Default: "Wright-Fisher Simulation"
#' @param show_params Whether to show parameters in subtitle. Default: TRUE
#'
#' @return A ggplot2 object
#' @export
#' @examples
#' \dontrun{
#' results <- wright_fisher_sim("dev/deme_test.yml", mutation_rate = 0.01)
#' plot_wright_fisher(results)
#' }
plot_wright_fisher <- function(results,
                               title = "Wright-Fisher Simulation",
                               show_params = TRUE) {
    if (!inherits(results, "wright_fisher_results")) {
        stop("results must be output from wright_fisher_sim()")
    }

    # Prepare data for plotting
    plot_data <- data.frame()

    # Find maximum number of generations
    max_gens <- max(sapply(results$results, length))

    for (pop_name in results$populations) {
        freqs <- results$results[[pop_name]]
        n_gens <- length(freqs)

        # Align to end at present (generation max_gens)
        start_gen <- max_gens - n_gens + 1

        pop_df <- data.frame(
            Generation = seq(start_gen, max_gens),
            Frequency = unlist(freqs),
            Population = pop_name
        )

        plot_data <- rbind(plot_data, pop_df)
    }

    # Create subtitle with parameters if requested
    subtitle <- NULL
    if (show_params) {
        params <- results$parameters
        subtitle <- sprintf(
            "μ = %.4f | Initial freq = %.2f | Seed = %s",
            params$mutation_rate,
            params$initial_frequency,
            ifelse(is.null(params$seed), "random", params$seed)
        )
    }

    # Create plot
    p <- ggplot(plot_data, aes(x = Generation, y = Frequency, color = Population)) +
        geom_line(linewidth = 1) +
        labs(
            title = title,
            subtitle = subtitle,
            x = "Generation",
            y = "Allele Frequency",
            color = "Population"
        ) +
        scale_y_continuous(limits = c(0, 1), breaks = seq(0, 1, 0.2)) +
        theme_minimal() +
        theme(
            plot.title = element_text(size = 16, face = "bold"),
            plot.subtitle = element_text(size = 11, color = "gray40"),
            axis.title = element_text(size = 12),
            legend.position = "right"
        )

    return(p)
}

#' Print method for Wright-Fisher results
#'
#' @param x A wright_fisher_results object
#' @param ... Additional arguments (unused)
#' @export
print.wright_fisher_results <- function(x, ...) {
    cat("Wright-Fisher Simulation Results\n")
    cat("=================================\n\n")

    cat("Populations:", paste(x$populations, collapse = ", "), "\n")
    cat("Generations simulated:\n")
    for (pop in x$populations) {
        cat(sprintf("  %s: %d\n", pop, length(x$results[[pop]])))
    }

    cat("\nParameters:\n")
    cat(sprintf("  Initial frequency: %.3f\n", x$parameters$initial_frequency))
    cat(sprintf("  Mutation rate: %.4f\n", x$parameters$mutation_rate))
    cat(sprintf("  Wild-type allele: %d\n", x$parameters$wild_type))
    cat(sprintf(
        "  Random seed: %s\n",
        ifelse(is.null(x$parameters$seed), "NULL", x$parameters$seed)
    ))

    invisible(x)
}

#' Summary method for Wright-Fisher results
#'
#' @param object A wright_fisher_results object
#' @param ... Additional arguments (unused)
#' @export
summary.wright_fisher_results <- function(object, ...) {
    cat("Wright-Fisher Simulation Summary\n")
    cat("================================\n\n")

    for (pop in object$populations) {
        freqs <- unlist(object$results[[pop]])
        cat(sprintf("\n%s:\n", pop))
        cat(sprintf("  Initial frequency: %.4f\n", freqs[1]))
        cat(sprintf("  Final frequency: %.4f\n", freqs[length(freqs)]))
        cat(sprintf("  Change: %+.4f\n", freqs[length(freqs)] - freqs[1]))
        cat(sprintf("  Mean frequency: %.4f\n", mean(freqs)))
        cat(sprintf("  SD frequency: %.4f\n", sd(freqs)))

        # Check for fixation/loss
        if (freqs[length(freqs)] == 1.0) {
            cat("  Status: Fixed (wild-type)\n")
        } else if (freqs[length(freqs)] == 0.0) {
            cat("  Status: Lost (all mutants)\n")
        } else {
            cat("  Status: Polymorphic\n")
        }
    }

    invisible(object)
}
