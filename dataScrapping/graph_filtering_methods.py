"""
Test script for graph filtering strategies to create strongly connected networks.

This script demonstrates 4 different filtering approaches:
1. K-Core Decomposition
2. Degree Filtering
3. Largest Connected Component Extraction
4. Edge Weight/Strength Filtering

Each method is tested and compared with visualizations and statistics.
"""

import networkx as nx
import matplotlib.pyplot as plt
import json
import os
from datetime import datetime

# Try to import Reddit scraper functions, use synthetic data if unavailable
try:
    from reddit_scraper import get_reddit_data, build_interaction_network
    REDDIT_AVAILABLE = True
except ImportError as e:
    print(f"Reddit scraper not available ({e}). Will use synthetic test data.")
    REDDIT_AVAILABLE = False

# Import graph metrics analyzer
from graph_metrics_analyzer import GraphMetricsAnalyzer

# Set up results directory with timestamp
# NOTE: RESULTS_DIR will be set in the main function after subreddit is determined
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BASE_RESULTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'results')
RESULTS_DIR = None  # Will be set in test_all_filtering_methods()


# ===========================
# FILTERING FUNCTIONS
# ===========================

def get_k_core_subgraph(G, k=3):
    """
    Extract k-core subgraph where all nodes have degree >= k.
    
    Args:
        G: NetworkX DiGraph
        k: Minimum degree threshold
    
    Returns:
        Subgraph with nodes having degree >= k
    """
    print(f"\n  Applying k-core decomposition with k={k}")
    G_undirected = G.to_undirected()
    k_core = nx.k_core(G_undirected, k=k)
    # Return directed subgraph with only k-core nodes
    subgraph = G.subgraph(k_core.nodes()).copy()
    print(f"  Kept {subgraph.number_of_nodes()} nodes, {subgraph.number_of_edges()} edges")
    return subgraph


def filter_by_degree(G, min_in_degree=2, min_out_degree=2, min_total_degree=3):
    """
    Filter nodes by degree requirements.
    
    Args:
        G: NetworkX DiGraph
        min_in_degree: Minimum incoming edges
        min_out_degree: Minimum outgoing edges
        min_total_degree: Minimum total edges (in + out)
    
    Returns:
        Filtered subgraph
    """
    print(f"\n  Filtering by degree: in>={min_in_degree}, out>={min_out_degree}, total>={min_total_degree}")
    nodes_to_keep = []
    for node in G.nodes():
        in_deg = G.in_degree(node)
        out_deg = G.out_degree(node)
        total_deg = in_deg + out_deg
        
        if (in_deg >= min_in_degree and 
            out_deg >= min_out_degree and 
            total_deg >= min_total_degree):
            nodes_to_keep.append(node)
    
    subgraph = G.subgraph(nodes_to_keep).copy()
    print(f"  Kept {subgraph.number_of_nodes()} nodes, {subgraph.number_of_edges()} edges")
    return subgraph


def get_largest_component(G, component_type='weakly'):
    """
    Extract largest connected component.
    
    Args:
        G: NetworkX DiGraph
        component_type: 'weakly' or 'strongly'
    
    Returns:
        Largest connected component subgraph
    """
    print(f"\n  Extracting largest {component_type} connected component")
    
    if component_type == 'strongly':
        components = list(nx.strongly_connected_components(G))
    else:
        components = list(nx.weakly_connected_components(G))
    
    if not components:
        print("  No components found!")
        return G
    
    # Get largest component
    largest = max(components, key=len)
    subgraph = G.subgraph(largest).copy()
    
    print(f"  Total components: {len(components)}")
    print(f"  Largest component: {len(largest)} nodes")
    print(f"  Kept {subgraph.number_of_nodes()} nodes, {subgraph.number_of_edges()} edges")
    
    return subgraph


def filter_by_edge_strength(G, min_strength=2.0):
    """
    Remove edges below strength threshold.
    
    Args:
        G: NetworkX DiGraph
        min_strength: Minimum relationship_strength to keep
    
    Returns:
        Filtered graph with only strong edges
    """
    print(f"\n  Filtering edges with strength < {min_strength}")
    G_filtered = G.copy()
    edges_to_remove = []
    
    for u, v, data in G_filtered.edges(data=True):
        if data.get('relationship_strength', 0) < min_strength:
            edges_to_remove.append((u, v))
    
    print(f"  Removing {len(edges_to_remove)} weak edges")
    G_filtered.remove_edges_from(edges_to_remove)
    
    # Remove isolated nodes
    isolated = list(nx.isolates(G_filtered))
    if isolated:
        print(f"  Removing {len(isolated)} isolated nodes")
        G_filtered.remove_nodes_from(isolated)
    
    print(f"  Kept {G_filtered.number_of_nodes()} nodes, {G_filtered.number_of_edges()} edges")
    return G_filtered


def iterative_prune(G, min_degree=2, max_iterations=100):
    """
    Iteratively remove nodes with degree < min_degree.
    
    Args:
        G: NetworkX DiGraph
        min_degree: Minimum total degree to keep
        max_iterations: Max pruning iterations
    
    Returns:
        Pruned subgraph
    """
    print(f"\n  Iteratively pruning nodes with degree < {min_degree}")
    G_pruned = G.copy()
    
    for iteration in range(max_iterations):
        nodes_to_remove = []
        for node in G_pruned.nodes():
            total_degree = G_pruned.in_degree(node) + G_pruned.out_degree(node)
            if total_degree < min_degree:
                nodes_to_remove.append(node)
        
        if not nodes_to_remove:
            print(f"  Converged after {iteration} iterations")
            break
        
        G_pruned.remove_nodes_from(nodes_to_remove)
    
    print(f"  Kept {G_pruned.number_of_nodes()} nodes, {G_pruned.number_of_edges()} edges")
    return G_pruned


# ===========================
# ANALYSIS FUNCTIONS
# ===========================

def analyze_graph_connectivity(G, graph_name="Graph"):
    """
    Analyze connectivity metrics of a graph.
    
    Returns:
        Dictionary with connectivity statistics
    """
    stats = {
        'name': graph_name,
        'nodes': G.number_of_nodes(),
        'edges': G.number_of_edges(),
        'density': nx.density(G),
        'weakly_connected_components': nx.number_weakly_connected_components(G),
        'strongly_connected_components': nx.number_strongly_connected_components(G),
    }
    
    # Size of largest components
    weak_components = list(nx.weakly_connected_components(G))
    strong_components = list(nx.strongly_connected_components(G))
    
    if weak_components:
        stats['largest_weak_component_size'] = len(max(weak_components, key=len))
        stats['largest_weak_component_pct'] = (stats['largest_weak_component_size'] / stats['nodes']) * 100
    else:
        stats['largest_weak_component_size'] = 0
        stats['largest_weak_component_pct'] = 0
    
    if strong_components:
        stats['largest_strong_component_size'] = len(max(strong_components, key=len))
        stats['largest_strong_component_pct'] = (stats['largest_strong_component_size'] / stats['nodes']) * 100
    else:
        stats['largest_strong_component_size'] = 0
        stats['largest_strong_component_pct'] = 0
    
    # Degree statistics
    if stats['nodes'] > 0:
        in_degrees = [G.in_degree(n) for n in G.nodes()]
        out_degrees = [G.out_degree(n) for n in G.nodes()]
        total_degrees = [G.in_degree(n) + G.out_degree(n) for n in G.nodes()]
        
        stats['avg_in_degree'] = sum(in_degrees) / len(in_degrees)
        stats['avg_out_degree'] = sum(out_degrees) / len(out_degrees)
        stats['avg_total_degree'] = sum(total_degrees) / len(total_degrees)
        stats['min_total_degree'] = min(total_degrees)
        stats['max_total_degree'] = max(total_degrees)
    
    return stats


def print_graph_stats(stats):
    """Print graph statistics in a readable format."""
    print(f"\n{'='*60}")
    print(f"  {stats['name']}")
    print(f"{'='*60}")
    print(f"  Nodes: {stats['nodes']}")
    print(f"  Edges: {stats['edges']}")
    print(f"  Density: {stats['density']:.4f}")
    print(f"\n  Connectivity:")
    print(f"    Weakly Connected Components: {stats['weakly_connected_components']}")
    print(f"    Strongly Connected Components: {stats['strongly_connected_components']}")
    print(f"    Largest Weak Component: {stats['largest_weak_component_size']} nodes ({stats['largest_weak_component_pct']:.1f}%)")
    print(f"    Largest Strong Component: {stats['largest_strong_component_size']} nodes ({stats['largest_strong_component_pct']:.1f}%)")
    
    if stats['nodes'] > 0:
        print(f"\n  Degree Statistics:")
        print(f"    Average In-Degree: {stats['avg_in_degree']:.2f}")
        print(f"    Average Out-Degree: {stats['avg_out_degree']:.2f}")
        print(f"    Average Total Degree: {stats['avg_total_degree']:.2f}")
        print(f"    Min Total Degree: {stats['min_total_degree']}")
        print(f"    Max Total Degree: {stats['max_total_degree']}")
    print(f"{'='*60}\n")


def compare_graphs_table(all_stats):
    """Print comparison table of all filtering methods."""
    print("\n" + "="*100)
    print("COMPARISON TABLE: All Filtering Methods")
    print("="*100)
    
    # Headers
    print(f"{'Method':<30} {'Nodes':<10} {'Edges':<10} {'Density':<10} {'Weak CC':<10} {'Strong CC':<10}")
    print("-"*100)
    
    # Data rows
    for stats in all_stats:
        print(f"{stats['name']:<30} {stats['nodes']:<10} {stats['edges']:<10} "
              f"{stats['density']:<10.4f} {stats['weakly_connected_components']:<10} "
              f"{stats['strongly_connected_components']:<10}")
    
    print("="*100)
    
    # Recommendations
    print("\nRECOMMENDATIONS:")
    print("-" * 100)
    
    # Find best method for strong connectivity
    best_strong = max(all_stats[1:], key=lambda x: x['largest_strong_component_pct'])  # Skip original
    print(f"  Best for Strong Connectivity: {best_strong['name']}")
    print(f"    -> {best_strong['largest_strong_component_size']} nodes in largest strongly connected component "
          f"({best_strong['largest_strong_component_pct']:.1f}%)")
    
    # Find best method for preserving size
    best_size = max(all_stats[1:], key=lambda x: x['nodes'])
    print(f"\n  Best for Preserving Graph Size: {best_size['name']}")
    print(f"    -> Retains {best_size['nodes']} nodes ({(best_size['nodes']/all_stats[0]['nodes'])*100:.1f}% of original)")
    
    # Find best density
    best_density = max(all_stats[1:], key=lambda x: x['density'])
    print(f"\n  Best for Graph Density: {best_density['name']}")
    print(f"    -> Density: {best_density['density']:.4f}")
    
    print("="*100 + "\n")


def visualize_degree_distributions(graphs_dict):
    """
    Visualize degree distributions for all graph variations.
    
    Args:
        graphs_dict: Dictionary mapping graph names to NetworkX graphs
    """
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    axes = axes.flatten()
    
    for idx, (name, G) in enumerate(graphs_dict.items()):
        if idx >= 6:
            break
        
        ax = axes[idx]
        
        if G.number_of_nodes() == 0:
            ax.text(0.5, 0.5, 'No nodes', ha='center', va='center')
            ax.set_title(name)
            continue
        
        # Calculate degree distributions
        in_degrees = [G.in_degree(n) for n in G.nodes()]
        out_degrees = [G.out_degree(n) for n in G.nodes()]
        total_degrees = [G.in_degree(n) + G.out_degree(n) for n in G.nodes()]
        
        # Plot histogram
        ax.hist([in_degrees, out_degrees, total_degrees], 
                bins=20, alpha=0.6, label=['In-Degree', 'Out-Degree', 'Total'])
        ax.set_xlabel('Degree')
        ax.set_ylabel('Number of Nodes')
        ax.set_title(f'{name}\n({G.number_of_nodes()} nodes, {G.number_of_edges()} edges)')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    # Hide unused subplots
    for idx in range(len(graphs_dict), 6):
        axes[idx].axis('off')
    
    plt.tight_layout()
    filename = os.path.join(RESULTS_DIR, f"graph_filtering_degree_distributions.png")
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    print(f"\nSaved degree distribution plot: {filename}")
    plt.close()


def visualize_network_comparison(graphs_dict, max_graphs=4):
    """
    Visualize multiple graphs side by side for comparison.
    
    Args:
        graphs_dict: Dictionary mapping graph names to NetworkX graphs
        max_graphs: Maximum number of graphs to visualize
    """
    # Limit number of graphs to visualize
    graph_items = list(graphs_dict.items())[:max_graphs]
    
    fig, axes = plt.subplots(1, len(graph_items), figsize=(6*len(graph_items), 6))
    
    if len(graph_items) == 1:
        axes = [axes]
    
    for idx, (name, G) in enumerate(graph_items):
        ax = axes[idx]
        
        if G.number_of_nodes() == 0:
            ax.text(0.5, 0.5, 'No nodes', ha='center', va='center', fontsize=16)
            ax.set_title(name, fontsize=12, fontweight='bold')
            ax.axis('off')
            continue
        
        # Limit visualization for very large graphs
        if G.number_of_nodes() > 100:
            # Sample largest degree nodes
            degrees = dict(G.degree())
            top_nodes = sorted(degrees, key=degrees.get, reverse=True)[:100]
            G_vis = G.subgraph(top_nodes)
            title_suffix = f"\n(showing top 100/{G.number_of_nodes()} nodes)"
        else:
            G_vis = G
            title_suffix = ""
        
        # Use spring layout
        pos = nx.spring_layout(G_vis, k=0.5, iterations=50, seed=42)
        
        # Draw network
        node_sizes = [30 + 10 * (G_vis.in_degree(n) + G_vis.out_degree(n)) for n in G_vis.nodes()]
        
        nx.draw_networkx_nodes(G_vis, pos, node_size=node_sizes, 
                              node_color='lightblue', alpha=0.7, ax=ax)
        nx.draw_networkx_edges(G_vis, pos, alpha=0.3, width=0.5, 
                              arrows=True, arrowsize=5, ax=ax)
        
        ax.set_title(f'{name}{title_suffix}\n{G.number_of_nodes()} nodes, {G.number_of_edges()} edges',
                    fontsize=12, fontweight='bold')
        ax.axis('off')
    
    plt.tight_layout()
    filename = os.path.join(RESULTS_DIR, f"graph_filtering_network_viz.png")
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    print(f"Saved network visualization: {filename}")
    plt.close()


# ===========================
# MAIN TEST SCRIPT
# ===========================

def test_all_filtering_methods():
    """
    Test all four filtering methods and compare results.
    """
    print("\n" + "="*60)
    print("GRAPH FILTERING TEST SCRIPT")
    print("="*60)
    print("\nThis script will:")
    print("  1. Fetch Reddit data and build interaction network")
    print("  2. Apply 4 different filtering strategies")
    print("  3. Analyze and compare connectivity metrics")
    print("  4. Generate visualizations")
    print("\n" + "="*60 + "\n")
    
    # Step 1: Get Reddit data
    print("STEP 1: Fetching Reddit data...")
    print("-" * 60)
    
    # You can customize these parameters - allow override from environment variable
    subreddit = os.environ.get('ANALYSIS_SUBREDDIT', 'assistance')  # Change to your target subreddit
    num_posts = 300         # Number of posts to fetch
    
    # Set up results directory with subreddit name
    global RESULTS_DIR
    RESULTS_DIR = os.path.join(BASE_RESULTS_DIR, f"graph_filtering_{subreddit}_{TIMESTAMP}")
    os.makedirs(RESULTS_DIR, exist_ok=True)
    
    print(f"Analyzing subreddit: r/{subreddit}")
    print(f"Results will be saved to: {RESULTS_DIR}\n")
    if REDDIT_AVAILABLE:
        try:
            posts = get_reddit_data(
                subreddit_name=subreddit,
                num_posts=num_posts,
                sort_by='comments',
                time_filter='all',
                verbose=True,
                include_comments=True,
                max_comment_depth=10,
                use_cache=True,  # Use cached data if available
                force_refresh=False  # Set to True to force re-scraping
            )
            print(f"\nSuccessfully fetched {len(posts)} posts")
        except Exception as e:
            print(f"Error fetching Reddit data: {e}")
            print("\nUsing synthetic test data instead...")
            posts = None
    else:
        print("Reddit scraper not available. Using synthetic test data...")
        posts = None
    
    # Step 2: Build network
    print("\n" + "="*60)
    print("STEP 2: Building interaction network...")
    print("-" * 60)
    
    if posts and REDDIT_AVAILABLE:
        network_data = build_interaction_network(posts)
        G_original = network_data['graph']
    else:
        # Create synthetic test graph
        G_original = create_synthetic_test_graph()
    
    print(f"\nOriginal network created:")
    print(f"  Nodes: {G_original.number_of_nodes()}")
    print(f"  Edges: {G_original.number_of_edges()}")
    
    # Step 3: Apply filtering methods
    print("\n" + "="*60)
    print("STEP 3: Applying filtering methods...")
    print("="*60)
    
    graphs = {'Original': G_original}
    all_stats = []
    
    # Analyze original
    print("\n[METHOD 0: Original Graph]")
    stats_original = analyze_graph_connectivity(G_original, "Original Graph")
    print_graph_stats(stats_original)
    all_stats.append(stats_original)
    
    # Method 1: K-Core Decomposition
    print("\n[METHOD 1: K-Core Decomposition]")
    print("-" * 60)
    for k in [2, 3]:
        try:
            G_kcore = get_k_core_subgraph(G_original, k=k)
            graph_name = f"K-Core (k={k})"
            graphs[graph_name] = G_kcore
            stats = analyze_graph_connectivity(G_kcore, graph_name)
            print_graph_stats(stats)
            all_stats.append(stats)
        except Exception as e:
            print(f"  Error with k={k}: {e}")
    
    # Method 2: Degree Filtering
    print("\n[METHOD 2: Degree Filtering]")
    print("-" * 60)
    try:
        G_degree = filter_by_degree(G_original, min_in_degree=1, min_out_degree=1, min_total_degree=3)
        graph_name = "Degree Filter (total>=3)"
        graphs[graph_name] = G_degree
        stats = analyze_graph_connectivity(G_degree, graph_name)
        print_graph_stats(stats)
        all_stats.append(stats)
    except Exception as e:
        print(f"  Error: {e}")
    
    # Method 3: Largest Connected Component
    print("\n[METHOD 3: Largest Connected Component]")
    print("-" * 60)
    for comp_type in ['weakly', 'strongly']:
        try:
            G_component = get_largest_component(G_original, component_type=comp_type)
            graph_name = f"Largest {comp_type.capitalize()} Component"
            graphs[graph_name] = G_component
            stats = analyze_graph_connectivity(G_component, graph_name)
            print_graph_stats(stats)
            all_stats.append(stats)
        except Exception as e:
            print(f"  Error with {comp_type}: {e}")
    
    # Method 4: Edge Strength Filtering
    print("\n[METHOD 4: Edge Strength Filtering]")
    print("-" * 60)
    for min_strength in [1.5, 2.0]:
        try:
            G_strength = filter_by_edge_strength(G_original, min_strength=min_strength)
            graph_name = f"Edge Strength >={min_strength}"
            graphs[graph_name] = G_strength
            stats = analyze_graph_connectivity(G_strength, graph_name)
            print_graph_stats(stats)
            all_stats.append(stats)
        except Exception as e:
            print(f"  Error with strength={min_strength}: {e}")
    
    # Step 4: Comparison
    print("\n" + "="*60)
    print("STEP 4: Comparison & Analysis")
    print("="*60)
    compare_graphs_table(all_stats)
    
    # Step 4b: Detailed metrics analysis for selected graphs
    print("\n" + "="*60)
    print("STEP 4b: Detailed Metrics Analysis")
    print("="*60)
    
    # Analyze original and best filtered graphs
    graphs_to_analyze = {
        'Original': G_original,
    }
    
    # Add the most strongly connected filtered graph
    if len(all_stats) > 1:
        best_filtered = max(all_stats[1:], key=lambda x: x.get('largest_strong_component_pct', 0))
        best_filtered_name = best_filtered['name']
        if best_filtered_name in graphs:
            graphs_to_analyze[best_filtered_name] = graphs[best_filtered_name]
    
    for graph_name, graph in graphs_to_analyze.items():
        if graph.number_of_nodes() > 0:
            print(f"\n--- Analyzing: {graph_name} ---")
            analyzer = GraphMetricsAnalyzer(graph, graph_name)
            is_large = graph.number_of_nodes() > 500
            metrics = analyzer.analyze_all(
                include_centrality=not is_large,
                include_communities=not is_large
            )
            
            # Save detailed metrics
            metrics_file = os.path.join(RESULTS_DIR, f"{graph_name.replace(' ', '_')}_detailed_metrics.json")
            analyzer.save_to_json(metrics_file)
            metrics_txt_file = os.path.join(RESULTS_DIR, f"{graph_name.replace(' ', '_')}_detailed_metrics.txt")
            analyzer.save_to_txt(metrics_txt_file)
    
    # Step 5: Visualizations
    print("\n" + "="*60)
    print("STEP 5: Generating visualizations...")
    print("="*60)
    
    try:
        visualize_degree_distributions(graphs)
        visualize_network_comparison(graphs, max_graphs=4)
        print("\nVisualizations complete!")
    except Exception as e:
        print(f"Error generating visualizations: {e}")
    
    # Step 6: Save results
    print("\n" + "="*60)
    print("STEP 6: Saving results...")
    print("="*60)
    
    # Save metadata
    metadata = {
        'timestamp': TIMESTAMP,
        'subreddit': subreddit,
        'num_posts': num_posts,
        'original_nodes': G_original.number_of_nodes(),
        'original_edges': G_original.number_of_edges(),
        'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    metadata_file = os.path.join(RESULTS_DIR, 'analysis_metadata.json')
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)
    print(f"Saved metadata to: {metadata_file}")
    
    # Save results
    results_file = os.path.join(RESULTS_DIR, f"graph_filtering_results.json")
    
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(all_stats, f, indent=2)
    
    print(f"Saved detailed results to: {results_file}")
    
    print("\n" + "="*60)
    print("TEST COMPLETE!")
    print("="*60)
    print("\nFiles generated in timestamped results folder:")
    print(f"  - analysis_metadata.json (subreddit: {subreddit})")
    print(f"  - graph_filtering_results.json")
    print(f"  - graph_filtering_degree_distributions.png")
    print(f"  - graph_filtering_network_viz.png")
    print(f"  - *_detailed_metrics.json (comprehensive metrics)")
    print(f"\nResults directory: {RESULTS_DIR}")
    print("="*60 + "\n")
    print(f"  - *_detailed_metrics.txt (human-readable metrics)")
    print(f"\nResults directory: {RESULTS_DIR}")
    print("\n" + "="*60 + "\n")
    
    return graphs, all_stats


def create_synthetic_test_graph():
    """
    Create a synthetic test graph for testing when Reddit API is unavailable.
    """
    print("\nCreating synthetic test graph...")
    G = nx.DiGraph()
    
    # Core group (well connected)
    core_users = [f"user_{i}" for i in range(1, 21)]
    for i, user in enumerate(core_users):
        G.add_node(user)
        # Each user replies to 3-5 others
        for j in range(3, 6):
            target = core_users[(i + j) % len(core_users)]
            if user != target:
                G.add_edge(user, target, weight=2, relationship_strength=2.5)
    
    # Peripheral users (weakly connected - sources)
    for i in range(21, 31):
        user = f"peripheral_{i}"
        G.add_node(user)
        # Only 1-2 outgoing edges
        target = core_users[i % len(core_users)]
        G.add_edge(user, target, weight=1, relationship_strength=1.0)
    
    # Lurkers (sinks - only incoming)
    for i in range(31, 41):
        user = f"lurker_{i}"
        G.add_node(user)
        # Only 1 incoming edge
        source = core_users[i % len(core_users)]
        G.add_edge(source, user, weight=1, relationship_strength=0.8)
    
    print(f"Synthetic graph created: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    return G


# ===========================
# RUN TESTS
# ===========================

if __name__ == "__main__":
    try:
        graphs, stats = test_all_filtering_methods()
        print("\n[OK] All tests completed successfully!\n")
    except Exception as e:
        print(f"\n[ERROR] Error during testing: {e}")
        import traceback
        traceback.print_exc()
