import numpy as np
from typing import Dict, List, Tuple
from network import CentralInstitutionNetwork
from metrics import NetworkMetrics
import json
from datetime import datetime

class CentralInstitutionSimulation:
    """Main simulation engine for central institution experiment."""
    
    def __init__(self, num_nodes: int, num_iterations: int, tokens_per_iteration: int,
                 token_threshold: int, connection_prob_base: float, connection_prob_max: float,
                 accumulation_rate: float, seed: int = 42):
        """
        Initialize simulation.
        
        Args:
            num_nodes: Number of peripheral nodes
            num_iterations: Number of iterations to run
            tokens_per_iteration: Tokens distributed per iteration
            token_threshold: Tokens needed for connection probability
            connection_prob_base: Base connection probability
            connection_prob_max: Maximum connection probability
            accumulation_rate: Token accumulation rate
            seed: Random seed
        """
        self.num_nodes = num_nodes
        self.num_iterations = num_iterations
        self.tokens_per_iteration = tokens_per_iteration
        self.seed = seed
        
        self.network = CentralInstitutionNetwork(
            num_nodes=num_nodes,
            token_threshold=token_threshold,
            connection_prob_base=connection_prob_base,
            connection_prob_max=connection_prob_max,
            accumulation_rate=accumulation_rate,
            seed=seed
        )
        
        # Store metrics over time
        self.metrics_history: List[Dict] = []
        self.new_connections_history: List[int] = []
        
    def run_iteration(self) -> Tuple[Dict, int]:
        """
        Run one iteration of the simulation.
        
        Returns:
            Tuple of (metrics dict, number of new peer connections)
        """
        # Central institution distributes tokens
        self.network.distribute_tokens(self.tokens_per_iteration)
        
        # Nodes attempt to form peer connections
        new_connections = self.network.attempt_peer_connections()
        
        # Calculate metrics
        graph = self.network.get_graph_copy()
        metrics = NetworkMetrics.get_all_metrics(graph)
        
        return metrics, new_connections
    
    def run(self) -> None:
        """Run full simulation for all iterations."""
        print(f"Starting simulation: {self.num_nodes} nodes, {self.num_iterations} iterations")
        print(f"Tokens per iteration: {self.tokens_per_iteration}\n")
        
        for iteration in range(self.num_iterations):
            metrics, new_connections = self.run_iteration()
            self.metrics_history.append(metrics)
            self.new_connections_history.append(new_connections)
            
            if (iteration + 1) % 10 == 0:
                print(f"Iteration {iteration + 1}/{self.num_iterations}")
                print(f"  Connected Components: {metrics['connected_components']}")
                print(f"  Clustering Coefficient: {metrics['clustering_coefficient']:.4f}")
                print(f"  Network Density: {metrics['network_density']:.4f}")
                print(f"  Degree Gini: {metrics['degree_gini']:.4f}")
                print(f"  New Peer Connections: {new_connections}")
                if metrics['average_shortest_path'] is not None:
                    print(f"  Avg Shortest Path: {metrics['average_shortest_path']:.4f}")
                print()
        
        print("Simulation complete!")
    
    def get_results_summary(self) -> Dict:
        """Generate summary of results."""
        if not self.metrics_history:
            return {}
        
        final_metrics = self.metrics_history[-1]
        initial_metrics = self.metrics_history[0]
        total_new_connections = sum(self.new_connections_history)
        
        summary = {
            'simulation_params': {
                'num_nodes': self.num_nodes,
                'num_iterations': self.num_iterations,
                'tokens_per_iteration': self.tokens_per_iteration,
                'seed': self.seed,
            },
            'final_metrics': final_metrics,
            'initial_metrics': initial_metrics,
            'total_new_connections': total_new_connections,
            'metrics_history': self.metrics_history,
            'new_connections_history': self.new_connections_history,
            'timestamp': datetime.now().isoformat()
        }
        return summary
    
    def save_results(self, filepath: str) -> None:
        """Save results to JSON file."""
        summary = self.get_results_summary()
        # Convert numpy types for JSON serialization
        summary = self._convert_for_json(summary)
        
        with open(filepath, 'w') as f:
            json.dump(summary, f, indent=2)
        print(f"Results saved to {filepath}")
    
    @staticmethod
    def _convert_for_json(obj):
        """Recursively convert numpy types to Python types for JSON."""
        if isinstance(obj, dict):
            return {k: CentralInstitutionSimulation._convert_for_json(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [CentralInstitutionSimulation._convert_for_json(v) for v in obj]
        elif isinstance(obj, (np.integer, np.floating)):
            return float(obj)
        elif obj is None:
            return None
        return obj
