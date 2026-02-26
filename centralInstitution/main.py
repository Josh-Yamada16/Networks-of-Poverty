from basicSetup import BasicSetup
from centralInstitutionNode import CentralInstitutionNode as CI
import networkx as nx
from infection import Infection
import utils as U
from visualizer import Visualization as viz
from interactivePlot import InteractivePlot
import parameters as P
import matplotlib.pyplot as plt

def main():
    sim = BasicSetup()
    sim.setup_basic_simulation()
    G = sim.G
    CI.spread_behavior_b(G, behavior_b=1)
    print(list(G.neighbors("CENTRAL_INSTITUTION")))

    states, layout = Infection().run_simulation(G=G)
    interactive = InteractivePlot(states=states, layout=layout)
    interactive.draw_current()
    if P.SHOW_PLOT:
        plt.show()

if __name__ == "__main__":
    main()