from basicsimSetup import BasicSimSetup
from infection import Infection
from utility.interactivePlot import InteractivePlot
from centralInstitutionNode import CentralInstitutionNode as CI
from utility.utils import Utils
import parameters as P
import matplotlib.pyplot as plt


def _infected_counts(states):
    return [
        sum(
            1 for node in graph.nodes()
            if graph.nodes[node].get('infected', False)
            and not graph.nodes[node].get('is_central_institution', False)
        )
        for graph, _ in states
    ]


def _has_converged(infected_counts, target_infectable):
    if not infected_counts:
        return False
    if infected_counts[-1] == target_infectable:
        return True
    return len(infected_counts) >= 3 and infected_counts[-1] == infected_counts[-2] == infected_counts[-3]


def main():
    init_sim = BasicSimSetup()
    print("=" * 40)
    print("Setting up initial network...")
    init_sim.setup_basic_simulation(central_institution_toggle=False)
    G = init_sim.G

    print("=" * 40)
    print("**Initial network setup**")
    print("Number of nodes:", len(G.nodes()))
    print("Average degree of a node:", f"{Utils.average_degree(G):.2f}")
    print("Number of initially infected nodes:", int(P.PERCENTAGE_OF_INFECTED_NODES * len(G.nodes())))
    print("Infection threshold:", P.INFECTION_THRESHOLD * 100, "%")


    print("=" * 40)
    print("[Phase 1] Running infection simulation without central institution...")
    infection_model = Infection()
    states, layout = infection_model.run_simulation(
        G=G,
        iterations=P.NUM_ITERATIONS,
        seed=P.RANDOM_SEED,
        central_institution_toggle=False
    )

    infected_counts = _infected_counts(states)
    target_infectable = len(G.nodes())
    converged_before_ci = _has_converged(infected_counts, target_infectable)

    print("=" * 40)
    if converged_before_ci:
        print(f"[Phase 2] Adding Central Institution...")
        print(f"Converged before adding central institution at {infected_counts[-1]}/{target_infectable} infected nodes.")
        CI.add_central_institution(G, list(G.nodes()), P.CENTRAL_INSTITUTION_CONNECTION_PERCENTAGE)
        print(f"Central institution connected to {len(list(G.neighbors('CENTRAL_INSTITUTION')))} nodes")
        states2, _ = infection_model.run_simulation(
            G=G,
            iterations=P.NUM_ITERATIONS,
            seed=P.RANDOM_SEED,
            central_institution_toggle=True,
            first_phase_2=True
        )
        states += states2
    else:
        print(
            "Infection did not converge within the configured iterations before adding a central institution. "
            "Increase NUM_ITERATIONS to trigger the two-phase experiment."
        )

    print("=" * 40)
    print("Rendering interactive plot...")
    interactive = InteractivePlot(states=states, layout=layout)
    interactive.draw_current()
    if P.SHOW_PLOT:
        plt.show()
    print("**Simulation Complete**")

if __name__ == "__main__":
    main()