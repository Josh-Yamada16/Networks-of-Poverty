import unittest
import networkx as nx
import numpy as np
from simulation import TokenSimulation
from setup import Setup
import parameters as P

class TestTokenSimulation(unittest.TestCase):
    def setUp(self):
        self.sim = TokenSimulation()
        self.n_nodes = 5
        self.g, self.edge_mat, self.node_list = Setup.gen_graph(t="erd", n_nodes=self.n_nodes, seed=1)
        Setup.assign_money(self.g)
        for node in self.g.nodes:
            self.g.nodes[node]['gains_losses'] = []
            self.g.nodes[node]['original_money'] = self.g.nodes[node]['money']

    def test_trade_cycle_money_conservation(self):
        # Save total money before
        total_before = sum(self.g.nodes[n]['money'] for n in self.g.nodes)
        states = []
        self.sim.trade_cycle(self.g, 0, self.edge_mat, self.node_list, states)
        total_after = sum(self.g.nodes[n]['money'] for n in self.g.nodes)
        self.assertAlmostEqual(total_before, total_after, places=5)

    def test_gains_losses_tracking(self):
        states = []
        self.sim.trade_cycle(self.g, 0, self.edge_mat, self.node_list, states)
        for n in self.g.nodes:
            self.assertEqual(len(self.g.nodes[n]['gains_losses']), 1)

    def test_stingy_behavior_toggle(self):
        # Force a node to be stingy
        n = self.node_list[0]
        self.g.nodes[n]['gains_losses'] = [-100] * max(5, P.STINGY_WINDOW)
        self.g.nodes[n]['money'] = 0
        # Enable stingy
        P.STINGY_ENABLED = True
        self.sim.check_and_apply_stingy_behavior(self.g, 1, self.edge_mat, self.node_list)
        self.assertTrue(self.g.has_edge(n, n))
        # Disable stingy
        self.g.remove_edge(n, n)
        P.STINGY_ENABLED = False
        self.sim.check_and_apply_stingy_behavior(self.g, 2, self.edge_mat, self.node_list)
        self.assertFalse(self.g.has_edge(n, n))

if __name__ == '__main__':
    unittest.main()
