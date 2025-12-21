"""
Quick test script to verify mutation functionality
"""

import sys
import os
sys.path.append('..')

from evolutionary_simulator.core import WrightFisherSim, plot_results

def test_mutation():
    """Test basic mutation feature"""
    
    # Determine the correct path to deme_test.yml
    if os.path.exists('deme_test.yml'):
        demes_file = 'deme_test.yml'
    elif os.path.exists('dev/deme_test.yml'):
        demes_file = 'dev/deme_test.yml'
    else:
        raise FileNotFoundError("Could not find deme_test.yml. Run from project root or dev/ directory.")
    
    # Test 1: Verify mutation parameters are set
    sim = WrightFisherSim(
        demes_file_path=demes_file,
        initial_allele_frequency=0.8,
        mutation_rate=0.01,
        wild_type=0,
        seed=42
    )
    
    assert sim.mutation_rate == 0.01, "Mutation rate not set correctly"
    assert sim.wild_type == 0, "Wild-type not set correctly"
    print("Parameters initialized correctly")
    
    # Test 2: Run simulation with mutations
    results = sim.run()
    print("Simulation completed successfully")
    
    # Test 3: Verify results structure
    assert len(results) > 0, "No results generated"
    for pop_name, freq_history in results.items():
        assert len(freq_history) > 0, f"No history for {pop_name}"
        print(f"✓ Population '{pop_name}': {len(freq_history)} generations recorded")
    
    # Test 4: Run without mutations (control)
    print("\nRunning simulation without mutations (control)...")
    sim_control = WrightFisherSim(
        demes_file_path=demes_file,
        initial_allele_frequency=0.8,
        mutation_rate=0.0,  # No mutations
        wild_type=0,
        seed=42
    )
    
    results_control = sim_control.run()
    print("Control simulation completed successfully")
    
    print("All tests passed!")
    
    # Plot results
    plot_results(results)

if __name__ == "__main__":
    test_mutation()
