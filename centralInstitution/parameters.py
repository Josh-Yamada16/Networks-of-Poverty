# Stingy Parameters
STINGY_MAX_BEHAVIORS = 3
STINGY_AVG_LOSS_PCT = 0.1
STINGY_WINDOW = 4

# Parameters for Main
SHOW_PLOT = True  # Whether to show the plot at the end of the simulation
CONTROL_RANDOM_SEED = False  # Whether to control random seed for reproducibility
GENERATE_LEDGER = True  # Whether to generate a ledger of transactions
MAX_STINGY_BEHAVIORS = 100  # Maximum number of stingy behaviors allowed in the simulation
NUM_ITERATIONS = 40  # Number of iterations for the token exchange simulation
LAYOUT = "spring"  # Layout for the graph visualization (e.g., "spring", "circular")
DRAW_INITIAL_GRAPH = True # Whether to draw the initial graph

# Parameters for Graph Generation
NUM_NODES = 12  # Number of nodes in the graph (matching your custom graph)
GRAPH_TYPE = "custom"  # Type of graph to generate (e.g., "erd", "wat", "bara", "cir", "lat", "barb", "sto", "reg")
CUSTOM_GRAPH = {
    'a': ['e', 'f'],
    'b': ['a'],
    'c': ['d', 'e'],
    'd': ['h', 'i'],
    'e': ['d'],
    'f': ['b', 'c'],
    'g': ['d'],
    'h': ['i'],
    'i': ['l'],
    'j': ['f', 'h', 'k'],
    'k': ['i', 'j'],
    'l': ['g']
}
CUSTOM_MONEY = [100, 50, 75, 200, 150, 80, 120, 90, 60, 110, 130, 70]  # Custom money distribution for the custom graph (12 nodes)

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
