from basicSim import BasicSimulation
import centralInstitution
import networkx as nx
import utils as U
from visualizer import Visualization as viz

def main():
    sim = BasicSimulation()
    sim.setup_basic_simulation()
    G = sim.G
    print(list(G.neighbors("CENTRAL_INSTITUTION")))
    viz.visualize_network(G, title="Initial Network")

if __name__ == "__main__":
    main()