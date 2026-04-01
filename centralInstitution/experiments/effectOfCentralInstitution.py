from pathlib import Path
import sys

# Allow running this file directly from centralInstitution/experiments.
sys.path.append(str(Path(__file__).resolve().parents[1]))

from experimentSkeleton import MultiPhaseExperimentSkeleton
from basicsimSetup import BasicSimSetup
from infection import Infection
from utility.interactivePlot import InteractivePlot
from centralInstitutionNode import CentralInstitutionNode as CI
from utility.utils import Utils
import parameters as P
import matplotlib.pyplot as plt


class CentralInstitutionExperiment(MultiPhaseExperimentSkeleton):
    """
    Experiment to measure the effect of a central institution on infection spread.
    
    Phase 1: Run infection simulation without central institution
    Phase 2: Add central institution and continue simulation
    """
    
    def __init__(self):
        super().__init__()
        self.infection_model = Infection()
        self.G = None
    
    def setup_phase1(self):
        """Initialize the graph for phase 1 (no central institution)."""
        init_sim = BasicSimSetup()
        print("Setting up initial network...")
        init_sim.setup_basic_simulation(central_institution_toggle=False)
        self.G = init_sim.G
        
        print("**Initial network setup**")
        print(f"  Number of nodes: {len(self.G.nodes())}")
        print(f"  Average degree: {Utils.average_degree(self.G):.2f}")
        print(f"  Initially infected nodes: {int(P.PERCENTAGE_OF_INFECTED_NODES * len(self.G.nodes()))}")
        print(f"  Infection threshold: {P.INFECTION_THRESHOLD * 100}%")
    
    def run_phase1(self):
        """Run phase 1 simulation without central institution."""
        print("Running infection simulation (Phase 1: no central institution)...")
        self.phase1_states, self.layout = self.infection_model.run_simulation(
            G=self.G,
            iterations=P.NUM_ITERATIONS,
            seed=P.RANDOM_SEED,
            central_institution_toggle=False
        )
        self.states = self.phase1_states.copy()
    
    def setup_phase2(self):
        """Add central institution to the graph."""
        print("Adding central institution...")
        CI.add_central_institution(
            self.G,
            list(self.G.nodes()),
            P.CENTRAL_INSTITUTION_CONNECTION_PERCENTAGE
        )
        ci_connections = len(list(self.G.neighbors('CENTRAL_INSTITUTION')))
        print(f"  Central institution connected to {ci_connections} nodes")
    
    def run_phase2(self):
        """Run phase 2 simulation with central institution."""
        self.phase2_states, _ = self.infection_model.run_simulation(
            G=self.G,
            iterations=P.NUM_ITERATIONS,
            seed=P.RANDOM_SEED,
            central_institution_toggle=True,
            first_phase_2=True
        )
        self.states.extend(self.phase2_states)
    
    def has_converged(self):
        """Check if phase 1 has converged."""
        infected_counts = self._get_infected_counts(self.phase1_states)
        target_infectable = len(self.G.nodes())
        
        if not infected_counts:
            return False
        if infected_counts[-1] == target_infectable:
            return True
        
        converged = (len(infected_counts) >= 3 and
                    infected_counts[-1] == infected_counts[-2] == infected_counts[-3])
        
        if converged:
            print(f"**Phase 1 Result**: Converged at {infected_counts[-1]}/{target_infectable} infected nodes.")
        else:
            print(
                "**Phase 1 Result**: Did not converge. "
                f"Reached {infected_counts[-1]}/{target_infectable} infected nodes. "
                "Increase NUM_ITERATIONS to potentially reach convergence before phase 2."
            )
        
        return converged
    
    @staticmethod
    def _get_infected_counts(states):
        """Count infected nodes (excluding central institution) at each state."""
        return [
            sum(
                1 for node in graph.nodes()
                if graph.nodes[node].get('infected', False)
                and not graph.nodes[node].get('is_central_institution', False)
            )
            for graph, _ in states
        ]
    
    def print_results(self):
        """Print summary statistics."""
        print("\n**Infected Nodes Over Time (Phase 1)**")
        phase1_counts = self._get_infected_counts(self.phase1_states)
        print(f"  Start: {phase1_counts[0]} infected")
        print(f"  Final: {phase1_counts[-1]} infected")
        
        if self.phase2_states:
            print("\n**Infected Nodes Over Time (Phase 2)**")
            phase2_counts = self._get_infected_counts(self.phase2_states)
            print(f"  Start: {phase2_counts[0]} infected")
            print(f"  Final: {phase2_counts[-1]} infected")
    
    def visualize(self, show_plot=True):
        """Visualize the simulation states."""
        interactive = InteractivePlot(states=self.states, layout=self.layout)
        interactive.draw_current()
        if show_plot and P.SHOW_PLOT:
            print("Rendering interactive plot...")
            plt.show()


def main():
    """Run the central institution experiment."""
    experiment = CentralInstitutionExperiment()
    experiment.execute(show_plot=P.SHOW_PLOT)


if __name__ == "__main__":
    main()