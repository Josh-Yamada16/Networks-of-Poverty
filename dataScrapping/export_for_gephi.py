"""
Gephi Export Module

Prepares network data for visualization in Gephi with:
- Nodes sized by helping activity (larger = more help given)
- Nodes colored by helper/seeker ratio
- Edge weights based on relationship strength
- Communities detected and labeled
"""

import reddit_scraper as rs
import networkx as nx
import csv
import json
from collections import defaultdict
import pickle
from graph_metrics_analyzer import GraphMetricsAnalyzer

def prepare_for_gephi(network_data, output_prefix, save_graphml=True, save_node_attrs=True, 
                      save_edge_attrs=True, save_community=True):
    """
    Enhance graph with visualization attributes and export for Gephi
    
    Args:
        network_data: Output from build_interaction_network()
        output_prefix: Prefix for output files
        save_graphml: Whether to save GraphML file for Gephi
        save_node_attrs: Whether to save node attributes CSV
        save_edge_attrs: Whether to save edge attributes CSV
        save_community: Whether to save community summary JSON
    """
    G = network_data['graph'].copy()
    user_metrics = network_data.get('user_metrics', {})
    
    print("\n" + "="*60)
    print("PREPARING NETWORK FOR GEPHI VISUALIZATION")
    print("="*60)
    
    # Step 1: Detect communities using modularity
    print("\nStep 1: Detecting communities...")
    communities = nx.community.greedy_modularity_communities(G.to_undirected())
    community_map = {}
    for idx, community in enumerate(communities):
        for user in community:
            community_map[user] = idx
    print(f"  Found {len(communities)} communities")
    
    # Step 2: Add node attributes for visualization
    print("\nStep 2: Adding node visualization attributes...")
    
    for user in G.nodes():
        metrics = user_metrics.get(user, {})
        helped = metrics.get('helped', 0)
        received = metrics.get('received_help', 0)
        total = metrics.get('total_interactions', 1)
        
        # Helper ratio: 0.0 = pure seeker, 1.0 = pure helper
        helper_ratio = helped / max(total, 1)
        
        # Node size based on helping activity (minimum 1, maximum 100)
        # More help given = larger node
        node_size = max(1, min(100, 5 + helped * 2))
        
        # Color based on helper/seeker role
        # Red = helper (gives lots of help)
        # Blue = seeker (receives help, gives little)
        # Purple = balanced (gives and receives roughly equally)
        if helper_ratio > 0.6:
            color = "255,0,0"  # Red - Helper
            role = "helper"
        elif helper_ratio < 0.4:
            color = "0,0,255"  # Blue - Seeker
            role = "seeker"
        else:
            color = "128,0,128"  # Purple - Balanced
            role = "balanced"
        
        # Add attributes to node
        G.nodes[user]['size'] = node_size
        G.nodes[user]['color'] = color
        G.nodes[user]['role'] = role
        G.nodes[user]['helper_ratio'] = helper_ratio
        G.nodes[user]['helped_count'] = helped
        G.nodes[user]['received_help_count'] = received
        G.nodes[user]['community'] = community_map.get(user, -1)
        G.nodes[user]['total_interactions'] = total
    
    # Step 3: Add edge attributes for visualization
    print("\nStep 3: Adding edge visualization attributes...")
    
    for u, v, data in G.edges(data=True):
        relationship_strength = data.get('relationship_strength', 0)
        weight = data.get('weight', 1)
        
        # Edge thickness based on strength
        # Maps 0-50 strength range to 0.5-5.0 width
        edge_width = 0.5 + (min(relationship_strength, 50) / 50) * 4.5
        
        # Edge color intensity based on strength
        # Stronger = more opaque red
        opacity = int(50 + min(relationship_strength * 10, 200))
        
        G[u][v]['width'] = edge_width
        G[u][v]['weight'] = relationship_strength  # Use strength as weight
        G[u][v]['label'] = f"{relationship_strength:.2f}"
    
    # Step 4: Calculate centrality measures
    print("\nStep 4: Calculating centrality measures...")
    
    degree_centrality = nx.degree_centrality(G)
    betweenness = nx.betweenness_centrality(G)
    closeness = nx.closeness_centrality(G)
    
    for user in G.nodes():
        G.nodes[user]['degree_centrality'] = degree_centrality.get(user, 0)
        G.nodes[user]['betweenness_centrality'] = betweenness.get(user, 0)
        G.nodes[user]['closeness_centrality'] = closeness.get(user, 0)
    
    # Step 5: Export enhanced GraphML for Gephi
    print("\nStep 5: Exporting to Gephi-compatible format...")
    
    graphml_file = None
    if save_graphml:
        # Create clean copy for GraphML (remove non-serializable attributes)
        G_graphml = G.copy()
        for u, v, data in G_graphml.edges(data=True):
            if 'interactions' in data:
                del data['interactions']
            if 'strength_components' in data:
                del data['strength_components']
        
        graphml_file = f"{output_prefix}_gephi_enhanced.graphml"
        nx.write_graphml(G_graphml, graphml_file)
        print(f"  Saved enhanced GraphML: {graphml_file}")
    
    # Step 6: Export node attributes CSV (for additional coloring options in Gephi)
    print("\nStep 6: Exporting node attributes...")
    
    node_attrs_file = None
    if save_node_attrs:
        node_attrs_file = f"{output_prefix}_node_attributes.csv"
        with open(node_attrs_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = [
                'user', 'role', 'helper_ratio', 'helped_count', 'received_help_count',
                'total_interactions', 'community', 'degree_centrality', 
                'betweenness_centrality', 'closeness_centrality', 'node_size'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for user in G.nodes():
                writer.writerow({
                    'user': user,
                    'role': G.nodes[user].get('role', 'unknown'),
                    'helper_ratio': f"{G.nodes[user].get('helper_ratio', 0):.3f}",
                    'helped_count': G.nodes[user].get('helped_count', 0),
                    'received_help_count': G.nodes[user].get('received_help_count', 0),
                    'total_interactions': G.nodes[user].get('total_interactions', 0),
                    'community': G.nodes[user].get('community', -1),
                    'degree_centrality': f"{G.nodes[user].get('degree_centrality', 0):.4f}",
                    'betweenness_centrality': f"{G.nodes[user].get('betweenness_centrality', 0):.4f}",
                    'closeness_centrality': f"{G.nodes[user].get('closeness_centrality', 0):.4f}",
                    'node_size': G.nodes[user].get('size', 1)
                })
        print(f"  Saved node attributes: {node_attrs_file}")
    
    # Step 7: Export community summary
    print("\nStep 7: Exporting community information...")
    
    community_summary_file = None
    if save_community:
        community_summary_file = f"{output_prefix}_community_summary.json"
        community_data = {}
        for community_id, community in enumerate(communities):
            helpers = [u for u in community if user_metrics.get(u, {}).get('helper_ratio', 0) > 0.6]
            seekers = [u for u in community if user_metrics.get(u, {}).get('helper_ratio', 0) < 0.4]
            
            community_data[f"community_{community_id}"] = {
                'size': len(community),
                'helpers': len(helpers),
                'seekers': len(seekers),
                'top_helpers': sorted(
                    helpers,
                    key=lambda x: user_metrics.get(x, {}).get('helped', 0),
                    reverse=True
                )[:5],
                'most_vulnerable': sorted(
                    seekers,
                    key=lambda x: user_metrics.get(x, {}).get('received_help', 0),
                    reverse=True
                )[:5]
            }
        
        with open(community_summary_file, 'w') as f:
            json.dump(community_data, f, indent=2)
        print(f"  Saved community summary: {community_summary_file}")
    
    # Step 8: Export edge attributes for Gephi
    print("\nStep 8: Exporting edge attributes...")
    
    edge_attrs_file = None
    if save_edge_attrs:
        edge_attrs_file = f"{output_prefix}_edge_attributes.csv"
        with open(edge_attrs_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['source', 'target', 'weight', 'relationship_strength', 'type']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for u, v, data in G.edges(data=True):
                writer.writerow({
                    'source': u,
                    'target': v,
                    'weight': data.get('weight', 1),
                    'relationship_strength': f"{data.get('relationship_strength', 0):.2f}",
                    'type': data.get('edge_type', 'reply')
                })
        print(f"  Saved edge attributes: {edge_attrs_file}")
    
    # Step 9: Summary statistics
    print("\n" + "="*60)
    print("VISUALIZATION READY - SUMMARY")
    print("="*60)
    
    helpers = [u for u in G.nodes() if user_metrics.get(u, {}).get('helper_ratio', 0) > 0.6]
    seekers = [u for u in G.nodes() if user_metrics.get(u, {}).get('helper_ratio', 0) < 0.4]
    balanced = [u for u in G.nodes() if 0.4 <= user_metrics.get(u, {}).get('helper_ratio', 0) <= 0.6]
    
    print(f"\nUser Roles:")
    print(f"  Helpers (red): {len(helpers)} users")
    print(f"  Seekers (blue): {len(seekers)} users")
    print(f"  Balanced (purple): {len(balanced)} users")
    
    print(f"\nTop 5 Central Helpers (by betweenness centrality):")
    top_central = sorted(
        [(u, betweenness.get(u, 0)) for u in helpers],
        key=lambda x: x[1],
        reverse=True
    )[:5]
    for i, (user, centrality) in enumerate(top_central, 1):
        helped = user_metrics.get(user, {}).get('helped', 0)
        print(f"  {i}. {user}: centrality={centrality:.4f}, helped={helped}")
    
    print(f"\nCommunities: {len(communities)}")
    
    # Step 10: Comprehensive metrics analysis
    print("\n" + "="*60)
    print("STEP 10: Comprehensive Metrics Analysis")
    print("="*60)
    
    if G.number_of_nodes() > 0:
        analyzer = GraphMetricsAnalyzer(G, "Gephi_Prepared_Network")
        is_large = G.number_of_nodes() > 500
        
        metrics = analyzer.analyze_all(
            include_centrality=not is_large,
            include_communities=not is_large
        )
        
        # Save comprehensive metrics
        metrics_json = f"{output_prefix}_comprehensive_metrics.json"
        metrics_txt = f"{output_prefix}_comprehensive_metrics.txt"
        analyzer.save_to_json(metrics_json)
        analyzer.save_to_txt(metrics_txt)
    
    print("\n" + "="*60)
    print("FILES TO IMPORT IN GEPHI:")
    print("="*60)
    if graphml_file:
        print(f"\n1. Main graph file: {graphml_file}")
        print("   - Open this in Gephi")
        print("   - Nodes already have: size, color, role attributes")
        print("   - Edges have: width, weight based on relationship strength")
    
    print("\n2. For additional analysis:")
    if node_attrs_file:
        print(f"   - Node attributes: {node_attrs_file}")
    if edge_attrs_file:
        print(f"   - Edge attributes: {edge_attrs_file}")
    if community_summary_file:
        print(f"   - Community info: {community_summary_file}")
    print(f"   - Comprehensive metrics (JSON): {metrics_json}")
    print(f"   - Comprehensive metrics (TXT): {metrics_txt}")
    
    if graphml_file:
        print("\nGephi Steps:")
        print("  1. Open: File -> Open -> " + graphml_file)
        print("  2. Layout: Layout panel -> ForceAtlas2 -> Run")
        print("  3. Nodes are already colored (red=helper, blue=seeker, purple=balanced)")
        print("  4. Nodes are sized by help given (larger = more helpful)")
        print("  5. Edges show relationship strength as thickness")
    
    return {
        'graph': G,
        'communities': communities,
        'community_map': community_map,
        'metrics': metrics if G.number_of_nodes() > 0 else None,
        'files': {
            'graphml': graphml_file,
            'node_attributes': node_attrs_file,
            'edge_attributes': edge_attrs_file,
            'community_summary': community_summary_file,
            'comprehensive_metrics_json': metrics_json if G.number_of_nodes() > 0 else None,
            'comprehensive_metrics_txt': metrics_txt if G.number_of_nodes() > 0 else None
        }
    }


if __name__ == "__main__":
    print("This script should be imported and used with prepared network data.")
    print("Use: prepare_for_gephi(network_data, output_prefix)")
