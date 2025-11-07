"""
Comprehensive Graph Metrics Analyzer

Calculates and reports detailed network metrics for any NetworkX graph.
Supports both directed and undirected graphs with metrics including:
- Basic metrics (nodes, edges, density)
- Connectivity metrics (components, diameter, radius)
- Centrality metrics (degree, betweenness, closeness, eigenvector)
- Clustering metrics (coefficient, transitivity)
- Community metrics (modularity)
- Assortativity and reciprocity
- Path metrics (average shortest path)
"""

import networkx as nx
import json
import os
from datetime import datetime
from collections import defaultdict
import warnings


class GraphMetricsAnalyzer:
    """Comprehensive graph metrics analyzer for social networks."""
    
    def __init__(self, graph, graph_name="Network"):
        """
        Initialize analyzer with a NetworkX graph.
        
        Args:
            graph: NetworkX Graph or DiGraph
            graph_name: Name for the graph (used in reports)
        """
        self.G = graph
        self.graph_name = graph_name
        self.is_directed = graph.is_directed()
        self.metrics = {}
        
    def analyze_all(self, include_centrality=True, include_communities=True):
        """
        Run complete analysis of the graph.
        
        Args:
            include_centrality: Calculate centrality metrics (can be slow for large graphs)
            include_communities: Detect communities (can be slow for large graphs)
            
        Returns:
            Dictionary containing all computed metrics
        """
        print(f"\n{'='*70}")
        print(f"COMPREHENSIVE GRAPH METRICS ANALYSIS: {self.graph_name}")
        print(f"{'='*70}\n")
        
        self.metrics['graph_name'] = self.graph_name
        self.metrics['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.metrics['is_directed'] = self.is_directed
        
        # Run all analysis sections
        self._analyze_basic_properties()
        self._analyze_connectivity()
        self._analyze_degree_distribution()
        self._analyze_clustering()
        
        if include_centrality:
            self._analyze_centrality()
        
        if include_communities:
            self._analyze_communities()
        
        self._analyze_paths()
        self._analyze_assortativity()
        
        if self.is_directed:
            self._analyze_directed_properties()
        
        return self.metrics
    
    def _analyze_basic_properties(self):
        """Analyze basic graph properties."""
        print("[*] Basic Properties")
        print("-" * 70)
        
        n_nodes = self.G.number_of_nodes()
        n_edges = self.G.number_of_edges()
        density = nx.density(self.G)
        
        self.metrics['basic'] = {
            'num_nodes': n_nodes,
            'num_edges': n_edges,
            'density': density,
            'is_directed': self.is_directed
        }
        
        print(f"  Nodes: {n_nodes:,}")
        print(f"  Edges: {n_edges:,}")
        print(f"  Density: {density:.6f}")
        print(f"  Graph Type: {'Directed' if self.is_directed else 'Undirected'}")
        print()
    
    def _analyze_connectivity(self):
        """Analyze connectivity metrics."""
        print("[*] Connectivity Analysis")
        print("-" * 70)
        
        connectivity = {}
        
        if self.is_directed:
            # Weakly connected components
            weak_components = list(nx.weakly_connected_components(self.G))
            n_weak = len(weak_components)
            largest_weak = max(weak_components, key=len) if weak_components else set()
            
            # Strongly connected components
            strong_components = list(nx.strongly_connected_components(self.G))
            n_strong = len(strong_components)
            largest_strong = max(strong_components, key=len) if strong_components else set()
            
            connectivity['weakly_connected_components'] = n_weak
            connectivity['largest_wcc_size'] = len(largest_weak)
            connectivity['largest_wcc_fraction'] = len(largest_weak) / max(self.G.number_of_nodes(), 1)
            connectivity['strongly_connected_components'] = n_strong
            connectivity['largest_scc_size'] = len(largest_strong)
            connectivity['largest_scc_fraction'] = len(largest_strong) / max(self.G.number_of_nodes(), 1)
            
            print(f"  Weakly Connected Components: {n_weak}")
            print(f"    Largest WCC: {len(largest_weak)} nodes ({connectivity['largest_wcc_fraction']:.1%})")
            print(f"  Strongly Connected Components: {n_strong}")
            print(f"    Largest SCC: {len(largest_strong)} nodes ({connectivity['largest_scc_fraction']:.1%})")
            
            # Use largest SCC for diameter/radius if available
            self._largest_component = self.G.subgraph(largest_strong).copy() if largest_strong else None
        else:
            # Connected components for undirected graphs
            components = list(nx.connected_components(self.G))
            n_components = len(components)
            largest_comp = max(components, key=len) if components else set()
            
            connectivity['connected_components'] = n_components
            connectivity['largest_cc_size'] = len(largest_comp)
            connectivity['largest_cc_fraction'] = len(largest_comp) / max(self.G.number_of_nodes(), 1)
            connectivity['is_connected'] = n_components == 1
            
            print(f"  Connected Components: {n_components}")
            print(f"    Largest CC: {len(largest_comp)} nodes ({connectivity['largest_cc_fraction']:.1%})")
            print(f"  Is Connected: {connectivity['is_connected']}")
            
            self._largest_component = self.G.subgraph(largest_comp).copy() if largest_comp else None
        
        # Calculate diameter and radius on largest component
        if self._largest_component and self._largest_component.number_of_nodes() > 1:
            try:
                # For directed graphs, use the underlying undirected graph
                comp_for_diameter = self._largest_component.to_undirected() if self.is_directed else self._largest_component
                
                if nx.is_connected(comp_for_diameter):
                    diameter = nx.diameter(comp_for_diameter)
                    radius = nx.radius(comp_for_diameter)
                    connectivity['diameter'] = diameter
                    connectivity['radius'] = radius
                    print(f"  Diameter (largest component): {diameter}")
                    print(f"  Radius (largest component): {radius}")
                else:
                    connectivity['diameter'] = None
                    connectivity['radius'] = None
                    print(f"  Diameter: N/A (component not connected)")
            except Exception as e:
                connectivity['diameter'] = None
                connectivity['radius'] = None
                print(f"  Diameter/Radius: Could not calculate ({str(e)})")
        else:
            connectivity['diameter'] = None
            connectivity['radius'] = None
        
        self.metrics['connectivity'] = connectivity
        print()
    
    def _analyze_degree_distribution(self):
        """Analyze degree distribution."""
        print("[*] Degree Distribution")
        print("-" * 70)
        
        degree_dist = {}
        
        if self.is_directed:
            in_degrees = [d for n, d in self.G.in_degree()]
            out_degrees = [d for n, d in self.G.out_degree()]
            total_degrees = [self.G.in_degree(n) + self.G.out_degree(n) for n in self.G.nodes()]
            
            degree_dist['avg_in_degree'] = sum(in_degrees) / max(len(in_degrees), 1)
            degree_dist['avg_out_degree'] = sum(out_degrees) / max(len(out_degrees), 1)
            degree_dist['avg_total_degree'] = sum(total_degrees) / max(len(total_degrees), 1)
            degree_dist['max_in_degree'] = max(in_degrees) if in_degrees else 0
            degree_dist['max_out_degree'] = max(out_degrees) if out_degrees else 0
            degree_dist['max_total_degree'] = max(total_degrees) if total_degrees else 0
            degree_dist['min_in_degree'] = min(in_degrees) if in_degrees else 0
            degree_dist['min_out_degree'] = min(out_degrees) if out_degrees else 0
            degree_dist['min_total_degree'] = min(total_degrees) if total_degrees else 0
            
            print(f"  Average In-Degree: {degree_dist['avg_in_degree']:.2f}")
            print(f"  Average Out-Degree: {degree_dist['avg_out_degree']:.2f}")
            print(f"  Average Total Degree: {degree_dist['avg_total_degree']:.2f}")
            print(f"  Max In-Degree: {degree_dist['max_in_degree']}")
            print(f"  Max Out-Degree: {degree_dist['max_out_degree']}")
            print(f"  Min Total Degree: {degree_dist['min_total_degree']}")
        else:
            degrees = [d for n, d in self.G.degree()]
            
            degree_dist['avg_degree'] = sum(degrees) / max(len(degrees), 1)
            degree_dist['max_degree'] = max(degrees) if degrees else 0
            degree_dist['min_degree'] = min(degrees) if degrees else 0
            
            print(f"  Average Degree: {degree_dist['avg_degree']:.2f}")
            print(f"  Max Degree: {degree_dist['max_degree']}")
            print(f"  Min Degree: {degree_dist['min_degree']}")
        
        self.metrics['degree_distribution'] = degree_dist
        print()
    
    def _analyze_clustering(self):
        """Analyze clustering metrics."""
        print("[*] Clustering Analysis")
        print("-" * 70)
        
        clustering = {}
        
        try:
            # Average clustering coefficient
            if self.is_directed:
                # For directed graphs, convert to undirected
                G_undirected = self.G.to_undirected()
                avg_clustering = nx.average_clustering(G_undirected)
            else:
                avg_clustering = nx.average_clustering(self.G)
            
            clustering['average_clustering_coefficient'] = avg_clustering
            print(f"  Average Clustering Coefficient: {avg_clustering:.4f}")
        except Exception as e:
            clustering['average_clustering_coefficient'] = None
            print(f"  Average Clustering Coefficient: Could not calculate")
        
        try:
            # Transitivity (global clustering coefficient)
            if self.is_directed:
                transitivity = nx.transitivity(self.G.to_undirected())
            else:
                transitivity = nx.transitivity(self.G)
            
            clustering['transitivity'] = transitivity
            print(f"  Transitivity (Global Clustering): {transitivity:.4f}")
        except Exception as e:
            clustering['transitivity'] = None
            print(f"  Transitivity: Could not calculate")
        
        self.metrics['clustering'] = clustering
        print()
    
    def _analyze_centrality(self):
        """Analyze centrality metrics."""
        print("[*] Centrality Analysis")
        print("-" * 70)
        print("  (This may take a while for large graphs...)")
        
        centrality = {}
        
        try:
            # Degree centrality
            degree_cent = nx.degree_centrality(self.G)
            centrality['avg_degree_centrality'] = sum(degree_cent.values()) / max(len(degree_cent), 1)
            centrality['max_degree_centrality'] = max(degree_cent.values()) if degree_cent else 0
            print(f"  Average Degree Centrality: {centrality['avg_degree_centrality']:.4f}")
        except Exception as e:
            print(f"  Degree Centrality: Could not calculate")
        
        try:
            # Betweenness centrality (can be slow)
            betweenness = nx.betweenness_centrality(self.G)
            centrality['avg_betweenness_centrality'] = sum(betweenness.values()) / max(len(betweenness), 1)
            centrality['max_betweenness_centrality'] = max(betweenness.values()) if betweenness else 0
            print(f"  Average Betweenness Centrality: {centrality['avg_betweenness_centrality']:.4f}")
        except Exception as e:
            print(f"  Betweenness Centrality: Could not calculate (graph may be too large)")
        
        try:
            # Closeness centrality
            closeness = nx.closeness_centrality(self.G)
            centrality['avg_closeness_centrality'] = sum(closeness.values()) / max(len(closeness), 1)
            centrality['max_closeness_centrality'] = max(closeness.values()) if closeness else 0
            print(f"  Average Closeness Centrality: {centrality['avg_closeness_centrality']:.4f}")
        except Exception as e:
            print(f"  Closeness Centrality: Could not calculate")
        
        try:
            # Eigenvector centrality (may not converge for all graphs)
            if not self.is_directed:
                eigenvector = nx.eigenvector_centrality(self.G, max_iter=100)
                centrality['avg_eigenvector_centrality'] = sum(eigenvector.values()) / max(len(eigenvector), 1)
                centrality['max_eigenvector_centrality'] = max(eigenvector.values()) if eigenvector else 0
                print(f"  Average Eigenvector Centrality: {centrality['avg_eigenvector_centrality']:.4f}")
        except Exception as e:
            print(f"  Eigenvector Centrality: Could not calculate")
        
        self.metrics['centrality'] = centrality
        print()
    
    def _analyze_communities(self):
        """Detect and analyze communities."""
        print("[*] Community Detection")
        print("-" * 70)
        
        communities_info = {}
        
        try:
            # Use greedy modularity for community detection
            if self.is_directed:
                G_undirected = self.G.to_undirected()
            else:
                G_undirected = self.G
            
            communities = nx.community.greedy_modularity_communities(G_undirected)
            n_communities = len(communities)
            
            # Calculate modularity
            modularity = nx.community.modularity(G_undirected, communities)
            
            # Community sizes
            community_sizes = [len(c) for c in communities]
            largest_community = max(community_sizes) if community_sizes else 0
            smallest_community = min(community_sizes) if community_sizes else 0
            avg_community_size = sum(community_sizes) / max(len(community_sizes), 1)
            
            communities_info['num_communities'] = n_communities
            communities_info['modularity'] = modularity
            communities_info['largest_community_size'] = largest_community
            communities_info['smallest_community_size'] = smallest_community
            communities_info['avg_community_size'] = avg_community_size
            communities_info['community_sizes'] = community_sizes
            
            print(f"  Number of Communities: {n_communities}")
            print(f"  Modularity: {modularity:.4f}")
            print(f"  Largest Community: {largest_community} nodes")
            print(f"  Smallest Community: {smallest_community} nodes")
            print(f"  Average Community Size: {avg_community_size:.1f} nodes")
            
        except Exception as e:
            print(f"  Community Detection: Could not calculate ({str(e)})")
        
        self.metrics['communities'] = communities_info
        print()
    
    def _analyze_paths(self):
        """Analyze path-related metrics."""
        print("[*] Path Analysis")
        print("-" * 70)
        
        paths = {}
        
        # Use largest connected component for path analysis
        if self._largest_component and self._largest_component.number_of_nodes() > 1:
            try:
                comp_for_paths = self._largest_component.to_undirected() if self.is_directed else self._largest_component
                
                if nx.is_connected(comp_for_paths):
                    avg_shortest_path = nx.average_shortest_path_length(comp_for_paths)
                    paths['avg_shortest_path_length'] = avg_shortest_path
                    print(f"  Average Shortest Path Length: {avg_shortest_path:.4f}")
                else:
                    paths['avg_shortest_path_length'] = None
                    print(f"  Average Shortest Path Length: N/A (graph not fully connected)")
            except Exception as e:
                paths['avg_shortest_path_length'] = None
                print(f"  Average Shortest Path Length: Could not calculate")
        else:
            paths['avg_shortest_path_length'] = None
            print(f"  Average Shortest Path Length: N/A (insufficient nodes)")
        
        self.metrics['paths'] = paths
        print()
    
    def _analyze_assortativity(self):
        """Analyze assortativity (degree correlation)."""
        print("[*] Assortativity Analysis")
        print("-" * 70)
        
        assortativity_info = {}
        
        try:
            # Degree assortativity coefficient
            assortativity = nx.degree_assortativity_coefficient(self.G)
            assortativity_info['degree_assortativity'] = assortativity
            
            if assortativity > 0:
                interpretation = "Assortative (high-degree nodes connect to high-degree nodes)"
            elif assortativity < 0:
                interpretation = "Disassortative (high-degree nodes connect to low-degree nodes)"
            else:
                interpretation = "Neutral (no degree correlation)"
            
            print(f"  Degree Assortativity: {assortativity:.4f}")
            print(f"    -> {interpretation}")
        except Exception as e:
            assortativity_info['degree_assortativity'] = None
            print(f"  Degree Assortativity: Could not calculate")
        
        self.metrics['assortativity'] = assortativity_info
        print()
    
    def _analyze_directed_properties(self):
        """Analyze properties specific to directed graphs."""
        print("[*] Directed Graph Properties")
        print("-" * 70)
        
        directed_props = {}
        
        try:
            # Reciprocity - fraction of edges that are bidirectional
            reciprocity = nx.reciprocity(self.G)
            directed_props['reciprocity'] = reciprocity
            print(f"  Reciprocity: {reciprocity:.4f}")
            print(f"    -> {reciprocity:.1%} of edges are reciprocated")
        except Exception as e:
            directed_props['reciprocity'] = None
            print(f"  Reciprocity: Could not calculate")
        
        self.metrics['directed_properties'] = directed_props
        print()
    
    def print_summary(self):
        """Print a formatted summary of all metrics."""
        print("\n" + "="*70)
        print("METRICS SUMMARY")
        print("="*70 + "\n")
        
        # Print in organized sections
        for section, data in self.metrics.items():
            if section in ['graph_name', 'timestamp', 'is_directed']:
                continue
            
            print(f"{section.upper().replace('_', ' ')}:")
            if isinstance(data, dict):
                for key, value in data.items():
                    if isinstance(value, float):
                        print(f"  {key}: {value:.4f}")
                    elif isinstance(value, list):
                        print(f"  {key}: {value[:5]}..." if len(value) > 5 else f"  {key}: {value}")
                    else:
                        print(f"  {key}: {value}")
            print()
    
    def save_to_json(self, filepath):
        """
        Save metrics to JSON file.
        
        Args:
            filepath: Path to save JSON file
        """
        # Convert any non-serializable objects
        serializable_metrics = json.loads(json.dumps(self.metrics, default=str))
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(serializable_metrics, f, indent=2)
        
        print(f"[OK] Metrics saved to: {filepath}")
    
    def save_to_txt(self, filepath):
        """
        Save metrics to human-readable text file.
        
        Args:
            filepath: Path to save text file
        """
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"COMPREHENSIVE GRAPH METRICS ANALYSIS\n")
            f.write(f"Graph: {self.graph_name}\n")
            f.write(f"Generated: {self.metrics.get('timestamp', 'N/A')}\n")
            f.write("="*70 + "\n\n")
            
            for section, data in self.metrics.items():
                if section in ['graph_name', 'timestamp']:
                    continue
                
                f.write(f"{section.upper().replace('_', ' ')}:\n")
                f.write("-"*70 + "\n")
                
                if isinstance(data, dict):
                    for key, value in data.items():
                        if isinstance(value, float):
                            f.write(f"  {key}: {value:.4f}\n")
                        elif isinstance(value, list) and len(value) > 10:
                            f.write(f"  {key}: [list of {len(value)} items]\n")
                        else:
                            f.write(f"  {key}: {value}\n")
                f.write("\n")
        
        print(f"[OK] Metrics report saved to: {filepath}")


def analyze_graph(graph, graph_name="Network", save_results=True, output_dir="results"):
    """
    Convenience function to analyze a graph and save results.
    
    Args:
        graph: NetworkX Graph or DiGraph
        graph_name: Name for the graph
        save_results: Whether to save results to files
        output_dir: Directory to save results
        
    Returns:
        Dictionary of computed metrics
    """
    analyzer = GraphMetricsAnalyzer(graph, graph_name)
    
    # Determine if graph is large (adjust centrality/community detection accordingly)
    is_large = graph.number_of_nodes() > 1000
    
    metrics = analyzer.analyze_all(
        include_centrality=not is_large,  # Skip for very large graphs
        include_communities=not is_large
    )
    
    if save_results:
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        json_path = os.path.join(output_dir, f"{graph_name}_metrics_{timestamp}.json")
        txt_path = os.path.join(output_dir, f"{graph_name}_metrics_{timestamp}.txt")
        
        analyzer.save_to_json(json_path)
        analyzer.save_to_txt(txt_path)
    
    return metrics


if __name__ == "__main__":
    # Example usage with a small test graph
    print("Creating sample graph for demonstration...")
    
    # Create a sample graph
    G = nx.karate_club_graph()
    
    # Analyze it
    metrics = analyze_graph(G, graph_name="Karate_Club", save_results=True)
    
    print("\n" + "="*70)
    print("Example complete! Check the 'results' folder for saved metrics.")
    print("="*70)
