import random
import parameters as P
import networkx as nx

behavior_b_dictionary = {
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
        CentralInstitutionNode.add_central_institution(G, list(G.nodes()))
    
    @staticmethod
    def add_central_institution(G: nx.Graph, letter_codes: list[str]):
        central_institution = "CENTRAL_INSTITUTION"
        G.add_node(central_institution, is_central_institution=True, behavior_b=False)
        num_connections = int(P.CENTRAL_INSTITUTION_CONNECTIONS * len(G.nodes())) # number of connections to random nodes
        random_nodes = random.sample(letter_codes, num_connections)
        for node in random_nodes:
            G.add_edge(central_institution, node)
        return G