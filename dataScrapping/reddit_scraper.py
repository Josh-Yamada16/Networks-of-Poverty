import praw
import requests
import networkx as nx
import json
import csv
import pickle
import time
from datetime import datetime
from collections import defaultdict
from config import *  # Import all configuration settings

# Initialize Reddit API with credentials from config
reddit = praw.Reddit(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    user_agent=USER_AGENT
)

def get_comment_tree(comment, depth=0, max_depth=10):
    """
    Recursively collect all comments and their replies, creating a hierarchical structure.
    
    Args:
        comment: PRAW comment object
        depth: Current depth in the comment tree
        max_depth: Maximum depth to traverse (prevents infinite recursion)
    
    Returns:
        Dictionary containing comment data and nested replies
    """
    # Handle deleted comments
    author = str(comment.author) if comment.author else '[deleted]'
    
    comment_data = {
        'id': comment.id,
        'author': author,
        'body': comment.body,
        'score': comment.score,
        'created_utc': comment.created_utc,
        'created_date': datetime.fromtimestamp(comment.created_utc).strftime('%Y-%m-%d %H:%M:%S'),
        'parent_id': comment.parent_id,  # Links to parent comment or post
        'depth': depth,
        'replies': []
    }
    
    # Recursively get all nested replies
    if depth < max_depth:
        try:
            # Replace MoreComments objects to get actual comments
            comment.replies.replace_more(limit=0)
            for reply in comment.replies:
                reply_data = get_comment_tree(reply, depth + 1, max_depth)
                comment_data['replies'].append(reply_data)
        except Exception as e:
            print(f"Error fetching replies for comment {comment.id}: {e}")
    
    return comment_data

def build_interaction_network(posts_with_comments):
    """
    Build a user interaction network from posts and comments.
    Creates edges between users based on:
    1. Direct replies (User A replies to User B)
    2. Co-participation (Users comment on the same post)
    
    Args:
        posts_with_comments: List of posts with full comment trees
    
    Returns:
        Dictionary containing NetworkX graph and edge list
    """
    G = nx.DiGraph()  # Directed graph for reply relationships
    edges = []  # List of all interactions
    user_posts = defaultdict(list)  # Track which posts each user participated in
    
    for post in posts_with_comments:
        post_id = post['id']
        post_author = post.get('author', '[deleted]')
        
        # Add post author as a node
        if post_author != '[deleted]':
            G.add_node(post_author, node_type='user')
            user_posts[post_author].append(post_id)
        
        # Process all comments to find interactions
        def process_comment_for_network(comment_data, parent_author=None):
            """Recursively process comments to build network edges"""
            author = comment_data['author']
            
            # Skip deleted users
            if author == '[deleted]':
                return
            
            # Add user as node
            if not G.has_node(author):
                G.add_node(author, node_type='user')
            
            # Track user participation in this post
            if post_id not in user_posts[author]:
                user_posts[author].append(post_id)
            
            # Create edge for direct reply
            if parent_author and parent_author != '[deleted]' and parent_author != author:
                # Add or update edge weight (number of interactions)
                if G.has_edge(author, parent_author):
                    G[author][parent_author]['weight'] += 1
                    G[author][parent_author]['interactions'].append({
                        'type': 'reply',
                        'post_id': post_id,
                        'comment_id': comment_data['id'],
                        'timestamp': comment_data['created_utc']
                    })
                else:
                    G.add_edge(author, parent_author, 
                             weight=1,
                             edge_type='reply',
                             interactions=[{
                                 'type': 'reply',
                                 'post_id': post_id,
                                 'comment_id': comment_data['id'],
                                 'timestamp': comment_data['created_utc']
                             }])
                
                # Add to edge list
                edges.append({
                    'from': author,
                    'to': parent_author,
                    'type': 'reply',
                    'post_id': post_id,
                    'comment_id': comment_data['id'],
                    'score': comment_data['score'],
                    'timestamp': comment_data['created_utc']
                })
            
            # Recursively process replies
            for reply in comment_data.get('replies', []):
                process_comment_for_network(reply, parent_author=author)
        
        # Process comments (first level replies to post)
        for comment in post.get('comments', []):
            # Parent of top-level comment is the post author
            process_comment_for_network(comment, parent_author=post_author)
    
    # Create co-participation edges (users who commented on same posts)
    co_participation_edges = []
    for post_id, participants in _get_post_participants(user_posts).items():
        participants = list(participants)
        for i, user1 in enumerate(participants):
            for user2 in participants[i+1:]:
                co_participation_edges.append({
                    'from': user1,
                    'to': user2,
                    'type': 'co_participation',
                    'post_id': post_id
                })
    
    return {
        'graph': G,
        'reply_edges': edges,
        'co_participation_edges': co_participation_edges,
        'user_posts': dict(user_posts),
        'stats': {
            'num_users': G.number_of_nodes(),
            'num_reply_edges': len(edges),
            'num_co_participation_edges': len(co_participation_edges)
        }
    }

def _get_post_participants(user_posts):
    """Helper function to invert user_posts mapping to post_participants"""
    post_participants = defaultdict(set)
    for user, posts in user_posts.items():
        for post_id in posts:
            post_participants[post_id].add(user)
    return post_participants

def get_reddit_data(subreddit_name=None, num_posts=None, sort_by=None, verbose=None, time_filter=None, include_comments=True, max_comment_depth=10):
    """
    Get Reddit posts with parameters from config file or overrides
    
    Args:
        subreddit_name: Name of subreddit to scrape
        num_posts: Number of posts to collect
        sort_by: Sorting method ('top', 'comments', 'interaction', 'hot', 'controversial')
        verbose: Print progress messages
        time_filter: Time filter for sorting ('hour', 'day', 'week', 'month', 'year', 'all')
        include_comments: Whether to fetch full comment trees (default: True)
        max_comment_depth: Maximum depth for comment tree traversal (default: 10)
    
    Returns:
        List of posts with optional comment trees
    """
    # Use config defaults if not specified
    subreddit_name = subreddit_name or SUBREDDIT_NAME
    num_posts = num_posts or NUM_POSTS
    sort_by = sort_by or SORT_BY
    verbose = verbose if verbose is not None else VERBOSE
    time_filter = time_filter or TIME_FILTER
    
    subreddit = reddit.subreddit(subreddit_name)
    
    # Choose sorting method based on config
    if sort_by == 'comments':
        post_generator = subreddit.top(limit=num_posts * OVERSAMPLE_MULTIPLIER, time_filter=time_filter)
    elif sort_by == 'interaction':
        post_generator = subreddit.top(limit=num_posts * OVERSAMPLE_MULTIPLIER, time_filter=time_filter)
    elif sort_by == 'hot':
        post_generator = subreddit.hot(limit=num_posts)
    elif sort_by == 'controversial':
        post_generator = subreddit.controversial(limit=num_posts, time_filter=time_filter)
    else:  # default to 'top'
        post_generator = subreddit.top(limit=num_posts, time_filter=time_filter)
    
    # Collect posts
    all_posts = []
    if verbose:
        print(f"Fetching posts from r/{subreddit_name} (sort: {sort_by})...")
    
    for post in post_generator:
        # Apply filters from config
        if post.score < MIN_SCORE or post.num_comments < MIN_COMMENTS:
            continue
        if MAX_SCORE and post.score > MAX_SCORE:
            continue
        if MAX_COMMENTS and post.num_comments > MAX_COMMENTS:
            continue
        
        interaction_score = post.score + post.num_comments
        if interaction_score < MIN_INTERACTION_SCORE:
            continue
        
        # Build post data based on config settings
        post_data = {
            'title': post.title,
            'score': post.score,
            'id': post.id,
            'url': post.url,
            'num_comments': post.num_comments,
            'interaction_score': interaction_score
        }
        
        # Add optional fields based on config
        if INCLUDE_AUTHOR:
            post_data['author'] = str(post.author) if post.author else '[deleted]'
        
        if INCLUDE_CREATED_TIME:
            post_data['created_utc'] = post.created_utc
            post_data['created_date'] = datetime.fromtimestamp(post.created_utc).strftime('%Y-%m-%d %H:%M:%S')
        
        if INCLUDE_FLAIR:
            post_data['flair'] = post.link_flair_text
        
        if INCLUDE_SELFTEXT:
            post_data['selftext'] = post.selftext
        
        # Fetch full comment tree if requested
        if include_comments and post.num_comments > 0:
            if verbose:
                print(f"  Fetching {post.num_comments} comments for: {post.title[:50]}...")
            
            try:
                # Get the full post with comments
                post.comments.replace_more(limit=0)  # Remove "load more comments" placeholders
                
                comments = []
                for comment in post.comments:
                    comment_tree = get_comment_tree(comment, depth=0, max_depth=max_comment_depth)
                    comments.append(comment_tree)
                
                post_data['comments'] = comments
                post_data['total_comments_collected'] = _count_comments(comments)
                
                if verbose:
                    print(f"    Collected {post_data['total_comments_collected']} comments (depth: {max_comment_depth})")
                
            except Exception as e:
                print(f"  Error fetching comments for post {post.id}: {e}")
                post_data['comments'] = []
                post_data['total_comments_collected'] = 0
        else:
            post_data['comments'] = []
            post_data['total_comments_collected'] = 0
        
        all_posts.append(post_data)
        
        # Add delay if specified in config
        if REQUEST_DELAY > 0:
            time.sleep(REQUEST_DELAY)
    
    # Sort by interaction method if specified
    if sort_by == 'comments':
        all_posts.sort(key=lambda x: x['num_comments'], reverse=True)
        posts = all_posts[:num_posts]
    elif sort_by == 'interaction':
        all_posts.sort(key=lambda x: x['interaction_score'], reverse=True)
        posts = all_posts[:num_posts]
    else:
        posts = all_posts[:num_posts]
    
    # Print with verbose option
    if verbose:
        print(f"Found {len(posts)} posts after filtering")
        for i, post_data in enumerate(posts, 1):
            title = post_data['title']
            print(f"Post {i}: {title[:60]}..." if len(title) > 60 else f"Post {i}: {title}")
            print(f"  Score: {post_data['score']}, Comments: {post_data['num_comments']}, Interaction: {post_data['interaction_score']}")
    
    return posts

def _count_comments(comments):
    """Helper function to recursively count total comments in a tree"""
    count = len(comments)
    for comment in comments:
        count += _count_comments(comment.get('replies', []))
    return count

def get_multi_subreddit_data():
    """Get data from multiple subreddits as specified in config"""
    all_posts = []
    for subreddit_name in SUBREDDIT_LIST:
        try:
            posts = get_reddit_data(subreddit_name, verbose=VERBOSE)
            for post in posts:
                post['subreddit'] = subreddit_name
            all_posts.extend(posts)
            if VERBOSE:
                print(f"Got {len(posts)} posts from r/{subreddit_name}")
        except Exception as e:
            print(f"Error scraping r/{subreddit_name}: {e}")
    
    # Sort combined results
    if SORT_BY == 'comments':
        all_posts.sort(key=lambda x: x['num_comments'], reverse=True)
    elif SORT_BY == 'interaction':
        all_posts.sort(key=lambda x: x['interaction_score'], reverse=True)
    else:
        all_posts.sort(key=lambda x: x['score'], reverse=True)
    
    return all_posts[:NUM_POSTS]

def save_posts_to_file(posts, filename=None, format_type=None):
    """Save posts to file in specified format"""
    filename = filename or OUTPUT_FILENAME
    format_type = format_type or OUTPUT_FORMAT
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if format_type == 'json':
        filepath = f"{filename}_{timestamp}.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(posts, f, indent=2, ensure_ascii=False)
    
    elif format_type == 'csv':
        filepath = f"{filename}_{timestamp}.csv"
        if posts:
            # For CSV, we'll flatten the data (excluding nested comments)
            flattened_posts = []
            for post in posts:
                post_copy = post.copy()
                # Remove nested structures for CSV
                post_copy.pop('comments', None)
                post_copy.pop('total_comments_collected', None)
                flattened_posts.append(post_copy)
            
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=flattened_posts[0].keys())
                writer.writeheader()
                writer.writerows(flattened_posts)
    
    elif format_type == 'txt':
        filepath = f"{filename}_{timestamp}.txt"
        with open(filepath, 'w', encoding='utf-8') as f:
            for i, post in enumerate(posts, 1):
                f.write(f"Post {i}:\n")
                f.write(f"Title: {post['title']}\n")
                f.write(f"Score: {post['score']}\n")
                f.write(f"Comments: {post['num_comments']}\n")
                f.write(f"URL: {post['url']}\n")
                f.write(f"ID: {post['id']}\n")
                if 'author' in post:
                    f.write(f"Author: {post['author']}\n")
                if 'created_date' in post:
                    f.write(f"Created: {post['created_date']}\n")
                f.write("-" * 50 + "\n")
    
    print(f"Saved {len(posts)} posts to {filepath}")
    return filepath

def save_network_data(network_data, base_filename="reddit_network"):
    """
    Save interaction network data in multiple formats for analysis.
    
    Args:
        network_data: Dictionary containing graph, edges, and stats from build_interaction_network()
        base_filename: Base name for output files
    
    Returns:
        Dictionary with paths to all saved files
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    saved_files = {}
    
    # 1. Save NetworkX graph as GraphML (can be opened in Gephi, Cytoscape, etc.)
    # GraphML doesn't support list attributes, so we need to create a clean copy
    graph_file = f"{base_filename}_graph_{timestamp}.graphml"
    G_clean = network_data['graph'].copy()
    
    # Remove 'interactions' attribute from edges (it's a list, not supported by GraphML)
    for u, v, data in G_clean.edges(data=True):
        if 'interactions' in data:
            del data['interactions']
    
    nx.write_graphml(G_clean, graph_file)
    saved_files['graph'] = graph_file
    print(f"Saved NetworkX graph to {graph_file}")
    
    # 2. Save NetworkX graph as pickle (for Python analysis)
    pickle_file = f"{base_filename}_graph_{timestamp}.gpickle"
    with open(pickle_file, 'wb') as f:
        pickle.dump(network_data['graph'], f)
    saved_files['pickle'] = pickle_file
    print(f"Saved graph pickle to {pickle_file}")
    
    # 3. Save reply edges as CSV
    reply_edges_file = f"{base_filename}_reply_edges_{timestamp}.csv"
    if network_data['reply_edges']:
        with open(reply_edges_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['from', 'to', 'type', 'post_id', 'comment_id', 'score', 'timestamp']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(network_data['reply_edges'])
        saved_files['reply_edges'] = reply_edges_file
        print(f"Saved {len(network_data['reply_edges'])} reply edges to {reply_edges_file}")
    
    # 4. Save co-participation edges as CSV
    copart_edges_file = f"{base_filename}_coparticipation_edges_{timestamp}.csv"
    if network_data['co_participation_edges']:
        with open(copart_edges_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['from', 'to', 'type', 'post_id']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(network_data['co_participation_edges'])
        saved_files['coparticipation_edges'] = copart_edges_file
        print(f"Saved {len(network_data['co_participation_edges'])} co-participation edges to {copart_edges_file}")
    
    # 5. Save network statistics as JSON
    stats_file = f"{base_filename}_stats_{timestamp}.json"
    stats = {
        **network_data['stats'],
        'graph_metrics': {
            'density': nx.density(network_data['graph']),
            'num_weakly_connected_components': nx.number_weakly_connected_components(network_data['graph']),
            'num_strongly_connected_components': nx.number_strongly_connected_components(network_data['graph']),
        },
        'top_users_by_degree': _get_top_nodes_by_degree(network_data['graph'], top_n=20),
        'timestamp': timestamp
    }
    
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2)
    saved_files['stats'] = stats_file
    print(f"Saved network statistics to {stats_file}")
    
    # 6. Save user participation summary
    user_summary_file = f"{base_filename}_user_summary_{timestamp}.csv"
    user_summary = []
    for user, posts in network_data['user_posts'].items():
        if user != '[deleted]':
            user_summary.append({
                'user': user,
                'num_posts_participated': len(posts),
                'in_degree': network_data['graph'].in_degree(user) if network_data['graph'].has_node(user) else 0,
                'out_degree': network_data['graph'].out_degree(user) if network_data['graph'].has_node(user) else 0
            })
    
    user_summary.sort(key=lambda x: x['num_posts_participated'], reverse=True)
    
    with open(user_summary_file, 'w', newline='', encoding='utf-8') as f:
        if user_summary:
            writer = csv.DictWriter(f, fieldnames=['user', 'num_posts_participated', 'in_degree', 'out_degree'])
            writer.writeheader()
            writer.writerows(user_summary)
    saved_files['user_summary'] = user_summary_file
    print(f"Saved user summary to {user_summary_file}")
    
    return saved_files

def _get_top_nodes_by_degree(graph, top_n=10):
    """Get top nodes by total degree (in + out)"""
    degree_dict = {node: graph.in_degree(node) + graph.out_degree(node) 
                   for node in graph.nodes() if node != '[deleted]'}
    sorted_nodes = sorted(degree_dict.items(), key=lambda x: x[1], reverse=True)
    return [{'user': node, 'degree': degree} for node, degree in sorted_nodes[:top_n]]

def create_graph(posts):
    """Create a network graph from posts"""
    G = nx.DiGraph()
    for post in posts:
        G.add_node(post['id'], 
                  title=post['title'], 
                  score=post['score'],
                  num_comments=post['num_comments'])
    return G

def print_posts(posts):
    """Print posts in a readable format"""
    if not PRINT_RESULTS:
        return
        
    print(f"\n--- Found {len(posts)} posts ---\n")
    for i, post in enumerate(posts, 1):
        print(f"Post {i}:")
        print(f"  Title: {post['title']}")
        print(f"  Score: {post['score']}")
        print(f"  Comments: {post['num_comments']}")
        print(f"  Interaction Score: {post['interaction_score']}")
        if 'author' in post:
            print(f"  Author: {post['author']}")
        if 'created_date' in post:
            print(f"  Created: {post['created_date']}")
        if 'subreddit' in post:
            print(f"  Subreddit: r/{post['subreddit']}")
        print(f"  URL: {post['url']}")
        print(f"  ID: {post['id']}")
        print("-" * 50)

def print_config_summary():
    """Print current configuration settings"""
    print("=== CURRENT CONFIGURATION ===")
    if MULTI_SUBREDDIT:
        print(f"Subreddits: {', '.join(SUBREDDIT_LIST)}")
    else:
        print(f"Subreddit: r/{SUBREDDIT_NAME}")
    print(f"Number of posts: {NUM_POSTS}")
    print(f"Sort by: {SORT_BY}")
    print(f"Time filter: {TIME_FILTER}")
    print(f"Verbose output: {VERBOSE}")
    print(f"Save to file: {SAVE_TO_FILE}")
    if SAVE_TO_FILE:
        print(f"Output format: {OUTPUT_FORMAT}")
    print("=" * 30)

if __name__ == "__main__":
    print_config_summary()
    
    try:
        # Get posts based on configuration
        if MULTI_SUBREDDIT:
            posts = get_multi_subreddit_data()
        else:
            # Get posts with comments if network analysis is enabled
            include_comments = INCLUDE_COMMENTS if 'INCLUDE_COMMENTS' in dir() else True
            max_depth = MAX_COMMENT_DEPTH if 'MAX_COMMENT_DEPTH' in dir() else 10
            posts = get_reddit_data(include_comments=include_comments, max_comment_depth=max_depth)
        
        # Print results if enabled
        print_posts(posts)
        
        # Save posts to file if enabled
        if SAVE_TO_FILE and posts:
            save_posts_to_file(posts)
        
        # Build and save interaction network if enabled
        build_network = BUILD_NETWORK if 'BUILD_NETWORK' in dir() else False
        save_network = SAVE_NETWORK if 'SAVE_NETWORK' in dir() else False
        
        if build_network and posts:
            print("\n--- Building Interaction Network ---")
            network_data = build_interaction_network(posts)
            
            print(f"\nNetwork Statistics:")
            print(f"  Total users: {network_data['stats']['num_users']}")
            print(f"  Reply interactions: {network_data['stats']['num_reply_edges']}")
            print(f"  Co-participation edges: {network_data['stats']['num_co_participation_edges']}")
            
            if save_network:
                print("\n--- Saving Network Data ---")
                saved_files = save_network_data(network_data)
                print(f"\nNetwork analysis complete! Saved {len(saved_files)} files.")
        
        print(f"\nScraping completed! Found {len(posts)} posts.")
        
    except Exception as e:
        print(f"Error during scraping: {e}")
        print("Check your Reddit API credentials and network connection.")
        import traceback
        traceback.print_exc()