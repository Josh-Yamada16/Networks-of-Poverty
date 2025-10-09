import praw
import requests
import networkx as nx
import json
import csv
import time
from datetime import datetime
from config import *  # Import all configuration settings

# Initialize Reddit API with credentials from config
reddit = praw.Reddit(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    user_agent=USER_AGENT
)

def get_reddit_data(subreddit_name=None, num_posts=None, sort_by=None, verbose=None, time_filter=None):
    """
    Get Reddit posts with parameters from config file or overrides
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
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=posts[0].keys())
                writer.writeheader()
                writer.writerows(posts)
    
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
            posts = get_reddit_data()
        
        # Print results if enabled
        print_posts(posts)
        
        # Save to file if enabled
        if SAVE_TO_FILE and posts:
            save_posts_to_file(posts)
        
        print(f"\nScraping completed! Found {len(posts)} posts.")
        
    except Exception as e:
        print(f"Error during scraping: {e}")
        print("Check your Reddit API credentials and network connection.")