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

class InfectionSimulation:
    def __init__(self, max_stingy_behaviors=None):
        self.max_stingy_behaviors = max_stingy_behaviors

    def trade(self, graph: nx.Graph, edge_mat: np.ndarray, node_list: list[str], it: int, gen_ledger: bool):
        # Convert node money into an array
        money_col_vector = np.array([graph.nodes[node]["money"] for node in node_list], dtype=float).T
        # Compute net flow using matrix multiplication
        trans = edge_mat.T
        result = edge_mat.T @ money_col_vector
        # Update the money for each node
        for i, node in enumerate(node_list):
            graph.nodes[node]["money"] = result[i]
        if gen_ledger:
            self.ledger_logic(graph=graph, trans=trans, node_list=node_list, it=it)

    def trade_cycle(self, gr: nx.Graph, it: int, edge_mat: np.ndarray, node_list: list[str], gen_ledger: bool, stingy_behavior_enabled: bool, states):
        previous_money = {n: gr.nodes[n]['money'] for n in node_list}
        self.trade(graph=gr, edge_mat=edge_mat, node_list=node_list, it=it, gen_ledger=gen_ledger)

        # Track gains/losses for each node this cycle
        for n in node_list:
            gain_loss = gr.nodes[n]['money'] - previous_money[n]
            gr.nodes[n].setdefault('gains_losses', []).append(gain_loss)

        # Stingy behavior: check and apply using separate method
        if stingy_behavior_enabled:
            self.check_and_apply_stingy_behavior(gr, it, edge_mat, node_list)

        Utils.calc_and_print_percent_change(g=gr, previous_money=previous_money, it=it)
        node_colors = [gr.nodes[n]["money"] for n in node_list]
        states.append((gr.copy(), node_colors.copy()))

    def run_simulation(self, gen_ledger: bool, iterations: int = 10, seed: int = 42, control_random: bool = False, stingy_behavior_enabled: bool = False):
        g, edge_mat, node_list = Setup.gen_graph(t=P.GRAPH_TYPE, n_nodes=P.NUM_NODES, seed=seed, control_random=control_random)
        # Initialize gains/losses history and store original money for each node
        og_money_amounts = {node: data["money"] for node, data in g.nodes(data=True)}
        node_colors = [g.nodes[n]["money"] for n in node_list]
        layout = layout_functions.get(P.LAYOUT, viz.spring_lay)(g)
        states = [(g.copy(), node_colors.copy())]
        for it in range(iterations):
            self.trade_cycle(gr=g, it=it, edge_mat=edge_mat, node_list=node_list, gen_ledger=gen_ledger, states=states, stingy_behavior_enabled=stingy_behavior_enabled)
        Utils.calc_and_print_percent_change(g=g, previous_money=og_money_amounts, it=None)
        last_graph = states[-1][0]
        end_monies = [last_graph.nodes[n]["money"] for n in node_list]
        mat_scaling_fac = Utils.compare_to_eigenvector(np.array(end_monies), edge_mat)
        Utils.check_if_eigenvector(end_monies=np.array(end_monies), edge_mat=edge_mat)
        # print(np.array(end_monies))
        # print(self.ledger.df)
        return states, layout, edge_mat