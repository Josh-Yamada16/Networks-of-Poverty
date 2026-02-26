from basicSim import BasicSimulation
from centralInstitution import CentralInstitution as CI
import networkx as nx
from networkSim.tokenSim import ExchangeSimulation
import utils as U
from visualizer import Visualization as viz
from interactivePlot import InteractivePlot
import parameters as P
import matplotlib.pyplot as plt

def main():
    sim = BasicSimulation()
    sim.setup_basic_simulation()
    G = sim.G
    CI.spread_behavior_b(G, behavior_b=1)
    print(list(G.neighbors("CENTRAL_INSTITUTION")))
    viz.visualize_network(G, title="Initial Network")

    states, layout = ExchangeSimulation(max_stingy_behaviors=P.MAX_STINGY_BEHAVIORS)\
        .run_simulation(gen_ledger=P.GENERATE_LEDGER, iterations=P.NUM_ITERATIONS)
    interactive = InteractivePlot(states=states, layout=layout)
    interactive.draw_current()
    if P.SHOW_PLOT:
        plt.show()

if __name__ == "__main__":
    main()