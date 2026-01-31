import networkx as nx
import numpy as np
from typing import List, Dict, Tuple
from node import Node

class CentralInstitutionNetwork:
    """Manages the network with central institution and emergent peer connections."""
    
    def __init__(self, num_nodes: int, central_id: str = "HUB",
                 token_threshold: int = 5, connection_prob_base: float = 0.1,
                 connection_prob_max: float = 0.9, accumulation_rate: float = 0.2,
                 seed: int = 42):
        """
        Initialize the network.
        
        Args:
            num_nodes: Number of peripheral nodes
            central_id: Name of central institution
            token_threshold: Tokens needed for connection probability
            connection_prob_base: Base connection probability
            connection_prob_max: Maximum connection probability
            accumulation_rate: Token accumulation rate for probability
            seed: Random seed
        """
        self.rng = np.random.default_rng(seed)
        self.central_id = central_id
        self.num_nodes = num_nodes
        
        # Create nodes
        self.nodes: Dict[str, Node] = {}
        for i in range(num_nodes):
            node_id = f"Node_{i}"
            self.nodes[node_id] = Node(
                node_id=node_id,
                token_threshold=token_threshold,
                connection_prob_base=connection_prob_base,
                connection_prob_max=connection_prob_max,
                accumulation_rate=accumulation_rate
            )
        
        # Initialize NetworkX graph: star topology
        self.graph = nx.Graph()
        self.graph.add_node(self.central_id, node_type="central")
        
        for node_id in self.nodes.keys():
            self.graph.add_node(node_id, node_type="peripheral")
            self.graph.add_edge(self.central_id, node_id)  # All connected to hub
    
    def distribute_tokens(self, num_tokens: int) -> None:
        """
        Central institution distributes tokens to peripheral nodes.
        Additionally, some tokens may be exchanged between nodes at the hub
        (simulating the hub as a meeting point where nodes can encounter each other).
        """
        for _ in range(num_tokens):
            # Hub sends token to a random peripheral node
            recipient = self.rng.choice(list(self.nodes.keys()))
            self.nodes[recipient].receive_token(self.central_id)
        
        # Simulate tokens exchanged between nodes at the hub (peer encounters at hub)
        # Each iteration, there's a chance random pairs of nodes send tokens to each other
        num_nodes_list = list(self.nodes.keys())
        num_encounters = max(1, len(num_nodes_list) // 3)  # Some nodes encounter each other
        
        for _ in range(num_encounters):
            if len(num_nodes_list) < 2:
                break
            # Random pair of nodes encounter at hub and exchange tokens
            node_a, node_b = self.rng.choice(num_nodes_list, size=2, replace=False)
            # They both receive tokens from encountering each other at the hub
            self.nodes[node_a].receive_token(node_b)
            self.nodes[node_b].receive_token(node_a)
    
    def attempt_peer_connections(self) -> int:
        """
        Nodes attempt to connect with each other based on token interactions.
        Existing peer connections also exchange tokens this iteration.
        Returns number of new connections formed.
        """
        new_connections = 0
        
        # First: peer nodes exchange tokens with their connected peers
        for node_id, node in self.nodes.items():
            for peer_id in list(node.connections):
                # Random chance that connected peers exchange tokens this iteration
                if self.rng.random() < 0.5:  # 50% chance each direction per iteration
                    self.nodes[peer_id].receive_token(node_id)
        
        # Second: attempt new connections based on received tokens
        for node_id, node in self.nodes.items():
            # For each node, attempt connection with any other node it's received tokens from
            for from_node in list(node.token_counts.keys()):
                if from_node == self.central_id:
                    continue  # Skip hub
                
                if not node.is_connected_to(from_node):
                    if node.attempt_connection(from_node, self.rng):
                        # Bidirectional connection
                        self.nodes[from_node].connections.add(node_id)
                        # Update graph
                        self.graph.add_edge(node_id, from_node)
                        new_connections += 1
        
        return new_connections
    
    def get_graph_copy(self) -> nx.Graph:
        """Return a copy of the current graph state."""
        return self.graph.copy()
    
    def get_node_degrees(self) -> Dict[str, int]:
        """Get degree of each node in current graph."""
        return dict(self.graph.degree())
    
    def get_peer_connection_counts(self) -> Dict[str, int]:
        """Get number of peer connections (excluding hub) for each node."""
        counts = {}
        for node_id, node in self.nodes.items():
            counts[node_id] = node.get_degree()
        return counts
