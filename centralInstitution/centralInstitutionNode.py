import random
import parameters as P
import networkx as nx

infected_dictionary = {
    1: "Always stingy",
    2: "Stingy if lost money in previous cycle",
    3: "Stingy if lost money in any previous cycle"
}

class CentralInstitutionNode:
    
    @staticmethod
    def relocate_central_institution(G: nx.Graph):
        # For simplicity, let's just move the central institution so it connects with randomly selected nodes
        central_inst = [node for node, data in G.nodes(data=True) if data.get('is_central_institution', False)]
        if not central_inst:
            raise ValueError("No central institution found in the graph.")
        old_central = central_inst[0]
        # Remove old central institution
        G.remove_node(old_central)
        # Add new central institution
        CentralInstitutionNode.add_central_institution(G, list(G.nodes()), P.CENTRAL_INSTITUTION_CONNECTION_PERCENTAGE)
    
    @staticmethod
    def add_central_institution(
        G: nx.Graph,
        letter_codes: list[str],
        central_institution_connection_percentage: float = P.CENTRAL_INSTITUTION_CONNECTION_PERCENTAGE,
        node_name: str = "CENTRAL_INSTITUTION",
    ):
        central_institution = node_name
        if G.has_node(central_institution):
            raise ValueError(f"Node '{central_institution}' already exists in the graph.")
        G.add_node(central_institution, is_central_institution=True, infected=False)
        eligible_nodes = [
            node for node in letter_codes
            if node in G and not G.nodes[node].get('is_central_institution', False)
        ]
        num_connections = int(central_institution_connection_percentage * len(eligible_nodes))
        num_connections = min(num_connections, len(eligible_nodes))
        random_nodes = random.sample(eligible_nodes, num_connections) if num_connections > 0 else []
        for node in random_nodes:
            G.add_edge(central_institution, node)

        infected_neighbors = sum(1 for node in G.neighbors(central_institution) if not G.nodes[node].get('is_central_institution', False) and G.nodes[node].get('infected', False))

        print(f"Neighbors already infected: {infected_neighbors} / {num_connections}")
        return G