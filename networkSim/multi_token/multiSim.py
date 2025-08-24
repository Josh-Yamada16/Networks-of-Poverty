from ..setup import Setup
from ..simulation import TokenSimulation
from .. import parameters as P
import networkx as nx
from ..visualizer import Visualization as viz
import numpy as np
from ..utils import Utils

class MultiTokenSimulation(TokenSimulation):
    def trade_cycle(self, gr: nx.Graph, it: int, edge_mat: np.ndarray, node_list: list[str], states):
        previous_money = {n: gr.nodes[n]['money'] for n in node_list}
        self.trade(graph=gr, edge_mat=edge_mat, node_list=node_list)
 
        # Track gains/losses for each node this cycle
        for n in node_list:
            gain_loss = gr.nodes[n]['money'] - previous_money[n]
            gr.nodes[n].setdefault('gains_losses', []).append(gain_loss)

        # Stingy behavior: check and apply using separate method
        self.check_and_apply_stingy_behavior(gr, it, edge_mat, node_list)

        Utils.calc_and_print_percent_change(g=gr, previous_money=previous_money, it=it)
        node_colors = [gr.nodes[n]["money"] for n in node_list]
        states.append((gr.copy(), node_colors.copy()))

    def run_simulation(self, iterations = 10):
        g1, edge_mat1, node_list = Setup.gen_graph(t=P.GRAPH_TYPE, n_nodes=P.NUM_NODES, seed=42)
        g2 = g1.reverse(copy=True)
        node_neighbors2 = Setup.get_node_neighbors(g2)
        edge_mat2 = Setup.generate_edge_matrix(node_neighbors=node_neighbors2, node_names=node_list)
        og_money_g1 = {node: data["money"] for node, data in g1.nodes(data=True)}
        og_money_g2 = {node: data["money"] for node, data in g2.nodes(data=True)}

        node_colors1 = [g1.nodes[n]["money"] for n in node_list]
        node_colors2 = [g2.nodes[n]["money"] for n in node_list]

        layout1 = self.layout_functions.get(P.LAYOUT, viz.spring_lay)(g1)
        layout2 = self.layout_functions.get(P.LAYOUT, viz.spring_lay)(g2)

        states = [(g1.copy(), node_colors1.copy(), g2.copy(), node_colors2.copy())]
        for it in range(iterations):
            self.trade_cycle(gr=g1, it=it, edge_mat=edge_mat1, node_list=node_list, states=states)

        return states, layout, edge_mat