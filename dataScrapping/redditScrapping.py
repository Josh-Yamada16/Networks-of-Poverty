import praw
import requests
import networkx as nx

reddit = praw.Reddit(client_id='qThRoFaCe_iXAwY7CDOoLg',
                     client_secret='ch-zv9PCgeXqCMcfQ9CKLqvbyxUmuA',
                     user_agent='poverty_research_script')

def get_reddit_data(subreddit_name, num_posts):
    subreddit = reddit.subreddit(subreddit_name)
    posts = []
    for post in subreddit.top(limit=num_posts):
        posts.append({
            'title': post.title,
            'score': post.score,
            'id': post.id,
            'url': post.url,
            'num_comments': post.num_comments
        })
    return posts

def create_graph(posts):
    G = nx.Graph()
    for post in posts:
        G.add_node(post['id'], title=post['title'], score=post['score'])
    return G