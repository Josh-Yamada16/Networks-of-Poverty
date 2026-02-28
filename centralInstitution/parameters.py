# Parameters for Main
SHOW_PLOT = True  # Whether to show the plot at the end of the simulation
CONTROL_RANDOM_SEED = True  # Whether to control random seed for reproducibility
RANDOM_SEED = 42  # Random seed for reproducibility
GENERATE_LEDGER = True  # Whether to generate a ledger of transactions
MAX_STINGY_BEHAVIORS = 100  # Maximum number of stingy behaviors allowed in the simulation
NUM_ITERATIONS = 10  # Number of iterations for the token exchange simulation
LAYOUT = "spring"  # Layout for the graph visualization (e.g., "spring", "circular")
DRAW_INITIAL_GRAPH = True # Whether to draw the initial graph

# Parameters for Graph Generation
NUM_NODES = 100  # Number of nodes in the graph (matching your custom graph)
GRAPH_TYPE = "sto"  # Type of graph to generate (e.g., "erd", "wat", "bara", "cir", "lat", "barb", "sto", "reg")
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
INTRA_BLOCK_PROB_LOW = 0.6  # Probability of edges within a block
INTRA_BLOCK_PROB_HIGH = 0.9  # Probability of edges within a block
EXTRA_BLOCK_PROB_LOW = 0.01  # Probability of edges between blocks
EXTRA_BLOCK_PROB_HIGH = 0.04  # Probability of edges between blocks

KEEP_LOW = 0.2
KEEP_HIGH = 0.4

# Parameters for Central Institution
CENTRAL_INSTITUTION_CONNECTIONS = 0.3  # Fraction of early adopter nodes that the central institution connects to

# Parameters for Infection
INFECTION_THRESHOLD = 0.3  # Fraction of neighbors that must be infected for a node to become infected

# Parameters for Basic Setup
CENTRAL_INSTITUTION_TOGGLE = True  # Whether to add a central institution and spread behavior_b at the start of the simulation
INIT_INFECTED_NODES = 5  # Number of nodes to initially infect with behavior_b at the start of the simulation
PURE_RANDOMIZED_INITIAL_INFECTION = True  # Whether to randomly select initial infected nodes from the entire graph
BLOCK_RANDOMIZED_INITIAL_INFECTION = False  # Whether to randomly select a block and then
DISPERSED_BLOCK_INITIAL_INFECTION = False  # Whether to randomly select nodes from different blocks for initial infection

# Parameters for Utils
PRINT_PERCENT_CHANGE = False  # Whether to print percent changes in money distribution
