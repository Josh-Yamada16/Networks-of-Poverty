from pathlib import Path
import sys

# Allow running this file directly from centralInstitution/experiments.
sys.path.append(str(Path(__file__).resolve().parents[1]))

"""Experiment: effect of infection threshold on final spread."""
from experimentSkeleton import ExperimentSkeleton
from basicsimSetup import BasicSimSetup
from infection import Infection
import parameters as P
import matplotlib.pyplot as plt


class InfectionThresholdExperiment(ExperimentSkeleton):
    """Run the same starting graph over multiple infection thresholds."""
    
    def __init__(self):
        super().__init__()
        self.G = None
        self.infection_model = Infection()
        self.thresholds = [round(x, 1) for x in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]]
        self.threshold_results = []
        self.original_threshold = P.INFECTION_THRESHOLD
    
    def setup(self):
        """Initialize one baseline graph that will be copied per threshold."""
        init_sim = BasicSimSetup()
        init_sim.setup_basic_simulation(central_institution_toggle=False)
        self.G = init_sim.G
        print(f"Base graph ready with {len(self.G.nodes())} nodes and {len(self.G.edges())} edges")
        print(f"Threshold sweep: {self.thresholds}")
    
    def run(self):
        """Run a simulation for each threshold value."""
        self.threshold_results = []
        representative_states = None
        representative_layout = None

        for threshold in self.thresholds:
            P.INFECTION_THRESHOLD = threshold
            test_graph = self.G.copy()
            states, layout = self.infection_model.run_simulation(
                G=test_graph,
                iterations=P.NUM_ITERATIONS,
                seed=P.RANDOM_SEED,
                central_institution_toggle=False,
                infection_threshold=threshold,
            )

            final_infected = self.infection_model.total_graph_infected(test_graph)
            total_nodes = len(test_graph.nodes())
            infected_ratio = final_infected / total_nodes if total_nodes else 0

            self.threshold_results.append(
                {
                    "threshold": threshold,
                    "final_infected": final_infected,
                    "infected_ratio": infected_ratio,
                    "steps": len(states) - 1,
                }
            )

            if abs(threshold - self.original_threshold) < 1e-9:
                representative_states = states
                representative_layout = layout

        P.INFECTION_THRESHOLD = self.original_threshold

        if representative_states is not None:
            self.states = representative_states
            self.layout = representative_layout
    
    def print_results(self):
        """Print threshold sweep summary."""
        print("\nInfection Threshold Sweep Results")
        print("threshold | final_infected | infected_ratio | steps")
        print("-" * 52)
        for row in self.threshold_results:
            print(
                f"{row['threshold']:>8.1f} |"
                f" {row['final_infected']:>14d} |"
                f" {row['infected_ratio']:>13.2%} |"
                f" {row['steps']:>5d}"
            )

        best = max(self.threshold_results, key=lambda r: r["infected_ratio"])
        worst = min(self.threshold_results, key=lambda r: r["infected_ratio"])
        print("\nKey Outcomes")
        print(
            f"Highest spread at threshold {best['threshold']:.1f}: "
            f"{best['final_infected']} infected ({best['infected_ratio']:.2%})"
        )
        print(
            f"Lowest spread at threshold {worst['threshold']:.1f}: "
            f"{worst['final_infected']} infected ({worst['infected_ratio']:.2%})"
        )
    
    def visualize(self, show_plot=True):
        """Plot threshold versus final infected ratio."""
        if not self.threshold_results:
            print("No results available to visualize.")
            return

        x_vals = [row["threshold"] for row in self.threshold_results]
        y_vals = [row["infected_ratio"] for row in self.threshold_results]

        plt.figure(figsize=(8, 5))
        plt.plot(x_vals, y_vals, marker="o", linewidth=2)
        plt.title("Infection Spread vs Infection Threshold")
        plt.xlabel("Infection Threshold")
        plt.ylabel("Final Infected Ratio")
        plt.ylim(0, 1)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()

        if show_plot:
            plt.show()


def main():
    """Run the custom experiment."""
    experiment = InfectionThresholdExperiment()
    experiment.execute(show_plot=P.SHOW_PLOT)


if __name__ == "__main__":
    main()
