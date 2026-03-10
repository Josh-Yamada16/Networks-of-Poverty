from basicsimSetup import BasicSimSetup
from centralInstitutionNode import CentralInstitutionNode as CI
from infection import Infection
from utility.interactivePlot import InteractivePlot
from utility.utils import Utils
import parameters as P
import networkx as nx
import imageio
import matplotlib.pyplot as plt
import os


def create_gif_from_states(states, layout, out_gif='graph_evolution.gif'):
    frames = []
    for i, state in enumerate(states):
        plt.figure(figsize=(8, 6))
        # If state is a tuple, extract the graph
        G = state[0] if isinstance(state, tuple) else state
        node_colors = [
            "orange" if G.nodes[node].get('is_central_institution', False)
            else "red" if G.nodes[node].get('behavior_b', False)
            else "lightblue"
            for node in G.nodes()
        ]
        nx.draw(G, layout, with_labels=False, node_color=node_colors, node_size=100, width=1)
        fname = f"frame_{i}.png"
        plt.savefig(fname)
        plt.close()
        frames.append(fname)
    images = [imageio.imread(f) for f in frames]
    imageio.mimsave(out_gif, images, duration=2.0)
    for f in frames:
        os.remove(f)

def main():
    sim = BasicSimSetup()
    sim.setup_basic_simulation()
    G = sim.G
    print("Number of neighbors of central institution:", len(list(G.neighbors("CENTRAL_INSTITUTION"))))
    print("Number of nodes:", len(G.nodes()))
    print("Average degree of a node:", Utils.average_degree(G))
    print("Number of initially infected nodes:", int(P.PERCENTAGE_OF_INFECTED_NODES * len(G.nodes())))

    states, layout = Infection().run_simulation(G=G, iterations=P.NUM_ITERATIONS, seed=P.RANDOM_SEED)
    interactive = InteractivePlot(states=states, layout=layout)
    interactive.draw_current()
    if P.SHOW_PLOT:
        plt.show()

    # Create GIF from simulation states
    # create_gif_from_states(states, layout)

if __name__ == "__main__":
    main()