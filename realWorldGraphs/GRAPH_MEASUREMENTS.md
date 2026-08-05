# Graph Measurements Guide

This project now includes a set of network measurements in `network_measures.py`. This file explains what each measurement means and how to interpret the results when comparing a real social network to common graph models.

## Basic Size and Connectivity

### Node count
How many nodes are in the graph. For this project, nodes usually represent streamers or accounts in the Twitch network.

### Edge count
How many connections exist between nodes. More edges usually means the network is more interconnected.

### Density
The fraction of possible edges that actually exist.

- High density: the graph is relatively crowded.
- Low density: the graph is sparse, which is common in real social networks.

### Is connected
Whether every node can reach every other node by some path.

- Connected: the graph is one large component.
- Not connected: the graph has separate clusters or isolated groups.

### Largest component fraction
The share of nodes contained in the largest connected component.

- Close to 1.0: most of the network belongs to one main group.
- Much smaller: the graph is fragmented into multiple pieces.

## Degree-Based Measures

### Average degree
The average number of connections per node.

- Higher values suggest more interaction overall.
- Lower values suggest a more sparse or selective network.

### Degree standard deviation
How spread out the node degrees are.

- High standard deviation: some nodes are hubs while many others have few links.
- Low standard deviation: nodes have more similar connectivity.

### Min degree / max degree
The smallest and largest number of connections for any node.

- A very large max degree compared to the average often indicates hub nodes.

### Degree sequence
A sorted list of node degrees.

- A steep drop-off often suggests a hub-dominated network.
- A flatter list suggests a more even structure.

## Clustering and Local Cohesion

### Average clustering
The average probability that two neighbors of a node are also connected to each other.

- High clustering: the graph has tightly knit local groups.
- Low clustering: the graph is more random or tree-like.

### Transitivity
A global version of clustering based on triangles.

- High transitivity means triangles are common.
- Social networks often have higher transitivity than random graphs.

### Local clustering mean
The average of the clustering coefficient across nodes.

- Similar to average clustering, but useful as a node-level summary.

### Top clustering nodes
The nodes with the strongest local triangle structure.

- These nodes sit in dense neighborhoods or close communities.

## Paths and Reachability

### Average shortest path length
The average number of steps needed to get from one node to another, usually measured on the largest connected component.

- Small values: the graph is compact and information can travel quickly.
- Large values: the graph is stretched out or fragmented.

### Diameter
The longest shortest path between any two nodes in the largest connected component.

- Smaller diameter: tighter network.
- Larger diameter: more chain-like or spread out structure.

### Radius
The minimum eccentricity of the graph.

- Helps describe how centrally located the best-connected node is.

## Assortativity

### Degree assortativity
Measures whether high-degree nodes tend to connect to other high-degree nodes.

- Positive assortativity: hubs link to hubs.
- Negative assortativity: hubs mostly connect to low-degree nodes.
- Near zero: little degree preference.

Many social networks are mildly assortative, but real online follower graphs can be negative depending on platform behavior.

## Centrality Measures

### Degree centrality
Which nodes have the most direct connections, normalized by network size.

- High degree centrality: a node is locally popular or active.

### Betweenness centrality
Which nodes sit on many shortest paths between other nodes.

- High betweenness: a node may act as a bridge or broker between groups.

### Closeness centrality
How quickly a node can reach all other nodes through shortest paths.

- High closeness: a node is well positioned in the network.

### Eigenvector centrality
Measures whether a node is connected to other important nodes, not just many nodes.

- High eigenvector centrality: a node is influential in a more global sense.

## Community Structure

### Community count
How many clusters the greedy modularity method finds.

- More communities usually means a more segmented network.

### Modularity
How strongly separated those communities are.

- Higher modularity: clearer group structure.
- Lower modularity: groups are less distinct.

### Community sizes
The sizes of the detected communities.

- A few very large communities may indicate a core-periphery structure.
- Many small communities may indicate a highly fragmented network.

## Reference Graph Comparison

### Erdos-Renyi
A random graph model where each possible edge appears with equal probability.

- Best when the real graph is fairly random and low-structure.

### Watts-Strogatz
A small-world model with high clustering and short paths.

- Best when the graph has local clusters but still stays well connected overall.

### Barabasi-Albert
A scale-free model that grows by preferential attachment.

- Best when a few hubs dominate the network and the degree distribution is very uneven.

### Best match
The model with the closest summary-statistic profile to the observed graph.

- This is a heuristic comparison, not a proof that the graph literally came from that model.

## How to Read the Results

If the graph has:

- high clustering and short path length, it may look small-world
- a very skewed degree distribution and a few major hubs, it may look scale-free
- low clustering and weak community structure, it may look more random
- strong modularity and obvious clusters, it may be a community-driven social graph

In practice, social networks often mix several of these patterns, so the goal is usually to find the closest overall description rather than force the graph into a single perfect category.