# Reddit Social Network Analysis

Enhanced Reddit scraper that captures user interactions and builds social networks based on comment replies and co-participation.

## 🎯 Overview

This enhanced scraper goes beyond collecting posts to capture the **full interaction network** between Reddit users. It tracks:

1. **Direct Replies**: When User A replies to User B's comment
2. **Co-Participation**: When multiple users comment on the same post
3. **Comment Hierarchies**: Full nested reply trees (not just top-level comments)

## 🚀 Quick Start

### Basic Usage

```python
import reddit_scraper as rs

# 1. Scrape posts with full comment trees
posts = rs.get_reddit_data(
    subreddit_name='povertyfinance',
    num_posts=10,
    include_comments=True,  # Enable comment collection
    max_comment_depth=10,   # Depth of reply tree
    verbose=True
)

# 2. Build interaction network
network_data = rs.build_interaction_network(posts)

# 3. Save network data
rs.save_network_data(network_data, base_filename="my_network")
```

### Using Configuration File

Edit `config.py`:

```python
# Enable network analysis
INCLUDE_COMMENTS = True
MAX_COMMENT_DEPTH = 10
BUILD_NETWORK = True
SAVE_NETWORK = True
```

Then run:

```bash
python reddit_scraper.py
```

## 📊 What Gets Collected

### Post Data
- Title, score, URL, ID
- Author, creation time
- Number of comments
- Post text (optional)

### Comment Data (New!)
- **Full comment trees** with nested replies
- Comment author, text, score
- Parent-child relationships (`parent_id`)
- Depth in reply tree
- Timestamp

### Network Data (New!)
- **Reply edges**: User A → User B (directed)
- **Co-participation edges**: Users who commented on same post
- **User statistics**: Activity levels, degree centrality
- **Graph metrics**: Density, connected components

## 📁 Output Files

When network analysis is enabled, you'll get:

| File | Description | Use Case |
|------|-------------|----------|
| `*_graph.graphml` | NetworkX graph | Open in Gephi/Cytoscape for visualization |
| `*_graph.gpickle` | Pickled NetworkX graph | Load in Python for analysis |
| `*_reply_edges.csv` | Reply interactions | Analyze who replies to whom |
| `*_coparticipation_edges.csv` | Co-participation | Find users in same discussions |
| `*_user_summary.csv` | User activity stats | Identify most active users |
| `*_stats.json` | Network metrics | Overall network statistics |

## 🔍 Understanding the Network

### Reply Network (Directed)

```
User A --replies-to--> User B
```

- **Direction matters**: A → B means A replied to B
- **Edge weight**: Number of times A replied to B
- **Use cases**: 
  - Find influential users (high in-degree)
  - Identify conversation initiators (high out-degree)
  - Detect help-seeking patterns

### Co-Participation Network (Undirected)

```
User A --discussed-with-- User B
(both commented on Post X)
```

- **No direction**: Mutual participation
- **Use cases**:
  - Find communities of interest
  - Identify users with shared concerns
  - Detect discussion clusters

## 📈 Network Analysis Examples

### Example 1: Find Most Influential Users

```python
import networkx as nx

# Load saved network
G = nx.read_gpickle('reddit_network_graph_*.gpickle')

# Get users by reply count (in-degree)
influential = sorted(
    [(node, G.in_degree(node)) for node in G.nodes()],
    key=lambda x: x[1],
    reverse=True
)[:10]

for user, replies in influential:
    print(f"{user}: {replies} replies received")
```

### Example 2: Find Connected Communities

```python
# Find weakly connected components
components = list(nx.weakly_connected_components(G))

print(f"Found {len(components)} communities")
for i, component in enumerate(sorted(components, key=len, reverse=True)[:5]):
    print(f"Community {i+1}: {len(component)} users")
```

### Example 3: Analyze Interaction Patterns

```python
import pandas as pd

# Load reply edges
edges_df = pd.read_csv('reddit_network_reply_edges_*.csv')

# Most active repliers
top_repliers = edges_df['from'].value_counts().head(10)

# Most replied-to users
most_replied = edges_df['to'].value_counts().head(10)

# Average comment score by user
avg_scores = edges_df.groupby('from')['score'].mean()
```

## 🛠️ Configuration Options

### In `config.py`:

```python
# Comment Collection
INCLUDE_COMMENTS = True       # Fetch full comment trees
MAX_COMMENT_DEPTH = 10        # How deep to traverse replies

# Network Building
BUILD_NETWORK = True          # Build interaction network
SAVE_NETWORK = True           # Save network files

# Network Types
INCLUDE_REPLY_NETWORK = True          # Direct reply edges
INCLUDE_COPARTICIPATION_NETWORK = True # Co-participation edges
```

### In Code:

```python
posts = rs.get_reddit_data(
    include_comments=True,     # Override config
    max_comment_depth=5        # Limit depth
)
```

## 🎨 Visualization

### Option 1: Python (Small Networks)

```python
import networkx as nx
import matplotlib.pyplot as plt

G = nx.read_gpickle('network.gpickle')

# Get largest component
largest = max(nx.weakly_connected_components(G), key=len)
subgraph = G.subgraph(largest)

# Visualize
nx.draw_spring(subgraph, with_labels=True)
plt.savefig('network.png')
```

### Option 2: Gephi (Recommended for Large Networks)

1. Open Gephi
2. File → Open → Select `*_graph.graphml`
3. Apply layout (ForceAtlas2 recommended)
4. Color nodes by degree
5. Size nodes by influence
6. Export visualization

## 📚 Network Metrics Explained

| Metric | What It Means |
|--------|---------------|
| **In-Degree** | Number of replies a user received (influence) |
| **Out-Degree** | Number of replies a user sent (engagement) |
| **Density** | How connected the network is (0-1) |
| **Components** | Separate conversation groups |
| **Centrality** | How "central" a user is to discussions |

## ⚠️ Important Notes

### Reddit API Limitations

1. **No upvote details**: API only shows total score, not individual upvoters
2. **Comment limits**: Very large threads may hit API limits
3. **Rate limiting**: Use `REQUEST_DELAY` to avoid being throttled
4. **Deleted users**: Shown as `[deleted]`, excluded from network

### Performance Tips

1. **Start small**: Test with `num_posts=5` first
2. **Limit depth**: `max_comment_depth=5` for faster scraping
3. **Filter posts**: Use `MIN_COMMENTS` to focus on active discussions
4. **Use delays**: Set `REQUEST_DELAY=2` for reliability

## 🔬 Research Use Cases

### Poverty & Financial Hardship Networks

```python
# Analyze help-seeking behavior
posts = rs.get_reddit_data(
    subreddit_name='povertyfinance',
    num_posts=50,
    sort_by='comments',
    time_filter='month',
    include_comments=True
)

network = rs.build_interaction_network(posts)

# Questions you can answer:
# - Who are the most helpful users? (high in-degree)
# - Are there support communities? (connected components)
# - How do help requests spread? (path analysis)
# - What topics connect users? (combine with text analysis)
```

### Multi-Subreddit Comparison

```python
subreddits = ['povertyfinance', 'assistance', 'homeless']
networks = {}

for sub in subreddits:
    posts = rs.get_reddit_data(subreddit_name=sub, num_posts=20)
    networks[sub] = rs.build_interaction_network(posts)

# Compare network structures across communities
```

## 📖 Example Workflow

See `network_analysis_example.py` for a complete working example:

```bash
python network_analysis_example.py
```

This will:
1. Scrape 5 posts from r/povertyfinance
2. Build interaction network
3. Calculate network metrics
4. Save all network data
5. Create visualization (if network is small enough)

## 🤝 Contributing

Have ideas for new network features? Want to add:
- Sentiment analysis on edges
- Temporal network evolution
- Community detection algorithms
- Cross-subreddit network linking

Open an issue or submit a PR!

## 📄 License

Same as parent project.

## 🆘 Troubleshooting

**"Comments not loading"**
- Check `INCLUDE_COMMENTS = True` in config
- Verify Reddit API credentials

**"Network too large to visualize"**
- Use Gephi for large networks
- Filter to largest component
- Increase `MIN_COMMENTS` threshold

**"API rate limit exceeded"**
- Increase `REQUEST_DELAY`
- Reduce `num_posts`
- Wait and try again later

**"No edges in network"**
- Check that posts have comments
- Verify `max_comment_depth > 0`
- Try more active subreddits
