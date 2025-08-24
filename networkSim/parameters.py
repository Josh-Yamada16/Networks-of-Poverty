# Stingy Parameters
STINGY_ENABLED = True
STINGY_MAX_BEHAVIORS = 3
STINGY_AVG_LOSS_PCT = 0.1
STINGY_WINDOW = 4

# Parameters for Main
SHOW_PLOT = True  # Whether to show the plot at the end of the simulation
DRAW_INITIAL_GRAPH = False # Whether to draw the initial graph
CONTROL_RANDOM_SEED = False  # Whether to control random seed for reproducibility

# Parameters for Simulation
NUM_ITERATIONS = 20  # Number of iterations for the token exchange simulation
LAYOUT = "spring"  # Layout for the graph visualization (e.g., "spring", "circular")

# Parameters for Graph Generation
NUM_NODES = 10  # Number of nodes in the graph
GRAPH_TYPE = "dir"  # Type of graph to generate (e.g., "erd", "wat", "bara", "cir", "lat", "barb", "sto", "reg")
CUSTOM_GRAPH = {
    0: [1],
    1: [0, 2],
    2: [0, 3],
    3: [0, 4],
    4: [0, 5],
    5: [0]
}
CUSTOM_MONEY = [1, 0, 0, 0, 0, 0]  # Custom money distribution for the custom graph

BLOCK_MEANS = {0: 100, 1: 200, 2: 50, 3: 400, 4: 500}
STD_DEV = 15  # Standard deviation for money distribution in stochastic block model

RANDOMIZE_WEIGHTS = False  # Whether to randomize edge weights in the edge matrix

# Parameters for Stochastic Block Model
STOCHASTIC_BLOCKS = 4
INTRA_BLOCK_PROB_LOW = 0.4  # Probability of edges within a block
INTRA_BLOCK_PROB_HIGH = 0.7  # Probability of edges within a block
EXTRA_BLOCK_PROB_LOW = 0.01  # Probability of edges between blocks
EXTRA_BLOCK_PROB_HIGH = 0.2  # Probability of edges between blocks

KEEP_LOW = 0.2
KEEP_HIGH = 0.4


# Parameters for Utils
PRINT_PERCENT_CHANGE = False  # Whether to print percent changes in money distribution
