import networkx as nx
import utils as U
import random

class BasicSimulation:
    def __init__(self):
        self.G = nx.Graph()

    def setup_basic_simulation(self):
        # create n nodes with letter codes as labels
        num_nodes = 100
        letter_codes = U.Utils.generate_letter_codes(num_nodes)
        for code in letter_codes:
            self.G.add_node(code, is_central_institution=False, behavior_b=False)
        # randomly create edges between nodes with a p% chance
        connection_probability = 0.025
        for i in range(len(letter_codes)):
            for j in range(i + 1, len(letter_codes)):
                if random.random() < connection_probability:
                    self.G.add_edge(letter_codes[i], letter_codes[j])
        # add a central institution node and connect it to x random nodes
        central_institution = "CENTRAL_INSTITUTION"
        self.G.add_node(central_institution, is_central_institution=True, behavior_b=False)
        num_connections = 10  # number of connections to random nodes
        random_nodes = random.sample(letter_codes, num_connections)
        for node in random_nodes:
            self.G.add_edge(central_institution, node)
    