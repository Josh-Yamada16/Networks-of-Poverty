from basicSetup import BasicSetup
from centralInstitutionNode import CentralInstitutionNode as CI
from infection import Infection
from interactivePlot import InteractivePlot
from utils import Utils
import parameters as P
import matplotlib.pyplot as plt

def main():
    sim = BasicSetup()
    sim.setup_basic_simulation()
    G = sim.G
    print(list(G.neighbors("CENTRAL_INSTITUTION")))
    print("Average degree:", Utils.average_degree(G))

    states, layout = Infection().run_simulation(G=G, iterations=P.NUM_ITERATIONS, control_random=P.CONTROL_RANDOM_SEED, seed=P.RANDOM_SEED)
    interactive = InteractivePlot(states=states, layout=layout)
    interactive.draw_current()
    if P.SHOW_PLOT:
        plt.show()

if __name__ == "__main__":
    main()