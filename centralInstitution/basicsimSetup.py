import networkx as nx
from centralInstitutionNode import CentralInstitutionNode as CI
from setup import Setup
import parameters as P
import random

class BasicSimSetup:
    def __init__(self):
        self.G = nx.Graph()

    def init_infect(self, G: nx.Graph, percentage_of_infected_nodes: float = P.PERCENTAGE_OF_INFECTED_NODES, initial_infection_type: int = P.INITIAL_INFECTION_TYPE):
        match initial_infection_type:
            # Randomly select initial infected nodes from the entire graph
            case 0:
                random_nodes = random.sample(list(G.nodes()), int(percentage_of_infected_nodes * len(G.nodes())))
            # Randomly select a block and then randomly select initial infected nodes from that block
            case 1:
                block = random.randint(0, P.STOCHASTIC_BLOCKS - 1)
                block_nodes = [node for node in G.nodes() if G.nodes[node].get('block') == block]
                random_nodes = random.sample(block_nodes, min(int(percentage_of_infected_nodes * len(G.nodes())), len(block_nodes)))
            # Randomly select nodes from different blocks for initial infection
            case 2:
                random_nodes = []
                for block in range(P.STOCHASTIC_BLOCKS):
                    block_nodes = [node for node in G.nodes() if G.nodes[node].get('block') == block]
                    if block_nodes:
                        random_nodes.append(random.choice(block_nodes))

        for node in G.nodes():
            if node in random_nodes:
                G.nodes[node]['behavior_b'] = True

    def setup_basic_simulation(self, n_nodes: int = P.NUM_NODES, central_institution_toggle: bool = P.CENTRAL_INSTITUTION_TOGGLE):
        # create n nodes with letter codes as labels
        self.G = Setup.gen_graph(t=P.GRAPH_TYPE, n_nodes=n_nodes)[0]
        # add a central institution node and connect it to x random nodes
        if central_institution_toggle:
            self.G = CI.add_central_institution(self.G, list(self.G.nodes()))
        self.init_infect(self.G, initial_infection_type=P.INITIAL_INFECTION_TYPE)
