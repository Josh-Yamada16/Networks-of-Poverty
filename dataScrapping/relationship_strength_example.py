"""
Quick Start Example: Using Relationship Strength Metrics

This script demonstrates how to use the new relationship strength metrics
to analyze social connections in Reddit communities.
"""

import reddit_scraper as rs
import gephi_visualization_prep as gvp
import networkx as nx
import os
from datetime import datetime
from config import (
    PREPARE_GEPHI_VISUALIZATION,
    SAVE_GEPHI_GRAPHML,
    SAVE_NODE_ATTRIBUTES_CSV,
    SAVE_EDGE_ATTRIBUTES_CSV,
    SAVE_COMMUNITY_SUMMARY,
    SAVE_PICKLE_GRAPH,
    SAVE_REPLY_EDGES_CSV,
    SAVE_COPARTICIPATION_CSV,
    SAVE_NETWORK_STATS_JSON,
    PRINT_ANALYSIS_RESULTS
)

def main():
    print("=== Quick Start: Relationship Strength Analysis ===\n")
    
    # Configuration
    subreddit_name = 'poverty'  # Community-focused subreddit
    num_posts = 200

    # Step 1: Scrape Reddit data with comments
    print("Step 1: Scraping Reddit data...")
    posts = rs.get_reddit_data(
        subreddit_name=subreddit_name,
        num_posts=num_posts,
        sort_by='comments',
        include_comments=True,
        verbose=True
    )
    
    # Step 2: Build network with relationship strength calculations
    print("\nStep 2: Building network with relationship strength metrics...")
    network_data = rs.build_interaction_network(
        posts, 
        edge_strength_threshold=1.0  # Keep all edges, filter later if needed
    )
    
    G = network_data['graph']
    
    # Step 3: Display overall statistics
    print("\n" + "="*50)
    print("NETWORK STATISTICS")
    print("="*50)
    print(f"Total users: {network_data['stats']['num_users']}")
    print(f"Total reply interactions: {network_data['stats']['num_reply_edges']}")
    print(f"Total co-participation edges: {network_data['stats']['num_co_participation_edges']}")
    print(f"Mutual interaction pairs: {network_data['stats']['num_mutual_pairs']}")
    print(f"Strong relationships (strength > 1.5): {network_data['stats']['num_strong_relationships']}")
    print(f"Network density: {nx.density(G):.4f}")
    
    # Step 4: Analyze strongest relationships
    print("\n" + "="*50)
    print("TOP 10 STRONGEST RELATIONSHIPS")
    print("="*50)
    
    strong_edges = [
        (u, v, G[u][v].get('relationship_strength', 0)) 
        for u, v in G.edges() 
        if G[u][v].get('relationship_strength', 0) > 0
    ]
    strong_edges.sort(key=lambda x: x[2], reverse=True)
    
    for i, (from_user, to_user, strength) in enumerate(strong_edges[:10], 1):
        interactions = G[from_user][to_user].get('weight', 0)
        print(f"{i}. {from_user} -> {to_user}")
        print(f"   Strength: {strength:.2f} | Interactions: {interactions}")
    
    # Step 5: Analyze mutual relationships
    print("\n" + "="*50)
    print("TOP 5 MUTUAL RELATIONSHIPS (Bidirectional)")
    print("="*50)
    
    mutual_edges = []
    for u, v in G.edges():
        if G.has_edge(v, u):
            strength_uv = G[u][v].get('relationship_strength', 0)
            strength_vu = G[v][u].get('relationship_strength', 0)
            combined_strength = strength_uv + strength_vu
            mutual_pair = tuple(sorted([u, v]))
            mutual_edges.append((mutual_pair[0], mutual_pair[1], combined_strength))
    
    # Remove duplicates
    mutual_edges = list({e[:2]: e for e in mutual_edges}.values())
    mutual_edges.sort(key=lambda x: x[2], reverse=True)
    
    for i, (user1, user2, combined_strength) in enumerate(mutual_edges[:5], 1):
        print(f"{i}. {user1} <-> {user2}")
        print(f"   Combined Strength: {combined_strength:.2f}")
    
    # Step 6: Analyze helpers
    print("\n" + "="*50)
    print("TOP 10 MOST ACTIVE HELPERS")
    print("="*50)
    
    user_metrics = network_data.get('user_metrics', {})
    helpers = [
        (user, metrics['helped'], metrics['received_help']) 
        for user, metrics in user_metrics.items() 
        if user in G.nodes() and metrics['helped'] > 0
    ]
    helpers.sort(key=lambda x: x[1], reverse=True)
    
    for i, (user, helped_count, received_count) in enumerate(helpers[:10], 1):
        ratio = G.nodes[user].get('helper_ratio', 0)
        print(f"{i}. {user}")
        print(f"   Helped: {helped_count} | Received: {received_count} | Ratio: {ratio:.2f}")
    
    # Step 7: Analyze help-seekers (low helper ratio)
    print("\n" + "="*50)
    print("TOP 5 VULNERABLE USERS (Most in need of help)")
    print("="*50)
    
    vulnerable = [
        (user, G.nodes[user].get('received_help_count', 0), G.nodes[user].get('helper_ratio', 0))
        for user in G.nodes() 
        if G.nodes[user].get('received_help_count', 0) > 0
    ]
    vulnerable.sort(key=lambda x: x[1], reverse=True)
    
    for i, (user, received_count, ratio) in enumerate(vulnerable[:5], 1):
        helped_count = G.nodes[user].get('helped_count', 0)
        print(f"{i}. {user}")
        print(f"   Received help: {received_count} | Helped: {helped_count} | Ratio: {ratio:.2f}")
    
    # Step 8: Find communities (high clustering)
    print("\n" + "="*50)
    print("COMMUNITY CLUSTERS (High common neighbors)")
    print("="*50)
    
    # Find strongly clustered relationships
    clustered = []
    for u, v, data in G.edges(data=True):
        weight = data.get('weight', 0)
        strength = data.get('relationship_strength', 0)
        # If strength is significantly higher than weight, it's due to clustering
        clustering_boost = strength - weight
        if clustering_boost > 1.0:
            clustered.append((u, v, clustering_boost, strength))
    
    clustered.sort(key=lambda x: x[2], reverse=True)
    
    for i, (user1, user2, boost, strength) in enumerate(clustered[:5], 1):
        print(f"{i}. {user1} <-> {user2}")
        print(f"   Clustering boost: +{boost:.2f} | Total strength: {strength:.2f}")
    
    # Step 9: Network insights
    print("\n" + "="*50)
    print("NETWORK INSIGHTS")
    print("="*50)
    
    # Calculate some interesting metrics
    if helpers:
        top_helper = helpers[0]
        print(f"\nMost active helper: {top_helper[0]} (helped {top_helper[1]} users)")
    
    if vulnerable:
        most_vulnerable = vulnerable[0]
        print(f"Most vulnerable user: {most_vulnerable[0]} (received {most_vulnerable[1]} replies)")
    
    if strong_edges:
        strongest = strong_edges[0]
        print(f"Strongest connection: {strongest[0]} -> {strongest[1]} (strength: {strongest[2]:.2f})")
    
    print(f"\nNetwork has {nx.number_weakly_connected_components(G)} communities")
    
    # Step 10: Export network data (optional based on config)
    if any([SAVE_PICKLE_GRAPH, SAVE_REPLY_EDGES_CSV, SAVE_COPARTICIPATION_CSV, 
            SAVE_NETWORK_STATS_JSON, SAVE_GEPHI_GRAPHML]):
        print("\n" + "="*50)
        print("SAVING NETWORK DATA")
        print("="*50)
        
        # Create organized output folder structure
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_folder = f"results/{subreddit_name}/{timestamp}"
        os.makedirs(output_folder, exist_ok=True)
        
        base_filename = f"{output_folder}/network_{subreddit_name}_{timestamp}"
        saved_files = rs.save_network_data(
            network_data, 
            base_filename=base_filename,
            save_pickle=SAVE_PICKLE_GRAPH,
            save_reply_edges=SAVE_REPLY_EDGES_CSV,
            save_coparticipation=SAVE_COPARTICIPATION_CSV,
            save_stats=SAVE_NETWORK_STATS_JSON,
            save_graphml=SAVE_GEPHI_GRAPHML
        )
        print(f"\nSaved {len(saved_files)} files:")
        for file_type, filepath in saved_files.items():
            print(f"  - {file_type}: {filepath}")
        
        # Step 11: Prepare for Gephi visualization (optional based on config)
        if PREPARE_GEPHI_VISUALIZATION:
            print("\n" + "="*50)
            print("PREPARING FOR GEPHI VISUALIZATION")
            print("="*50)
            
            gephi_data = gvp.prepare_for_gephi(
                network_data, 
                base_filename,
                save_graphml=SAVE_GEPHI_GRAPHML,
                save_node_attrs=SAVE_NODE_ATTRIBUTES_CSV,
                save_edge_attrs=SAVE_EDGE_ATTRIBUTES_CSV,
                save_community=SAVE_COMMUNITY_SUMMARY
            )
            print(f"\nGephi files saved to: {output_folder}")
            print("\nVisualization files created:")
            for file_type, filepath in gephi_data['files'].items():
                print(f"  - {file_type}: {filepath}")
        
        print("\n=== Analysis Complete ===")
        print(f"Results saved to: {output_folder}")
    else:
        print("\n=== Analysis Complete ===")
        print("(File saving disabled in config)")

if __name__ == "__main__":
    main()
