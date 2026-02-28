from basicsimSetup import BasicSimSetup
from centralInstitutionNode import CentralInstitutionNode as CI
from infection import Infection
from utility.interactivePlot import InteractivePlot
from utility.utils import Utils
import parameters as P
import matplotlib.pyplot as plt

def main():
    sim = BasicSimSetup()
    sim.setup_basic_simulation()
    G = sim.G
    print("Number of neighbors of central institution:", len(list(G.neighbors("CENTRAL_INSTITUTION"))))
    print("Number of nodes:", len(G.nodes()))
    print("Average degree of a node:", Utils.average_degree(G))
    print("Number of initially infected nodes:", P.INIT_INFECTED_NODES)

    states, layout = Infection().run_simulation(G=G, iterations=P.NUM_ITERATIONS, seed=P.RANDOM_SEED)
    interactive = InteractivePlot(states=states, layout=layout)
    interactive.draw_current()
    if P.SHOW_PLOT:
        plt.show()

if __name__ == "__main__":
    main()