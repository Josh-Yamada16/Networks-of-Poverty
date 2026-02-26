import networkx as nx
from centralInstitutionNode import CentralInstitutionNode as CI
from setup import Setup
import parameters as P

class BasicSetup:
    def __init__(self):
        self.G = nx.Graph()

    def setup_basic_simulation(self):
        # create n nodes with letter codes as labels
        self.G = Setup.gen_graph(t=P.GRAPH_TYPE, n_nodes=P.NUM_NODES, seed=P.RANDOM_SEED, control_random=P.CONTROL_RANDOM_SEED)[0]
        # add a central institution node and connect it to x random nodes
        self.G = CI.add_central_institution(self.G, list(self.G.nodes()))
    