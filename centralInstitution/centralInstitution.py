import networkx as nx

behavior_b_dictionary = {
    1: "Always stingy",
    2: "Stingy if lost money in previous cycle",
    3: "Stingy if lost money in any previous cycle"
}

class CentralInstitution:
    
    @staticmethod
    def spread_behavior_b(G: nx.Graph, behavior_b: int):
        central_inst = [node for node, data in G.nodes(data=True) if data.get('is_central_institution', False)]
        if not central_inst:
            raise ValueError("No central institution found in the graph.")
        # spread the behavior_b to all nodes neighboring the central institution
        for node in G.nodes:
            if any(node in G.neighbors(central_node) for central_node in central_inst):
                G.nodes[node]['behavior_b'] = True