"""
Base experiment skeleton for running, printing results, and visualizing simulations.
Subclass this to create new experiments with different setups and configurations.
"""
from abc import ABC, abstractmethod
import matplotlib.pyplot as plt


class ExperimentSkeleton(ABC):
    """Abstract base class for defining and running experiments."""
    
    def __init__(self):
        """Initialize the experiment. Override in subclasses if needed."""
        self.results = {}
        self.states = []
        self.layout = None
    
    @abstractmethod
    def setup(self):
        """
        Set up the experiment (initialize graph, parameters, etc).
        Should populate self.G and other needed attributes.
        """
        pass
    
    @abstractmethod
    def run(self):
        """
        Run the simulation. 
        Should populate self.states and self.layout.
        """
        pass
    
    @abstractmethod
    def print_results(self):
        """Print results and statistics from the simulation."""
        pass
    
    @abstractmethod
    def visualize(self, show_plot=True):
        """
        Visualize the results.
        
        Args:
            show_plot: Whether to display the plot
        """
        pass
    
    def execute(self, show_plot=True):
        """
        Execute the full experiment pipeline: setup → run → print → visualize.
        
        Args:
            show_plot: Whether to display plots at the end
        """
        print("=" * 50)
        print(f"Starting experiment: {self.__class__.__name__}")
        print("=" * 50)
        
        print("\n[1/4] Setting up experiment...")
        self.setup()
        
        print("[2/4] Running simulation...")
        self.run()
        
        print("[3/4] Printing results...")
        self.print_results()
        
        print("[4/4] Visualizing results...")
        self.visualize(show_plot=show_plot)
        
        print("=" * 50)
        print(f"Experiment complete: {self.__class__.__name__}")
        print("=" * 50)


class MultiPhaseExperimentSkeleton(ExperimentSkeleton):
    """Extended skeleton for multi-phase experiments (e.g., before/after intervention)."""
    
    def __init__(self):
        super().__init__()
        self.phase1_states = []
        self.phase2_states = []
        self.phase1_converged = False
    
    @abstractmethod
    def setup_phase1(self):
        """Set up phase 1 (baseline scenario)."""
        pass
    
    @abstractmethod
    def run_phase1(self):
        """Run phase 1 simulation."""
        pass
    
    @abstractmethod
    def setup_phase2(self):
        """Set up phase 2 (with intervention). Only run if phase 1 converges."""
        pass
    
    @abstractmethod
    def run_phase2(self):
        """Run phase 2 simulation."""
        pass
    
    @abstractmethod
    def has_converged(self):
        """Determine if phase 1 has converged and phase 2 should run."""
        pass
    
    def setup(self):
        """Setup phase 1."""
        self.setup_phase1()
    
    def run(self):
        """Run phase 1, check convergence, optionally run phase 2."""
        self.run_phase1()
        
        if self.has_converged():
            print("[Phase 2] Convergence detected. Setting up phase 2...")
            self.setup_phase2()
            print("[Phase 2] Running phase 2 simulation...")
            self.run_phase2()
        else:
            print("[Phase 1] Did not converge. Phase 2 skipped.")
