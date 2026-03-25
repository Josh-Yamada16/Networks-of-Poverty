# Parameters for Main
NUM_ITERATIONS = 15  # Number of iterations for the token exchange simulation
LAYOUT = "spring"  # Layout for the graph visualization (e.g., "spring", "circular")
CONTROL_RANDOM_SEED = False  # Whether to control random seed for reproducibility
RANDOM_SEED = 43  # Random seed for reproducibility
DRAW_INITIAL_GRAPH = True # Whether to draw the initial graph
SHOW_PLOT = True  # Whether to show the plot at the end of the simulation

# Parameters for Central Institution
CENTRAL_INSTITUTION_CONNECTION_PERCENTAGE = 0.15  # Fraction of early adopter nodes that the central institution connects to

# Parameters for Infection
INFECTION_THRESHOLD = 0.45  # Fraction of neighbors that must be infected for a node to become infected

# Parameters for Basic Setup
CENTRAL_INSTITUTION_TOGGLE = True  # Whether to add a central institution and spread infected at the start of the simulation
PERCENTAGE_OF_INFECTED_NODES = 0.3  # Percentage of nodes that are initially infected (between 0 and 1)

INITIAL_INFECTION_TYPE = 0  # Type of initial infection strategy (0: Pure Randomized, 1: Block Randomized, 2: Dispersed Block Randomized)
INITIAL_INFECTION_TYPE_DICTIONARY = {
    "PURE_RANDOMIZED_INITIAL_INFECTION": 0,  # Whether to randomly select initial infected nodes from the entire graph
    "BLOCK_RANDOMIZED_INITIAL_INFECTION": 1,  # Whether to randomly select a block and then randomly select initial infected nodes from that block
    "DISPERSED_BLOCK_INITIAL_INFECTION": 2  # Whether to randomly select nodes from different blocks for initial infection
}

# Parameters for Graph Generation
NUM_NODES = 200  # Number of nodes in the graph (matching your custom graph)
GRAPH_TYPE = "sto"  # Type of graph to generate (e.g., "erd", "wat", "bara", "cir", "lat", "barb", "sto", "reg")

CUSTOM_MONEY = [100, 50, 75, 200, 150, 80, 120, 90, 60, 110, 130, 70]  # Custom money distribution for the custom graph (12 nodes)

BLOCK_MEANS = {0: 100, 1: 200, 2: 50, 3: 400, 4: 500}
STD_DEV = 15  # Standard deviation for money distribution in stochastic block model

RANDOMIZE_WEIGHTS = False  # Added to fix missing parameter error

# Parameters for Stochastic Block Model
STOCHASTIC_BLOCKS = 4
INTRA_BLOCK_PROB_LOW = 0.1  # Probability of edges within a block
INTRA_BLOCK_PROB_HIGH = 0.3  # Probability of edges within a block
EXTRA_BLOCK_PROB_LOW = 0.1  # Probability of edges between blocks
EXTRA_BLOCK_PROB_HIGH = 0.3  # Probability of edges between blocks

# SBM structure mode
# "random": standard nx.stochastic_block_model
# "hub_leaf": higher modularity + lower degree assortativity pattern inside blocks
SBM_STRUCTURE_MODE = "hub_leaf"

# Hub-leaf SBM controls (used only when SBM_STRUCTURE_MODE == "hub_leaf")
SBM_HUB_FRACTION = 0.12
SBM_HUB_LEAF_PROB = 0.65
SBM_HUB_HUB_PROB = 0.10
SBM_LEAF_LEAF_PROB = 0.03
SBM_INTER_BLOCK_PROB_SCALE = 0.25

