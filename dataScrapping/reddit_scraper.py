import praw
import requests
import networkx as nx
import json
import csv
import pickle
import time
import os
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

def build_interaction_network(posts_with_comments, edge_strength_threshold=0.0):
    """
    Build a user interaction network from posts and comments with relationship strength metrics.
    Creates edges between users based on:
    1. Direct replies (User A replies to User B)
    2. Co-participation (Users comment on the same post)
    3. Mutual interactions (bidirectional engagement)
    4. Sustained engagement (shared posts over time)
    5. Common neighbors (shared connections)
    
    Args:
        posts_with_comments: List of posts with full comment trees
        edge_strength_threshold: Minimum edge strength to include (default: 0.0, keep all)
    
    Returns:
        Dictionary containing NetworkX graph with enhanced edge attributes and relationship metrics
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
                        'timestamp': comment_data['created_utc'],
                        'depth': comment_data.get('depth', 0)
                    })
                else:
                    G.add_edge(author, parent_author, 
                             weight=1,
                             edge_type='reply',
                             relationship_strength=0,  # Will be calculated after all edges added
                             interactions=[{
                                 'type': 'reply',
                                 'post_id': post_id,
                                 'comment_id': comment_data['id'],
                                 'timestamp': comment_data['created_utc'],
                                 'depth': comment_data.get('depth', 0)
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
    
    # Calculate relationship strength metrics
    mutual_interactions = []  # Bidirectional edges
    strong_relationships = []  # High strength edges
    user_metrics = {}  # Per-user helper/helped ratios
    
    # First pass: calculate relationship strength for each edge using 5-factor model
    for edge in G.edges():
        user1, user2 = edge
        edge_data = G[user1][user2]
        
        # Factor 1: Base strength from interaction count (weight)
        strength = edge_data.get('weight', 1)
        
        # Factor 2: Mutual interaction bonus (1.5x if bidirectional)
        if G.has_edge(user2, user1):
            strength *= 1.5
        
        # Factor 3: Sustained engagement - shared posts over time
        # Count how many distinct posts this edge appears in
        interactions = edge_data.get('interactions', [])
        shared_posts = len(set(i.get('post_id') for i in interactions if i.get('post_id')))
        sustained_engagement_bonus = shared_posts * 0.5
        strength += sustained_engagement_bonus
        
        # Factor 4: Common neighbors bonus
        # Find users that both user1 and user2 interact with
        user1_neighbors = set(G.successors(user1)) | set(G.predecessors(user1))
        user2_neighbors = set(G.successors(user2)) | set(G.predecessors(user2))
        common_neighbors = len(user1_neighbors & user2_neighbors)
        common_neighbors_bonus = common_neighbors * 0.3
        strength += common_neighbors_bonus
        
        # Factor 5: Conversation depth - based on max depth in replies
        max_depth = 0
        for interaction in interactions:
            if 'depth' in interaction:
                max_depth = max(max_depth, interaction.get('depth', 0))
        # Deeper conversations indicate more engagement
        depth_bonus = max(0, (max_depth - 1) * 0.2)  # Start bonus at depth 2
        strength += depth_bonus
        
        # Set the relationship_strength attribute with full 5-factor calculation
        G[user1][user2]['relationship_strength'] = strength
        G[user1][user2]['strength_components'] = {
            'base_weight': edge_data.get('weight', 1),
            'mutual_bonus': 0.5 * edge_data.get('weight', 1) if G.has_edge(user2, user1) else 0,
            'sustained_engagement': sustained_engagement_bonus,
            'common_neighbors': common_neighbors_bonus,
            'conversation_depth': depth_bonus
        }
    
    # Second pass: build user metrics
    for user in G.nodes():
        out_degree = G.out_degree(user)  # Posts to others (helping)
        in_degree = G.in_degree(user)    # Receives posts from others (receiving help)
        
        # Helper/helped ratio: how often user initiates vs receives
        total_interactions = out_degree + in_degree
        if total_interactions > 0:
            helper_ratio = out_degree / total_interactions
        else:
            helper_ratio = 0.0
        
        user_metrics[user] = {
            'out_degree': out_degree,
            'in_degree': in_degree,
            'helper_ratio': helper_ratio,
            'total_interactions': total_interactions,
            'helped': out_degree,  # Alias for out_degree
            'received_help': in_degree  # Alias for in_degree
        }
        
        # Add attributes to graph nodes for easy access
        G.nodes[user]['helper_ratio'] = helper_ratio
        G.nodes[user]['helped_count'] = out_degree
        G.nodes[user]['received_help_count'] = in_degree
    
    # Find mutual interactions (bidirectional edges)
    for edge in G.edges():
        user1, user2 = edge
        if G.has_edge(user2, user1):
            # Avoid duplicates by only counting when user1 < user2 alphabetically
            if user1 < user2:
                mutual_interactions.append({
                    'users': (user1, user2),
                    'mutual': True
                })
    
    # Find strong relationships (strength > threshold)
    for edge in G.edges(data=True):
        user1, user2 = edge[0], edge[1]
        edge_data = edge[2]
        
        strength = edge_data.get('relationship_strength', 0)
        if strength > edge_strength_threshold:
            strong_relationships.append({
                'users': (user1, user2),
                'strength': strength,
                'interactions': len(edge_data.get('interactions', []))
            })
    
    return {
        'graph': G,
        'reply_edges': edges,
        'co_participation_edges': co_participation_edges,
        'user_posts': dict(user_posts),
        'mutual_interactions': mutual_interactions,
        'user_metrics': user_metrics,
        'interaction_strength': {edge: G[edge[0]][edge[1]].get('relationship_strength', 0) for edge in G.edges()},
        'stats': {
            'num_users': G.number_of_nodes(),
            'num_reply_edges': len(edges),
            'num_co_participation_edges': len(co_participation_edges),
            'num_mutual_pairs': len(mutual_interactions),
            'num_strong_relationships': len(strong_relationships)
        }
    }

def _get_post_participants(user_posts):
    """Helper function to invert user_posts mapping to post_participants"""
    post_participants = defaultdict(set)
    for user, posts in user_posts.items():
        for post_id in posts:
            post_participants[post_id].add(user)
    return post_participants

def get_cache_filepath(subreddit_name, num_posts, sort_by, time_filter, include_comments):
    """
    Generate a consistent cache filename based on scraping parameters.
    
    Args:
        subreddit_name: Name of subreddit
        num_posts: Number of posts
        sort_by: Sorting method
        time_filter: Time filter
        include_comments: Whether comments are included
    
    Returns:
        Path to cache file
    """
    cache_dir = os.path.join(os.path.dirname(__file__), 'cached_data')
    os.makedirs(cache_dir, exist_ok=True)
    
    comments_suffix = "_with_comments" if include_comments else "_no_comments"
    filename = f"{subreddit_name}_{sort_by}_{time_filter}_{num_posts}posts{comments_suffix}.json"
    
    return os.path.join(cache_dir, filename)

def save_posts_cache(posts, subreddit_name, num_posts, sort_by, time_filter, include_comments):
    """
    Save scraped posts to cache file.
    
    Args:
        posts: List of post dictionaries
        subreddit_name: Name of subreddit
        num_posts: Number of posts
        sort_by: Sorting method
        time_filter: Time filter
        include_comments: Whether comments are included
    
    Returns:
        Path to saved cache file
    """
    cache_file = get_cache_filepath(subreddit_name, num_posts, sort_by, time_filter, include_comments)
    
    cache_data = {
        'metadata': {
            'subreddit': subreddit_name,
            'num_posts': num_posts,
            'sort_by': sort_by,
            'time_filter': time_filter,
            'include_comments': include_comments,
            'cached_at': datetime.now().isoformat(),
            'total_posts': len(posts)
        },
        'posts': posts
    }
    
    with open(cache_file, 'w', encoding='utf-8') as f:
        json.dump(cache_data, f, indent=2, ensure_ascii=False)
    
    # Calculate file size
    file_size = os.path.getsize(cache_file) / (1024 * 1024)  # MB
    print(f"Cached {len(posts)} posts to: {cache_file}")
    print(f"Cache file size: {file_size:.2f} MB")
    
    return cache_file

def load_posts_cache(subreddit_name, num_posts, sort_by, time_filter, include_comments, max_age_days=None):
    """
    Load posts from cache if available and not too old.
    
    Args:
        subreddit_name: Name of subreddit
        num_posts: Number of posts
        sort_by: Sorting method
        time_filter: Time filter
        include_comments: Whether comments are included
        max_age_days: Maximum age of cache in days (None = no limit)
    
    Returns:
        List of posts if cache exists and is valid, None otherwise
    """
    cache_file = get_cache_filepath(subreddit_name, num_posts, sort_by, time_filter, include_comments)
    
    if not os.path.exists(cache_file):
        return None
    
    # Check cache age if max_age_days specified
    if max_age_days is not None:
        file_mod_time = datetime.fromtimestamp(os.path.getmtime(cache_file))
        age_days = (datetime.now() - file_mod_time).days
        if age_days > max_age_days:
            print(f"Cache file is {age_days} days old (max: {max_age_days}). Re-scraping...")
            return None
    
    try:
        with open(cache_file, 'r', encoding='utf-8') as f:
            cache_data = json.load(f)
        
        metadata = cache_data.get('metadata', {})
        posts = cache_data.get('posts', [])
        
        file_size = os.path.getsize(cache_file) / (1024 * 1024)  # MB
        print(f"Loaded {len(posts)} posts from cache: {cache_file}")
        print(f"Cache created: {metadata.get('cached_at', 'unknown')}")
        print(f"Cache file size: {file_size:.2f} MB")
        
        return posts
    except Exception as e:
        print(f"Error loading cache: {e}")
        return None

def get_reddit_data(subreddit_name=None, num_posts=None, sort_by=None, verbose=None, time_filter=None, include_comments=True, max_comment_depth=10, use_cache=True, max_cache_age_days=None, force_refresh=False):
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
        use_cache: Whether to use cached data if available (default: True)
        max_cache_age_days: Maximum age of cache in days (None = no limit)
        force_refresh: Force re-scraping even if cache exists (default: False)
    
    Returns:
        List of posts with optional comment trees
    """
    # Use config defaults if not specified
    subreddit_name = subreddit_name or SUBREDDIT_NAME
    num_posts = num_posts or NUM_POSTS
    sort_by = sort_by or SORT_BY
    verbose = verbose if verbose is not None else VERBOSE
    time_filter = time_filter or TIME_FILTER
    
    # Try to load from cache first (unless force_refresh is True)
    if use_cache and not force_refresh:
        cached_posts = load_posts_cache(subreddit_name, num_posts, sort_by, time_filter, 
                                       include_comments, max_cache_age_days)
        if cached_posts is not None:
            return cached_posts
    
    # If no cache or force_refresh, scrape from Reddit
    if verbose:
        if force_refresh:
            print("Force refresh enabled - scraping fresh data from Reddit...")
        else:
            print("No valid cache found - scraping from Reddit...")
    
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
                # Handle Unicode properly for console output
                title = post.title[:50]
                try:
                    print(f"  Fetching {post.num_comments} comments for: {title}...")
                except UnicodeEncodeError:
                    # Fallback for encoding errors in Windows console
                    print(f"  Fetching {post.num_comments} comments for: [post with unicode characters]")
            
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
    
    # Cache the scraped data if use_cache is True
    if use_cache:
        try:
            save_posts_cache(posts, subreddit_name, num_posts, sort_by, time_filter, include_comments)
        except Exception as e:
            print(f"Warning: Could not save cache: {e}")
    
    # Print with verbose option
    if verbose:
        print(f"Found {len(posts)} posts after filtering")
        for i, post_data in enumerate(posts, 1):
            title = post_data['title']
            try:
                if len(title) > 60:
                    print(f"Post {i}: {title[:60]}...")
                else:
                    print(f"Post {i}: {title}")
                print(f"  Score: {post_data['score']}, Comments: {post_data['num_comments']}, Interaction: {post_data['interaction_score']}")
            except UnicodeEncodeError:
                # Fallback for encoding errors in Windows console
                print(f"Post {i}: [post with unicode characters]")
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

def save_network_data(network_data, base_filename="reddit_network", 
                     save_pickle=True, save_reply_edges=True, 
                     save_coparticipation=True, save_stats=True,
                     save_graphml=True):
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
    if save_graphml:
        # GraphML doesn't support list attributes, so we need to create a clean copy
        graph_file = f"{base_filename}_graph_{timestamp}.graphml"
        G_clean = network_data['graph'].copy()
        
        # Remove attributes not supported by GraphML (lists, dicts, etc.)
        for u, v, data in G_clean.edges(data=True):
            if 'interactions' in data:
                del data['interactions']
            if 'strength_components' in data:
                del data['strength_components']
        
        nx.write_graphml(G_clean, graph_file)
        saved_files['graph'] = graph_file
        print(f"Saved NetworkX graph to {graph_file}")
    
    # 2. Save NetworkX graph as pickle (for Python analysis)
    if save_pickle:
        pickle_file = f"{base_filename}_graph_{timestamp}.gpickle"
        with open(pickle_file, 'wb') as f:
            pickle.dump(network_data['graph'], f)
        saved_files['pickle'] = pickle_file
        print(f"Saved graph pickle to {pickle_file}")
    
    # 3. Save reply edges as CSV
    if save_reply_edges and network_data['reply_edges']:
        reply_edges_file = f"{base_filename}_reply_edges_{timestamp}.csv"
        with open(reply_edges_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['from', 'to', 'type', 'post_id', 'comment_id', 'score', 'timestamp']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(network_data['reply_edges'])
        saved_files['reply_edges'] = reply_edges_file
        print(f"Saved {len(network_data['reply_edges'])} reply edges to {reply_edges_file}")
    
    # 4. Save co-participation edges as CSV
    if save_coparticipation and network_data['co_participation_edges']:
        copart_edges_file = f"{base_filename}_coparticipation_edges_{timestamp}.csv"
        with open(copart_edges_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['from', 'to', 'type', 'post_id']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(network_data['co_participation_edges'])
        saved_files['coparticipation_edges'] = copart_edges_file
        print(f"Saved {len(network_data['co_participation_edges'])} co-participation edges to {copart_edges_file}")
    
    # 5. Save network statistics as JSON
    if save_stats:
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
    
    # 6. Save user participation summary (Note: not controlled by config flags)
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