# Configuration parameters for central institution experiment

# Simulation Parameters
NUM_NODES = 10  # Number of peripheral nodes (excludes central institution)
NUM_ITERATIONS = 100  # Number of iterations to run
SEED = 42  # Random seed for reproducibility

# Token Parameters
TOKENS_PER_ITERATION = 10  # Number of tokens central institution sends per iteration
TOKEN_THRESHOLD = 5  # Number of tokens needed to reach base probability
CONNECTION_PROBABILITY_BASE = 0.1  # Base probability when threshold is met
CONNECTION_PROBABILITY_MAX = 0.9  # Maximum connection probability
TOKEN_ACCUMULATION_RATE = 0.2  # Probability increase per token beyond threshold (scaled exponentially)

# Visualization Parameters
PLOT_METRICS = True  # Whether to plot metrics over time
SAVE_RESULTS = True  # Whether to save results to file
RESULTS_FILE = "central_institution_results.json"
