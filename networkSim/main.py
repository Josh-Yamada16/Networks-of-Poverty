from simulation import TokenSimulation
import parameters as P
from interactivePlot import InteractivePlot
import matplotlib.pyplot as plt

def main():
    states, layout, edge_mat = TokenSimulation(max_stingy_behaviors=100).run_simulation(P.NUM_ITERATIONS)
    viz = InteractivePlot(states=states, layout=layout)
    viz.draw_current()
    if P.SHOW_PLOT:
        plt.show()

if __name__ == "__main__":
    main()
