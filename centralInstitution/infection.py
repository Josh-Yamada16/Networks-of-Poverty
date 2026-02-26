import networkx as nx
import numpy as np
import parameters as P
from setup import Setup
from visualizer import Visualization as viz
from utils import Utils

layout_functions = {
    'spring': viz.spring_lay,
    'circular': viz.circ_lay,
    # Add more layouts if needed
}

class Infection:

    def pass_infection(self, graph: nx.Graph):
        # Complex Contagion infection model: if x fraction of p node's neighbors are infected, it becomes infected
        infection_threshold = 0.3  # Example threshold: 50% of neighbors must be infected
        for node in graph.nodes():
            if graph.nodes[node].get('is_central_institution', False):
                continue  # Skip central institutions
            neighbors = list(graph.neighbors(node))
            if not neighbors:
                continue
            infected_neighbors = sum(1 for n in neighbors if graph.nodes[n].get('behavior_b', False))
            infection_fraction = infected_neighbors / len(neighbors)
            if infection_fraction >= infection_threshold:
                graph.nodes[node]['behavior_b'] = True

    def infect_cycle(self, gr: nx.Graph, states):
        self.pass_infection(graph=gr)

        node_colors = [
            "lightgray" if gr.nodes[node].get('is_central_institution', False)
            else "red" if gr.nodes[node].get('behavior_b', False)
            else "lightblue"
            for node in gr.nodes()
        ]
        states.append((gr.copy(), node_colors.copy()))

    def run_simulation(self, iterations: int = 10, seed: int = 42, control_random: bool = False, G: nx.Graph = None):
        # g, edge_mat, node_list = Setup.gen_graph(t=P.GRAPH_TYPE, n_nodes=P.NUM_NODES, seed=seed, control_random=control_random)
        if G is not None:
            g = G
        # Initialize gains/losses history and store original money for each node
        node_list = list(g.nodes())
        edge_mat = nx.to_numpy_array(g)
        node_colors = [
            "lightgray" if g.nodes[node].get('is_central_institution', False)
            else "red" if g.nodes[node].get('behavior_b', False)
            else "lightblue"
            for node in g.nodes()
        ]
        layout = layout_functions.get(P.LAYOUT, viz.spring_lay)(g)
        states = [(g.copy(), node_colors.copy())]
        for it in range(iterations):
            self.infect_cycle(gr=g, states=states)
        return states, layout, edge_mat