"""
Example script demonstrating how to use the enhanced Reddit scraper
to collect interaction data and build social networks.

This script shows how to:
1. Scrape Reddit posts with full comment trees
2. Build user interaction networks
3. Analyze network properties
4. Export network data for visualization
"""

import reddit_scraper as rs
import networkx as nx
import matplotlib.pyplot as plt

def main():
    print("=== Reddit Social Network Analysis Example ===\n")
    
    # Configuration
    subreddit_name = 'poverty'
    num_posts = 100
    sort_by = 'comments'
    time_filter = 'all'
    max_comment_depth = 100  # How deep to traverse comment trees
    
    # Step 1: Scrape posts with comments
    print("Step 1: Scraping posts with full comment trees...")
    posts = rs.get_reddit_data(
        subreddit_name=subreddit_name,  # Target subreddit
        num_posts=num_posts,  # Number of posts to analyze
        sort_by=sort_by,  # Get 'top', 'hot', 'new', 'rising', 'controversial', 'comments', 'interaction'
        time_filter=time_filter,  # From 'hour', 'day', 'week', 'month', 'year', 'all'
        include_comments=True,  # IMPORTANT: Fetch full comment trees
        max_comment_depth=max_comment_depth,  # How deep to traverse replies
        verbose=True  # Show progress
    )
    
    print(f"\nCollected {len(posts)} posts with comments")
    
    # Step 2: Build interaction network
    print("\nStep 2: Building user interaction network...")
    network_data = rs.build_interaction_network(posts)
    
    # Step 3: Analyze network
    print("\n=== Network Analysis Results ===")
    print(f"Total users: {network_data['stats']['num_users']}")
    print(f"Reply interactions: {network_data['stats']['num_reply_edges']}")
    print(f"Co-participation edges: {network_data['stats']['num_co_participation_edges']}")
    
    G = network_data['graph']
    
    # Calculate network metrics
    if G.number_of_nodes() > 0:
        print(f"\nNetwork Density: {nx.density(G):.4f}")
        print(f"Weakly Connected Components: {nx.number_weakly_connected_components(G)}")
        
        # Find most active users
        print("\n=== Most Active Users (by degree) ===")
        degrees = [(node, G.in_degree(node) + G.out_degree(node)) 
                   for node in G.nodes() if node != '[deleted]']
        degrees.sort(key=lambda x: x[1], reverse=True)
        
        for i, (user, degree) in enumerate(degrees[:10], 1):
            in_deg = G.in_degree(user)
            out_deg = G.out_degree(user)
            print(f"{i}. {user}: {degree} total (↓{in_deg} replies received, ↑{out_deg} replies sent)")
        
        # Find most replied-to users
        print("\n=== Most Replied-To Users ===")
        in_degrees = [(node, G.in_degree(node)) 
                      for node in G.nodes() if node != '[deleted]']
        in_degrees.sort(key=lambda x: x[1], reverse=True)
        
        for i, (user, in_deg) in enumerate(in_degrees[:5], 1):
            print(f"{i}. {user}: {in_deg} replies received")
    
    # Step 4: Save network data
    print("\n=== Saving Network Data ===")
    # Create organized output folder structure
    import os
    from datetime import datetime
    
    # Option: Organize by subreddit and timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_folder = f"results/{subreddit_name}/{timestamp}"
    os.makedirs(output_folder, exist_ok=True)  # Create folder if it doesn't exist
    
    # Create a descriptive filename
    base_filename = f"{output_folder}/{subreddit_name}_{sort_by}_{time_filter}_{num_posts}posts"
    
    saved_files = rs.save_network_data(network_data, base_filename=base_filename)
    
    # Save analysis metadata
    metadata = {
        'timestamp': timestamp,
        'subreddit': subreddit_name,
        'num_posts': num_posts,
        'sort_by': sort_by,
        'time_filter': time_filter,
        'total_users': network_data['stats']['num_users'],
        'reply_interactions': network_data['stats']['num_reply_edges'],
        'co_participation_edges': network_data['stats']['num_co_participation_edges']
    }
    import json
    with open(f"{output_folder}/analysis_metadata.json", 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"Saved analysis metadata to {output_folder}/analysis_metadata.json")
    
    print("\n=== Files Created ===")
    for file_type, filepath in saved_files.items():
        print(f"  {file_type}: {filepath}")
    
    # Step 5: Create a simple visualization (optional)
    print("\n=== Creating Network Visualization ===")
    try:
        # Get the largest weakly connected component for visualization
        if G.number_of_nodes() > 0:
            largest_wcc = max(nx.weakly_connected_components(G), key=len)
            subgraph = G.subgraph(largest_wcc).copy()
            
            # Only visualize if not too large
            if subgraph.number_of_nodes() <= 50:
                plt.figure(figsize=(12, 10))
                
                # Use spring layout
                pos = nx.spring_layout(subgraph, k=0.5, iterations=50)
                
                # Draw nodes
                nx.draw_networkx_nodes(subgraph, pos, 
                                      node_size=300, 
                                      node_color='lightblue',
                                      alpha=0.7)
                
                # Draw edges
                nx.draw_networkx_edges(subgraph, pos, 
                                      alpha=0.3, 
                                      arrows=True,
                                      arrowsize=10,
                                      edge_color='gray')
                
                # Draw labels
                nx.draw_networkx_labels(subgraph, pos, 
                                       font_size=8,
                                       font_weight='bold')
                
                plt.title("User Interaction Network (Largest Component)")
                plt.axis('off')
                plt.tight_layout()
                
                viz_file = "network_visualization.png"
                plt.savefig(viz_file, dpi=300, bbox_inches='tight')
                print(f"Saved visualization to {viz_file}")
                print("(Note: For large networks, use Gephi or Cytoscape with the .graphml file)")
            else:
                print(f"Network too large for matplotlib ({subgraph.number_of_nodes()} nodes)")
                print("Use Gephi or Cytoscape to visualize the .graphml file")
    except Exception as e:
        print(f"Visualization skipped: {e}")
    
    print("\n=== Analysis Complete ===")
    print("\nNext steps:")
    print("1. Open the .graphml file in Gephi or Cytoscape for advanced visualization")
    print("2. Use the edge CSV files for custom analysis")
    print("3. Load the .gpickle file in Python with nx.read_gpickle() for further analysis")

def analyze_interaction_types():
    """
    Example showing how to analyze different types of interactions
    """
    print("\n=== Analyzing Interaction Types ===\n")
    
    # Scrape data
    posts = rs.get_reddit_data(
        subreddit_name='assistance',
        num_posts=3,
        include_comments=True,
        verbose=False
    )
    
    # Build network
    network_data = rs.build_interaction_network(posts)
    
    # Analyze reply patterns
    print("Reply Network Analysis:")
    reply_edges = network_data['reply_edges']
    
    if reply_edges:
        # Count replies per user
        replies_sent = {}
        replies_received = {}
        
        for edge in reply_edges:
            from_user = edge['from']
            to_user = edge['to']
            
            replies_sent[from_user] = replies_sent.get(from_user, 0) + 1
            replies_received[to_user] = replies_received.get(to_user, 0) + 1
        
        print(f"  Total reply interactions: {len(reply_edges)}")
        print(f"  Unique users sending replies: {len(replies_sent)}")
        print(f"  Unique users receiving replies: {len(replies_received)}")
    
    # Analyze co-participation
    print("\nCo-Participation Network Analysis:")
    copart_edges = network_data['co_participation_edges']
    
    if copart_edges:
        print(f"  Total co-participation edges: {len(copart_edges)}")
        
        # Find posts with most co-participation
        posts_copart = {}
        for edge in copart_edges:
            post_id = edge['post_id']
            posts_copart[post_id] = posts_copart.get(post_id, 0) + 1
        
        print(f"  Posts generating co-participation: {len(posts_copart)}")

if __name__ == "__main__":
    # Run main example
    main()
    
    # Uncomment to run interaction type analysis
    # analyze_interaction_types()
