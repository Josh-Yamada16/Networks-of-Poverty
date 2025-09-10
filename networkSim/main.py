from tokenSim import ExchangeSimulation
import parameters as P
from interactivePlot import InteractivePlot
import matplotlib.pyplot as plt

def main():
    states, layout, edge_mat, ledger = ExchangeSimulation(max_stingy_behaviors=P.MAX_STINGY_BEHAVIORS)\
        .run_simulation(gen_ledger=P.GENERATE_LEDGER, iterations=P.NUM_ITERATIONS)
    print(ledger.df)
    viz = InteractivePlot(states=states, layout=layout)
    viz.draw_current()
    if P.SHOW_PLOT:
        plt.show()

if __name__ == "__main__":
    main()
