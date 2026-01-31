"""
Main entry point for Central Institution Network Experiment

This experiment models how peer connections emerge in a network that starts as a 
star topology (all nodes connected only to a central hub). As nodes receive tokens
from the hub and other nodes, they develop higher probability of connecting directly
with each other based on their interaction history.
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Import simulation and visualization components
from simulation import CentralInstitutionSimulation
from visualizer import SimulationVisualizer
import parameters as P


def main():
    """Run the central institution network simulation."""
    
    print("=" * 80)
    print("CENTRAL INSTITUTION NETWORK EXPERIMENT")
    print("=" * 80)
    print()
    print("CONFIGURATION:")
    print(f"  Number of Nodes: {P.NUM_NODES}")
    print(f"  Number of Iterations: {P.NUM_ITERATIONS}")
    print(f"  Tokens per Iteration: {P.TOKENS_PER_ITERATION}")
    print(f"  Token Threshold: {P.TOKEN_THRESHOLD}")
    print(f"  Base Connection Probability: {P.CONNECTION_PROBABILITY_BASE}")
    print(f"  Max Connection Probability: {P.CONNECTION_PROBABILITY_MAX}")
    print(f"  Token Accumulation Rate: {P.TOKEN_ACCUMULATION_RATE}")
    print(f"  Random Seed: {P.SEED}")
    print()
    
    # Create and run simulation
    sim = CentralInstitutionSimulation(
        num_nodes=P.NUM_NODES,
        num_iterations=P.NUM_ITERATIONS,
        tokens_per_iteration=P.TOKENS_PER_ITERATION,
        token_threshold=P.TOKEN_THRESHOLD,
        connection_prob_base=P.CONNECTION_PROBABILITY_BASE,
        connection_prob_max=P.CONNECTION_PROBABILITY_MAX,
        accumulation_rate=P.TOKEN_ACCUMULATION_RATE,
        seed=P.SEED
    )
    
    sim.run()
    print()
    
    # Print final summary
    summary = sim.get_results_summary()
    
    print("=" * 80)
    print("FINAL METRICS SUMMARY")
    print("=" * 80)
    print()
    print("Initial State:")
    initial = summary['initial_metrics']
    print(f"  Connected Components: {initial['connected_components']}")
    print(f"  Clustering Coefficient: {initial['clustering_coefficient']:.4f}")
    print(f"  Network Density: {initial['network_density']:.4f}")
    print(f"  Degree Gini (inequality): {initial['degree_gini']:.4f}")
    print()
    
    print("Final State:")
    final = summary['final_metrics']
    print(f"  Connected Components: {final['connected_components']}")
    print(f"  Clustering Coefficient: {final['clustering_coefficient']:.4f}")
    print(f"  Network Density: {final['network_density']:.4f}")
    print(f"  Degree Gini (inequality): {final['degree_gini']:.4f}")
    if final['average_shortest_path'] is not None:
        print(f"  Avg Shortest Path Length: {final['average_shortest_path']:.4f}")
    print()
    
    print("Overall Statistics:")
    print(f"  Total New Peer Connections: {summary['total_new_connections']}")
    print(f"  Average New Connections per Iteration: {summary['total_new_connections']/P.NUM_ITERATIONS:.2f}")
    print()
    
    # Save results
    if P.SAVE_RESULTS:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"central_institution_results_{timestamp}.json"
        sim.save_results(results_file)
        print(f"Results saved to: {results_file}")
        print()
    
    # Generate visualizations
    if P.PLOT_METRICS:
        print("Generating visualizations...")
        
        # Metrics over time
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        figure_1 = f"metrics_evolution_{timestamp}.png"
        SimulationVisualizer.plot_metrics_over_time(
            sim.metrics_history,
            sim.new_connections_history,
            save_path=figure_1
        )
        print(f"Saved: {figure_1}")
        
        # Degree distribution evolution
        figure_2 = f"degree_distribution_{timestamp}.png"
        SimulationVisualizer.plot_degree_evolution(
            sim.metrics_history,
            P.NUM_NODES,
            save_path=figure_2
        )
        print(f"Saved: {figure_2}")
    
    print()
    print("=" * 80)
    print("EXPERIMENT COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
