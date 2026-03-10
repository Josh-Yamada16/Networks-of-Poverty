import networkx as nx
import parameters as P
from utility.visualizer import Visualization as viz

layout_functions = {
    'spring': viz.spring_lay,
    'circular': viz.circ_lay,
    # Add more layouts if needed
}

class Infection:
    def pass_infection(self, graph: nx.Graph, infection_threshold: float = P.INFECTION_THRESHOLD):
        # Complex Contagion infection model: if x fraction of p node's neighbors are infected, it becomes infected
        # get the central institution's neighbors
        central_neighbors = [node for node in graph.neighbors("CENTRAL_INSTITUTION") if graph.nodes[node].get('is_central_institution', False)]
        infected_central_neighbors = sum(1 for n in central_neighbors if graph.nodes[n].get('behavior_b', False))
        og_graph = graph.copy()  # Create a copy of the original graph to iterate over
        for node in graph.nodes():
            if graph.nodes[node].get('is_central_institution', False):
                continue  # Skip central institutions
            neighbors = set(graph.neighbors(node))
            if not neighbors:
                continue  # Skip isolated nodes
            infected_neighbors = sum(1 for n in neighbors if og_graph.nodes[n].get('behavior_b', False))
            # if this node is connected to the central institution, it should access the central institution's neighbors as well
            if any(graph.nodes[n].get('is_central_institution', False) for n in neighbors):
                neighbors |= set(central_neighbors)
                infected_neighbors += infected_central_neighbors
            infection_fraction = infected_neighbors / len(neighbors)
            if infection_fraction >= infection_threshold:
                graph.nodes[node]['behavior_b'] = True

    def total_graph_infected(self, graph: nx.Graph):
        return sum(1 for node in graph.nodes() if graph.nodes[node].get('behavior_b', False))

    def infect_cycle(self, gr: nx.Graph, states):
        self.pass_infection(graph=gr)

        node_colors = [
            "lightgray" if gr.nodes[node].get('is_central_institution', False)
            else "red" if gr.nodes[node].get('behavior_b', False)
            else "lightblue"
            for node in gr.nodes()
        ]
        states.append((gr.copy(), node_colors.copy()))

    def run_simulation(self, G: nx.Graph, iterations: int = 10, seed: int = 42, control_random: bool = False):
        # g, edge_mat, node_list = Setup.gen_graph(t=P.GRAPH_TYPE, n_nodes=P.NUM_NODES, seed=seed, control_random=control_random)
        penulti, final = None, None
        node_colors = [
            "lightgray" if G.nodes[node].get('is_central_institution', False)
            else "red" if G.nodes[node].get('behavior_b', False)
            else "lightblue"
            for node in G.nodes()
        ]
        layout = layout_functions.get(P.LAYOUT, viz.spring_lay)(G)
        states = [(G.copy(), node_colors.copy())]
        for i in range(iterations):
            self.infect_cycle(gr=G, states=states)
            cur_count = self.total_graph_infected(G)
            if (cur_count == penulti and cur_count == final) or cur_count == len(G.nodes()):
                print(f"Stopping early at iteration {i + 1} as infection count converged at {cur_count}/{len(G.nodes()) - 1}.")
                break
            penulti, final = final, cur_count
        return states, layout