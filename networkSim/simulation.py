import networkx as nx
import numpy as np
from . import parameters as P
from .setup import Setup
from .visualizer import Visualization as viz
from .utils import Utils


class TokenSimulation:
    def __init__(self, max_stingy_behaviors=None):
        self.max_stingy_behaviors = max_stingy_behaviors
        self.layout_functions = {
            'spring': viz.spring_lay,
            'circular': viz.circ_lay
        }

    def check_and_apply_stingy_behavior(self, gr: nx.Graph, it: int, edge_mat: np.ndarray, node_list: list[str]):
        if not getattr(P, 'STINGY_ENABLED', True):
            return
        window = getattr(P, 'STINGY_WINDOW', 3)
        avg_loss_pct = getattr(P, 'STINGY_AVG_LOSS_PCT', 0.05)
        max_behaviors = self.max_stingy_behaviors
        # Use an attribute on the graph to track total stingy behaviors
        if 'stingy_count' not in gr.graph:
            gr.graph['stingy_count'] = 0
        updated_nodes = []
        for n in node_list:
            if max_behaviors is not None and gr.graph['stingy_count'] >= max_behaviors:
                break
            glist = gr.nodes[n]['gains_losses']
            original = gr.nodes[n].get('original_money', gr.nodes[n]['money'])
            if len(glist) >= window:
                avg_pct_loss = sum(g / original for g in glist[-window:]) / window
                if avg_pct_loss <= -avg_loss_pct:
                    if not gr.has_edge(n, n):
                        gr.add_edge(n, n)
                        updated_nodes.append(n)
                        gr.graph['stingy_count'] += 1
        # If any self-loops were added, update the edge matrix and print info
        if updated_nodes:
            # print(f"Iteration {it + 2}: Self-loop added for node(s): {', '.join(str(x) for x in updated_nodes)}")
            node_neighbors = Setup.get_node_neighbors(gr)
            edge_mat[:] = Setup.generate_edge_matrix(node_neighbors=node_neighbors, node_names=node_list)
            # print(Utils.calc_eigenvector(edge_mat))

    @staticmethod
    def trade(graph: nx.Graph, edge_mat: np.ndarray, node_list: list[str]):
        # Convert node money into an array
        money_col_vector = np.array([graph.nodes[node]["money"] for node in node_list], dtype=float).T
        # Compute net flow using matrix multiplication
        result = edge_mat.T @ money_col_vector
        # Update the money for each node
        for i, node in enumerate(node_list):
            graph.nodes[node]["money"] = result[i]

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

    def run_simulation(self, iterations: int = 10):
        g, edge_mat, node_list = Setup.gen_graph(t=P.GRAPH_TYPE, n_nodes=P.NUM_NODES, seed=42)
        # Initialize gains/losses history and store original money for each nodew
        og_money_amounts = {node: data["money"] for node, data in g.nodes(data=True)}
        node_colors = [g.nodes[n]["money"] for n in node_list]
        layout = self.layout_functions.get(P.LAYOUT, viz.spring_lay)(g)
        states = [(g.copy(), node_colors.copy())]
        for it in range(iterations):
            self.trade_cycle(gr=g, it=it, edge_mat=edge_mat, node_list=node_list, states=states)
        Utils.calc_and_print_percent_change(g=g, previous_money=og_money_amounts, it=None)
        last_graph = states[-1][0]
        end_monies = [last_graph.nodes[n]["money"] for n in node_list]
        mat_scaling_fac = Utils.compare_to_eigenvector(np.array(end_monies), edge_mat)
        Utils.check_if_eigenvector(end_monies=np.array(end_monies), edge_mat=edge_mat)
        # print(np.array(end_monies))
        return states, layout, edge_mat