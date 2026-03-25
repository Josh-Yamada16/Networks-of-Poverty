import networkx as nx
from centralInstitutionNode import CentralInstitutionNode as CI
from setup import Setup
import parameters as P
import random

class BasicSimSetup:
    def __init__(self):
        self.G = nx.Graph()

    def init_infect(self, G: nx.Graph, percentage_of_infected_nodes: float = P.PERCENTAGE_OF_INFECTED_NODES, initial_infection_type: int = P.INITIAL_INFECTION_TYPE):
        eligible_nodes = [
            node for node in G.nodes()
            if not G.nodes[node].get('is_central_institution', False)
        ]
        match initial_infection_type:
            # Randomly select initial infected nodes from the entire graph
            case 0:
                target = int(percentage_of_infected_nodes * len(eligible_nodes))
                random_nodes = random.sample(eligible_nodes, min(target, len(eligible_nodes)))
            # Randomly select a block and then randomly select initial infected nodes from that block
            case 1:
                block = random.randint(0, P.STOCHASTIC_BLOCKS - 1)
                block_nodes = [node for node in eligible_nodes if G.nodes[node].get('block') == block]
                target = int(percentage_of_infected_nodes * len(eligible_nodes))
                random_nodes = random.sample(block_nodes, min(target, len(block_nodes)))
            # Randomly select nodes from different blocks for initial infection
            case 2:
                random_nodes = []
                for block in range(P.STOCHASTIC_BLOCKS):
                    block_nodes = [node for node in eligible_nodes if G.nodes[node].get('block') == block]
                    if block_nodes:
                        random_nodes.append(random.choice(block_nodes))
            case _:
                random_nodes = []

        for node in G.nodes():
            if node in random_nodes:
                G.nodes[node]['infected'] = True

    def setup_basic_simulation(self, n_nodes: int = P.NUM_NODES, central_institution_toggle: bool = P.CENTRAL_INSTITUTION_TOGGLE):
        # create n nodes with letter codes as labels
        self.G = Setup.gen_graph(t=P.GRAPH_TYPE, n_nodes=n_nodes)[0]
        # add a central institution node and connect it to x random nodes
        if central_institution_toggle:
            self.G = CI.add_central_institution(self.G, list(self.G.nodes()))
        self.init_infect(self.G, initial_infection_type=P.INITIAL_INFECTION_TYPE)
