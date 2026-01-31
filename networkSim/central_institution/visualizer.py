import matplotlib.pyplot as plt
import numpy as np
from typing import List, Dict

class SimulationVisualizer:
    """Visualize simulation results over time."""
    
    @staticmethod
    def plot_metrics_over_time(metrics_history: List[Dict], new_connections_history: List[int],
                               save_path: str = None) -> None:
        """
        Plot all key metrics over simulation iterations.
        
        Args:
            metrics_history: List of metric dicts from each iteration
            new_connections_history: List of new connections per iteration
            save_path: Optional path to save figure
        """
        if not metrics_history:
            print("No metrics to plot")
            return
        
        iterations = np.arange(len(metrics_history))
        
        # Extract metrics
        connected_components = [m['connected_components'] for m in metrics_history]
        clustering = [m['clustering_coefficient'] for m in metrics_history]
        density = [m['network_density'] for m in metrics_history]
        degree_gini = [m['degree_gini'] for m in metrics_history]
        avg_path = [m['average_shortest_path'] if m['average_shortest_path'] is not None else np.nan 
                    for m in metrics_history]
        
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        fig.suptitle('Central Institution Network Evolution Over Time', fontsize=16, fontweight='bold')
        
        # Plot 1: Connected Components
        ax = axes[0, 0]
        ax.plot(iterations, connected_components, 'b-', linewidth=2, marker='o', markersize=3)
        ax.set_xlabel('Iteration')
        ax.set_ylabel('Number of Components')
        ax.set_title('Connected Components\n(↓ Better - Network Fragmentation)')
        ax.grid(True, alpha=0.3)
        ax.set_ylim(bottom=0.5)
        
        # Plot 2: Clustering Coefficient
        ax = axes[0, 1]
        ax.plot(iterations, clustering, 'g-', linewidth=2, marker='o', markersize=3)
        ax.set_xlabel('Iteration')
        ax.set_ylabel('Clustering Coefficient')
        ax.set_title('Clustering Coefficient\n(↑ Better - Community Formation)')
        ax.grid(True, alpha=0.3)
        ax.set_ylim([0, 1])
        
        # Plot 3: Network Density
        ax = axes[0, 2]
        ax.plot(iterations, density, 'r-', linewidth=2, marker='o', markersize=3)
        ax.set_xlabel('Iteration')
        ax.set_ylabel('Density')
        ax.set_title('Network Density\n(↑ More Connected)')
        ax.grid(True, alpha=0.3)
        ax.set_ylim([0, 1])
        
        # Plot 4: Degree Gini Coefficient
        ax = axes[1, 0]
        ax.plot(iterations, degree_gini, 'purple', linewidth=2, marker='o', markersize=3)
        ax.set_xlabel('Iteration')
        ax.set_ylabel('Gini Coefficient')
        ax.set_title('Degree Distribution Gini\n(↓ Better - Power Decentralization)')
        ax.grid(True, alpha=0.3)
        ax.set_ylim([0, 1])
        
        # Plot 5: Average Shortest Path
        ax = axes[1, 1]
        ax.plot(iterations, avg_path, 'orange', linewidth=2, marker='o', markersize=3)
        ax.set_xlabel('Iteration')
        ax.set_ylabel('Avg Shortest Path')
        ax.set_title('Average Shortest Path Length\n(↓ Better - Efficiency)')
        ax.grid(True, alpha=0.3)
        
        # Plot 6: New Connections per Iteration
        ax = axes[1, 2]
        ax.bar(iterations, new_connections_history, color='teal', alpha=0.7)
        ax.set_xlabel('Iteration')
        ax.set_ylabel('New Connections')
        ax.set_title('New Peer Connections per Iteration')
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Figure saved to {save_path}")
        else:
            plt.show()
    
    @staticmethod
    def plot_degree_evolution(metrics_history: List[Dict], num_nodes: int,
                              save_path: str = None) -> None:
        """
        Plot evolution of degree distribution.
        
        Args:
            metrics_history: List of metric dicts from each iteration
            num_nodes: Number of peripheral nodes
            save_path: Optional path to save figure
        """
        if not metrics_history:
            return
        
        # Sample at key points: start, middle, end
        indices = [0, len(metrics_history)//2, len(metrics_history)-1]
        
        fig, axes = plt.subplots(1, 3, figsize=(15, 4))
        fig.suptitle('Degree Distribution Evolution', fontsize=14, fontweight='bold')
        
        for i, idx in enumerate(indices):
            ax = axes[i]
            degree_dist = metrics_history[idx]['degree_distribution']
            
            # Extract peripheral node degrees (exclude HUB)
            node_degrees = [d for n, d in degree_dist.items() if n != 'HUB']
            
            ax.hist(node_degrees, bins=range(0, num_nodes+1), alpha=0.7, color='steelblue', edgecolor='black')
            ax.set_xlabel('Node Degree (peer connections + hub)')
            ax.set_ylabel('Frequency')
            ax.set_title(f'Iteration {idx}\n(Gini: {metrics_history[idx]["degree_gini"]:.3f})')
            ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Figure saved to {save_path}")
        else:
            plt.show()
