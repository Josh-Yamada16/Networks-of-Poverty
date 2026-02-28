import networkx as nx
from centralInstitutionNode import CentralInstitutionNode as CI
from setup import Setup
import parameters as P
import random

class BasicSetup:
    def __init__(self):
        self.G = nx.Graph()

    def init_infect(self, G: nx.Graph):
        if P.PURE_RANDOMIZED_INITIAL_INFECTION:
            random_nodes = random.sample(G.nodes(), P.INIT_INFECTED_NODES)
        elif P.BLOCK_RANDOMIZED_INITIAL_INFECTION:
            # Randomly select a block
            block = random.randint(0, P.STOCHASTIC_BLOCKS - 1)
            block_nodes = [node for node in G.nodes() if G.nodes[node].get('block') == block]
            random_nodes = random.sample(block_nodes, min(P.INIT_INFECTED_NODES, len(block_nodes)))
        elif P.DISPERSED_BLOCK_INITIAL_INFECTION:
            # Randomly select nodes from different blocks
            random_nodes = []
            for block in range(P.STOCHASTIC_BLOCKS):
                block_nodes = [node for node in G.nodes() if G.nodes[node].get('block') == block]
                if block_nodes:
                    random_nodes.append(random.choice(block_nodes))

        for node in G.nodes():
            if node in random_nodes:
                G.nodes[node]['behavior_b'] = True

    def setup_basic_simulation(self):
        # create n nodes with letter codes as labels
        self.G = Setup.gen_graph(t=P.GRAPH_TYPE, n_nodes=P.NUM_NODES, seed=P.RANDOM_SEED, control_random=P.CONTROL_RANDOM_SEED)[0]
        # add a central institution node and connect it to x random nodes
        if P.CENTRAL_INSTITUTION_TOGGLE:
            self.G = CI.add_central_institution(self.G, list(self.G.nodes()))
        self.init_infect(self.G)
