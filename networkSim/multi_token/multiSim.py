from ..setup import Setup
from ..tokenSim import TokenSimulation
from .. import parameters as P
import networkx as nx
from ..visualizer import Visualization as viz
import numpy as np
from ..utils import Utils

class MultiTokenSimulation(TokenSimulation):
    @staticmethod
    def trade_cycle(self, gr: nx.Graph, it: int, edge_mat: np.ndarray, node_list: list[str], states):
        # capture balances before the trade
        previous_money = {n: gr.nodes[n]['money'] for n in node_list}

        # build column vector of money and compute per-pair transfers
        money_col = np.array([previous_money[n] for n in node_list], dtype=float)
        # transfer_matrix[i, j] = amount sent from node i to node j
        transfer_matrix = edge_mat * money_col[:, None]

        # Perform the balance update using the base trade implementation
        self.trade(graph=gr, edge_mat=edge_mat, node_list=node_list)

        # If a ledger is attached to the simulation instance, record all non-zero transfers
        ledger = getattr(self, 'ledger', None)
        if ledger is not None:
            n = len(node_list)
            for i in range(n):
                from_node = node_list[i]
                for j in range(n):
                    amt = float(transfer_matrix[i, j])
                    if amt > 1e-12:
                        to_node = node_list[j]
                        try:
                            ledger.record(iteration=it, from_node=from_node, to_node=to_node, amount=amt, method='trade')
                        except Exception:
                            # tolerate ledger failures during recording to keep simulation running
                            pass

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
        # Build primary graph and edge matrix
        g1, edge_mat1, node_list = Setup.gen_graph(t=P.GRAPH_TYPE, n_nodes=P.NUM_NODES, seed=42)

        # Create a reversed graph for the second simulation when applicable
        if getattr(g1, 'is_directed', lambda: False)():
            g2 = g1.reverse(copy=True)
        else: 
            g2 = g1.copy()

        node_neighbors2 = Setup.get_node_neighbors(g2)
        edge_mat2 = Setup.generate_edge_matrix(node_neighbors=node_neighbors2, node_names=node_list)

        # Original money maps for percent-change reporting
        og_money_g1 = {node: data["money"] for node, data in g1.nodes(data=True)}
        og_money_g2 = {node: data["money"] for node, data in g2.nodes(data=True)}

        # Initialize per-node tracking fields
        for g in (g1, g2):
            for n in g.nodes:
                g.nodes[n].setdefault('gains_losses', [])
                g.nodes[n].setdefault('original_money', g.nodes[n].get('money', 0))

        node_colors1 = [g1.nodes[n]["money"] for n in node_list]
        node_colors2 = [g2.nodes[n]["money"] for n in node_list]

        layout1 = viz.spring_lay(g1)
        layout2 = viz.spring_lay(g2)

        states1 = [(g1.copy(), node_colors1.copy())]
        states2 = [(g2.copy(), node_colors2.copy())]

        # Run iterations for both graphs
        for it in range(iterations):
            self.trade_cycle(gr=g1, it=it, edge_mat=edge_mat1, node_list=node_list, states=states1)
            self.trade_cycle(gr=g2, it=it, edge_mat=edge_mat2, node_list=node_list, states=states2)

        # Final percent-change reports
        Utils.calc_and_print_percent_change(g=g1, previous_money=og_money_g1, it=None)
        Utils.calc_and_print_percent_change(g=g2, previous_money=og_money_g2, it=None)

        return (states1, layout1, edge_mat1), (states2, layout2, edge_mat2)