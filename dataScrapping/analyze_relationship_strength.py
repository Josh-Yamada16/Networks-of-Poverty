"""
Institutional Network Analysis: Posts as Resource Distribution Centers

This script analyzes how posts (institutions) distribute resources to users
and how users form peer networks around these institutional hubs.
"""

import reddit_scraper as rs
import export_for_gephi as gvp
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

def build_institutional_network(posts):
    """
    Build a network where posts are institutions distributing resources
    and users form peer networks through direct interactions.
    
    Node types:
    - Posts: Institution nodes (type='post')
    - Users: Participant nodes (type='user')
    
    Edge types:
    - Post → User: Resource distribution (one-directional)
    - User ↔ User: Peer connections established through direct replies only
    """
    G = nx.DiGraph()
    
    user_interactions = {}  # Track user-to-user interactions
    post_participation = {}  # Track which users participate in which posts
    
    for post in posts:
        post_id = post['id']
        post_title = post.get('title', 'No title')[:50]
        post_author = post.get('author', '[deleted]')
        
        # Add post node as institution
        G.add_node(post_id, node_type='post', title=post_title, 
                  score=post.get('score', 0), comment_count=post.get('num_comments', 0))
        
        post_participation[post_id] = set()
        
        # Process comments
        comments = post.get('comments', [])
        
        def process_comment(comment, parent_author=None, depth=0):
            """Recursively process comments and replies"""
            author = comment.get('author')
            
            if not author or author == '[deleted]':
                return
            
            # Add user node
            if author not in G:
                G.add_node(author, node_type='user', depth=depth)
            
            # Add edge from post to user (resource distribution)
            if not G.has_edge(post_id, author):
                G.add_edge(post_id, author, edge_type='distribution', weight=1)
            else:
                G[post_id][author]['weight'] = G[post_id][author].get('weight', 0) + 1
            
            post_participation[post_id].add(author)
            
            # Track interaction with parent comment (direct reply)
            if parent_author and parent_author != author and parent_author != '[deleted]':
                if parent_author not in G:
                    G.add_node(parent_author, node_type='user', depth=depth-1)
                
                # Create bidirectional peer edge (direct reply only)
                if not G.has_edge(author, parent_author):
                    G.add_edge(author, parent_author, edge_type='peer', weight=1)
                else:
                    G[author][parent_author]['weight'] = G[author][parent_author].get('weight', 0) + 1
                
                if not G.has_edge(parent_author, author):
                    G.add_edge(parent_author, author, edge_type='peer', weight=1)
                else:
                    G[parent_author][author]['weight'] = G[parent_author][author].get('weight', 0) + 1
                
                # Track interaction
                pair = tuple(sorted([author, parent_author]))
                user_interactions[pair] = user_interactions.get(pair, 0) + 1
            
            # Process nested replies (pass current author as parent_author)
            replies = comment.get('replies', [])
            for reply in replies:
                process_comment(reply, parent_author=author, depth=depth + 1)
        
        for comment in comments:
            process_comment(comment, parent_author=post_author, depth=0)
    
    # Calculate distribution metrics
    post_nodes = [n for n, attr in G.nodes(data=True) if attr.get('node_type') == 'post']
    user_nodes = [n for n, attr in G.nodes(data=True) if attr.get('node_type') == 'user']
    
    post_distribution_metrics = {}
    for post_id in post_nodes:
        successors = list(G.successors(post_id))
        total_reach = sum(G[post_id][u].get('weight', 0) for u in successors)
        post_distribution_metrics[post_id] = {
            'unique_users': len(successors),
            'total_reach': total_reach,
            'avg_engagement': total_reach / len(successors) if successors else 0
        }
    
    # Convert peer interactions to reply_edges format for compatibility
    reply_edges = []
    for u, v, data in G.edges(data=True):
        if data.get('edge_type') == 'peer':
            reply_edges.append({
                'from': u,
                'to': v,
                'type': 'peer',
                'post_id': '',
                'comment_id': '',
                'score': 0,
                'timestamp': 0
            })
    
    # Create stats dictionary for compatibility
    stats = {
        'num_users': len(user_nodes),
        'num_posts': len(post_nodes),
        'num_reply_edges': len(reply_edges),
        'num_co_participation_edges': 0,
        'num_mutual_pairs': 0,
        'num_strong_relationships': 0
    }
    
    return {
        'graph': G,
        'post_distribution_metrics': post_distribution_metrics,
        'user_interactions': user_interactions,
        'post_participation': post_participation,
        'reply_edges': reply_edges,
        'co_participation_edges': [],
        'stats': stats,
        'user_posts': {}
    }


def main():
    print("=== Institutional Network Analysis: Posts as Resource Distribution Centers ===\n")
    
    # Configuration - allow override from environment variable for batch processing
    subreddit_name = os.environ.get('ANALYSIS_SUBREDDIT', 'poverty')  # Community-focused subreddit
    num_posts = 2
    
    print(f"Analyzing subreddit: r/{subreddit_name}\n")

    # Step 1: Scrape Reddit data with comments
    print("Step 1: Scraping Reddit data...")
    posts = rs.get_reddit_data(
        subreddit_name=subreddit_name,
        num_posts=num_posts,
        sort_by='comments',
        time_filter='all',
        include_comments=True,
        verbose=True,
        max_comment_depth=100,
        use_cache=True,  # Use cached data if available
        force_refresh=False  # Set to True to force re-scraping
    )
    
    # Step 2: Build institutional network
    print("\nStep 2: Building institutional network (posts as resource distribution centers)...")
    network_data = build_institutional_network(posts)
    
    G = network_data['graph']
    
    # Step 3: Display network overview
    print("\n" + "="*50)
    print("NETWORK OVERVIEW")
    print("="*50)
    
    # Count node types
    post_nodes = [n for n, attr in G.nodes(data=True) if attr.get('node_type') == 'post']
    user_nodes = [n for n, attr in G.nodes(data=True) if attr.get('node_type') == 'user']
    
    print(f"Total institutions (posts): {len(post_nodes)}")
    print(f"Total users: {len(user_nodes)}")
    
    # Count edge types
    distribution_edges = [(u, v) for u, v, attr in G.edges(data=True) if attr.get('edge_type') == 'distribution']
    peer_edges = [(u, v) for u, v, attr in G.edges(data=True) if attr.get('edge_type') == 'peer']
    
    print(f"Distribution edges (post->user): {len(distribution_edges)}")
    print(f"Peer edges (user<->user): {len(peer_edges)}")
    print(f"Average distribution reach per post: {len(distribution_edges) / len(post_nodes):.2f}")
    
    # Step 4: Analyze institutional (post) resource distribution
    print("\n" + "="*50)
    print("TOP 10 MOST RESOURCEFUL INSTITUTIONS (Posts)")
    print("="*50)
    
    post_metrics = network_data['post_distribution_metrics']
    ranked_posts = sorted(
        [(post_id, metrics) for post_id, metrics in post_metrics.items()],
        key=lambda x: x[1]['total_reach'],
        reverse=True
    )
    
    for i, (post_id, metrics) in enumerate(ranked_posts[:10], 1):
        post_title = G.nodes[post_id].get('title', 'No title')
        post_score = G.nodes[post_id].get('score', 0)
        print(f"{i}. {post_title}")
        print(f"   Score: {post_score} | Users reached: {metrics['unique_users']} | Total engagement: {metrics['total_reach']}")
    
    # Step 5: Analyze user participation distribution
    print("\n" + "="*50)
    print("USER PARTICIPATION IN INSTITUTIONS")
    print("="*50)
    
    user_participation = {}
    for user in user_nodes:
        incoming = list(G.predecessors(user))  # Posts that distributed to this user
        user_participation[user] = len(incoming)
    
    most_engaged_users = sorted(user_participation.items(), key=lambda x: x[1], reverse=True)
    
    print(f"Average posts participated in per user: {sum(user_participation.values()) / len(user_nodes):.2f}")
    print(f"\nTop 10 most engaged users (most institutional participation):")
    for i, (user, num_posts) in enumerate(most_engaged_users[:10], 1):
        print(f"{i}. {user}: participated in {num_posts} post(s)")
    
    # Step 6: Analyze peer network (user-to-user connections)
    print("\n" + "="*50)
    print("PEER NETWORK ANALYSIS (User-to-User Connections)")
    print("="*50)
    
    user_interaction_metrics = {}
    for user in user_nodes:
        outgoing_peers = list(G.successors(user))
        incoming_peers = list(G.predecessors(user))
        # Filter out posts
        outgoing_peers = [u for u in outgoing_peers if G.nodes[u].get('node_type') == 'user']
        incoming_peers = [u for u in incoming_peers if G.nodes[u].get('node_type') == 'user']
        
        user_interaction_metrics[user] = {
            'peer_connections': len(set(outgoing_peers + incoming_peers)),
            'outgoing': len(outgoing_peers),
            'incoming': len(incoming_peers)
        }
    
    most_connected_peers = sorted(
        user_interaction_metrics.items(),
        key=lambda x: x[1]['peer_connections'],
        reverse=True
    )
    
    print(f"Total peer connections in network: {len(peer_edges)}")
    print(f"Average peer connections per user: {sum(m['peer_connections'] for m in user_interaction_metrics.values()) / len(user_nodes):.2f}")
    print(f"\nTop 10 most connected peers (most interactions with other users):")
    for i, (user, metrics) in enumerate(most_connected_peers[:10], 1):
        print(f"{i}. {user}: {metrics['peer_connections']} connections (sent {metrics['outgoing']}, received {metrics['incoming']})")
    
    # Step 7: Resource distribution patterns
    print("\n" + "="*50)
    print("RESOURCE DISTRIBUTION PATTERNS")
    print("="*50)
    
    # Analyze how resources flow from institutions to users
    print("\nInstitution-to-User Flow Analysis:")
    distribution_intensity = {}
    for post_id, metrics in ranked_posts:
        distribution_intensity[post_id] = metrics['total_reach']
    
    # Categorize distribution patterns
    high_reach = len([m for m in post_metrics.values() if m['total_reach'] > 20])
    medium_reach = len([m for m in post_metrics.values() if 5 <= m['total_reach'] <= 20])
    low_reach = len([m for m in post_metrics.values() if m['total_reach'] < 5])
    
    print(f"High-reach institutions (>20 participants): {high_reach}")
    print(f"Medium-reach institutions (5-20 participants): {medium_reach}")
    print(f"Low-reach institutions (<5 participants): {low_reach}")
    
    # Analyze user concentration
    print("\nUser Concentration Pattern:")
    user_institutional_reach = [metrics['unique_users'] for metrics in post_metrics.values()]
    print(f"Average users per institution: {sum(user_institutional_reach) / len(user_institutional_reach):.2f}")
    print(f"Max users reached by single institution: {max(user_institutional_reach)}")
    print(f"Min users reached by single institution: {min(user_institutional_reach)}")
    
    # Analyze peer network density around institutions
    print("\nPeer Network Density Around Institutions:")
    total_peer_edges = len(peer_edges)
    potential_peer_connections = len(user_nodes) * (len(user_nodes) - 1) / 2
    peer_density = total_peer_edges / potential_peer_connections if potential_peer_connections > 0 else 0
    print(f"Peer network density: {peer_density:.4f}")
    print(f"Total peer connections: {total_peer_edges}")
    
    # Step 8: Network insights
    print("\n" + "="*50)
    print("INSTITUTIONAL NETWORK INSIGHTS")
    print("="*50)
    
    if ranked_posts:
        top_post = ranked_posts[0]
        print(f"\nMost resourceful institution: {top_post[0]}")
        print(f"  Title: {G.nodes[top_post[0]].get('title')}")
        print(f"  Users reached: {top_post[1]['unique_users']}")
        print(f"  Total engagement: {top_post[1]['total_reach']}")
    
    if most_engaged_users:
        top_user = most_engaged_users[0]
        print(f"\nMost engaged user: {top_user[0]} (participated in {top_user[1]} institutions)")
    
    if most_connected_peers:
        top_peer = most_connected_peers[0]
        print(f"Most connected peer: {top_peer[0]} ({top_peer[1]['peer_connections']} connections)")
    
    # Institutional coverage
    coverage_rate = len(user_nodes) / len(post_nodes) if post_nodes else 0
    print(f"\nInstitutional coverage ratio: {coverage_rate:.2f} users per institution")
    
    # Step 9: Export network data (optional based on config)
    if any([SAVE_PICKLE_GRAPH, SAVE_REPLY_EDGES_CSV, SAVE_COPARTICIPATION_CSV, 
            SAVE_NETWORK_STATS_JSON, SAVE_GEPHI_GRAPHML]):
        print("\n" + "="*50)
        print("SAVING INSTITUTIONAL NETWORK DATA")
        print("="*50)
        
        # Create organized output folder structure
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_folder = f"results/{subreddit_name}/institutional_network_{timestamp}"
        os.makedirs(output_folder, exist_ok=True)
        
        base_filename = f"{output_folder}/institutional_network_{subreddit_name}_{timestamp}"
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
        
        # Step 10: Prepare for Gephi visualization (optional based on config)
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
        
        print("\n=== Institutional Network Analysis Complete ===")
        print(f"Results saved to: {output_folder}")
    else:
        print("\n=== Institutional Network Analysis Complete ===")
        print("(File saving disabled in config)")

if __name__ == "__main__":
    main()
