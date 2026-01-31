import networkx as nx
import numpy as np
from typing import Dict, Tuple, List

class NetworkMetrics:
    """Calculate connectivity metrics for the network."""
    
    @staticmethod
    def get_connected_components(graph: nx.Graph) -> int:
        """
        Get number of connected components.
        
        Ideal: 1 (whole network connected)
        Higher values indicate fragmentation.
        """
        return nx.number_connected_components(graph)
    
    @staticmethod
    def get_average_shortest_path(graph: nx.Graph) -> float:
        """
        Get average shortest path length (only for connected graphs).
        
        Measures network efficiency. Lower is better.
        If graph is disconnected, returns None.
        """
        if not nx.is_connected(graph):
            return None
        return nx.average_shortest_path_length(graph)
    
    @staticmethod
    def get_clustering_coefficient(graph: nx.Graph) -> float:
        """
        Get average clustering coefficient.
        
        Measures how clustered/triangular the network is.
        Range: 0-1. Higher indicates more tight-knit communities.
        """
        return nx.average_clustering(graph)
    
    @staticmethod
    def get_network_density(graph: nx.Graph) -> float:
        """
        Get network density (ratio of actual to possible edges).
        
        Range: 0-1. Shows how "filled in" the network is.
        """
        return nx.density(graph)
    
    @staticmethod
    def get_degree_distribution_gini(graph: nx.Graph) -> float:
        """
        Get Gini coefficient of degree distribution.
        
        Measures inequality in node connectivity.
        Range: 0-1. 
        - 0 = perfect equality (all nodes same degree)
        - 1 = perfect inequality (one node has all connections)
        
        Shows if power/influence is concentrating.
        """
        degrees = [d for n, d in graph.degree()]
        if len(degrees) < 2:
            return 0.0
        
        degrees_sorted = np.sort(degrees)
        n = len(degrees)
        cumsum = np.cumsum(degrees_sorted)
        
        # Gini coefficient formula
        gini = (2 * np.sum(np.arange(1, n + 1) * degrees_sorted)) / (n * np.sum(degrees_sorted)) - (n + 1) / n
        return max(0.0, gini)  # Ensure non-negative
    
    @staticmethod
    def get_degree_distribution(graph: nx.Graph) -> Dict[str, int]:
        """Get degree of each node."""
        return dict(graph.degree())
    
    @staticmethod
    def get_all_metrics(graph: nx.Graph) -> Dict:
        """
        Calculate all metrics for the network.
        
        Returns:
            Dictionary with all metric values
        """
        metrics = {
            'connected_components': NetworkMetrics.get_connected_components(graph),
            'average_shortest_path': NetworkMetrics.get_average_shortest_path(graph),
            'clustering_coefficient': NetworkMetrics.get_clustering_coefficient(graph),
            'network_density': NetworkMetrics.get_network_density(graph),
            'degree_gini': NetworkMetrics.get_degree_distribution_gini(graph),
            'degree_distribution': NetworkMetrics.get_degree_distribution(graph)
        }
        return metrics
