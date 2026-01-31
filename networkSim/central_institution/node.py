import numpy as np
from collections import defaultdict
from typing import Dict

class Node:
    """Represents a peripheral node that receives tokens and forms connections."""
    
    def __init__(self, node_id: str, token_threshold: int = 5, 
                 connection_prob_base: float = 0.1, connection_prob_max: float = 0.9,
                 accumulation_rate: float = 0.2):
        """
        Initialize a node.
        
        Args:
            node_id: Unique identifier for this node
            token_threshold: Number of tokens needed to start connection probability
            connection_prob_base: Base probability when threshold is met
            connection_prob_max: Maximum probability cap
            accumulation_rate: Rate at which probability increases per token
        """
        self.node_id = node_id
        self.token_threshold = token_threshold
        self.connection_prob_base = connection_prob_base
        self.connection_prob_max = connection_prob_max
        self.accumulation_rate = accumulation_rate
        
        # Track tokens received from each other node
        self.token_counts: Dict[str, int] = defaultdict(int)
        # Track which nodes this node is connected to (bidirectional)
        self.connections: set = set()
        
    def receive_token(self, from_node: str) -> None:
        """Record receipt of a token from another node."""
        self.token_counts[from_node] += 1
        
    def get_connection_probability(self, from_node: str) -> float:
        """
        Calculate probability of forming connection with from_node based on tokens received.
        
        Probability increases with number of tokens received:
        - Below threshold: 0
        - At threshold: connection_prob_base
        - Above threshold: increases exponentially toward connection_prob_max
        """
        count = self.token_counts[from_node]
        
        if count < self.token_threshold:
            return 0.0
        
        # Exponential increase: base + (max - base) * (1 - e^(-rate * excess_tokens))
        excess_tokens = count - self.token_threshold
        prob = self.connection_prob_base + (
            (self.connection_prob_max - self.connection_prob_base) *
            (1 - np.exp(-self.accumulation_rate * excess_tokens))
        )
        return min(prob, self.connection_prob_max)
    
    def attempt_connection(self, from_node: str, rng: np.random.Generator) -> bool:
        """
        Attempt to establish connection with from_node based on current probability.
        
        Returns:
            True if connection was established, False otherwise
        """
        if from_node in self.connections:
            return False  # Already connected
        
        prob = self.get_connection_probability(from_node)
        if rng.random() < prob:
            self.connections.add(from_node)
            return True
        return False
    
    def is_connected_to(self, other_node: str) -> bool:
        """Check if connected to another node."""
        return other_node in self.connections
    
    def get_degree(self) -> int:
        """Get number of peer connections (not counting hub)."""
        return len(self.connections)
