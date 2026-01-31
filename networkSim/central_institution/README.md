# Central Institution Network Experiment

## Overview

This experiment models the **emergence of peer-to-peer connections** in a network that starts as a star topology (all peripheral nodes connected only to a central hub/institution). As nodes encounter each other through the hub and exchange tokens, they develop higher probability of forming direct peer connections based on their interaction history.

## Motivation

This model addresses real-world institutional networks where:
- A central institution (gatekeeper) initially mediates all interactions
- Nodes encounter each other through the hub (e.g., at meetings, events)
- Repeated encounters increase trust and probability of peer relationships
- Over time, the network evolves from centralized to decentralized

**Real-world applications:**
- Institutional networks in poverty alleviation
- Corporate organizational networks
- Community institutions facilitating resource exchange
- Academic collaboration networks

## Model Design

### Network Topology

**Initial State (Iteration 0):**
- Star topology: 1 central hub + N peripheral nodes
- Only hub-peripheral edges (all nodes connected to hub only)
- No peer-to-peer connections

**Dynamic Evolution:**
- Nodes encounter each other at the hub
- Each encounter is tracked as a "token received from peer X"
- When encounter count exceeds threshold, connection probability increases
- Connections, once formed, persist forever

### Mechanism: Token Exchange & Connection Formation

#### Phase 1: Token Distribution (each iteration)
1. Central hub sends **K tokens** to random peripheral nodes
2. Random pairs of nodes encounter at the hub and exchange tokens
   - Each pair exchanges tokens bidirectionally
   - This simulates meetings/interactions at the hub

#### Phase 2: Connection Probability Calculation
For each node tracking tokens from peer X:
- **Below threshold**: 0% chance of connection
- **At threshold (T tokens)**: Base probability (e.g., 10%)
- **Above threshold**: Probability increases exponentially toward maximum

Formula:
```
P(connect to X) = base + (max - base) × (1 - e^(-rate × excess_tokens))
```

Where:
- `base` = CONNECTION_PROBABILITY_BASE
- `max` = CONNECTION_PROBABILITY_MAX
- `rate` = TOKEN_ACCUMULATION_RATE
- `excess_tokens` = token_count - TOKEN_THRESHOLD

#### Phase 3: Attempt Connections
- Each node checks each peer it's received tokens from
- If threshold met, rolls probability dice
- If successful, bidirectional edge is added to graph
- Once connected, edge persists

#### Phase 4: Existing Peer Exchanges
- Connected peers exchange tokens with 50% probability each iteration
- This maintains interaction history between connected nodes

## Configuration Parameters

Located in `parameters.py`:

```python
NUM_NODES = 10                          # Peripheral nodes (excludes hub)
NUM_ITERATIONS = 100                    # Simulation iterations
TOKENS_PER_ITERATION = 10               # Hub tokens per iteration
TOKEN_THRESHOLD = 5                     # Encounters needed for base probability
CONNECTION_PROBABILITY_BASE = 0.1       # Probability at threshold
CONNECTION_PROBABILITY_MAX = 0.9        # Maximum connection probability
TOKEN_ACCUMULATION_RATE = 0.2           # Exponential rate of increase
SEED = 42                               # Random seed for reproducibility
PLOT_METRICS = True                     # Generate visualizations
SAVE_RESULTS = True                     # Save JSON results
```

### Tuning the Model

**To get faster network growth:**
- Decrease `TOKEN_THRESHOLD` (fewer encounters needed)
- Increase `CONNECTION_PROBABILITY_BASE` (higher starting probability)
- Increase `TOKEN_ACCUMULATION_RATE` (probability grows faster)
- Increase `TOKENS_PER_ITERATION` (more encounters)

**To get slower, more realistic growth:**
- Increase `TOKEN_THRESHOLD`
- Decrease `CONNECTION_PROBABILITY_BASE`
- Decrease `TOKEN_ACCUMULATION_RATE`
- Decrease `TOKENS_PER_ITERATION`

## Metrics Tracked

### 1. Connected Components
- **Meaning**: Number of disconnected subgraphs
- **Ideal**: 1 (entire network connected)
- **Higher values**: Indicate fragmentation
- **Interpretation**: With hub always present, should stay at 1

### 2. Clustering Coefficient
- **Meaning**: Probability that two neighbors of node A are also connected
- **Range**: 0-1
- **Initial**: 0 (star has no triangles)
- **Expected evolution**: Increases as peer connections form
- **Interpretation**: Shows emergence of tight-knit communities

### 3. Network Density
- **Meaning**: Ratio of actual edges to possible edges
- **Range**: 0-1 (1 = complete graph)
- **Initial**: ~0.18 (for 10 nodes: 10 edges / 45 possible)
- **Expected evolution**: Increases toward 1
- **Interpretation**: Network becomes increasingly "filled in"

### 4. Average Shortest Path Length
- **Meaning**: Average minimum steps between any two nodes
- **Initial**: ~1.8 (all paths go through hub)
- **Expected evolution**: Decreases as shortcuts form
- **Interpretation**: Network becomes more efficient for information/resource flow

### 5. Degree Distribution Gini Coefficient
- **Meaning**: Inequality in node connectivity
- **Range**: 0-1 (0 = perfect equality, 1 = perfect inequality)
- **Initial**: ~0.41 (hub has n-1 connections, others have 1)
- **Expected evolution**: Decreases (power decentralizes)
- **Interpretation**: Initially hub-centric, evolves toward egalitarian

### 6. New Peer Connections per Iteration
- **Meaning**: Number of new peer edges formed each iteration
- **Pattern**: Usually peaks early, then decreases as network fills
- **Interpretation**: Shows phase of network evolution

## Running the Experiment

### Basic Execution
```bash
cd networkSim/central_institution
python main.py
```

### Output

**Console Output:**
- Iteration-by-iteration metrics every 10 iterations
- Final summary statistics
- File locations for saved results

**Generated Files:**
1. `central_institution_results_TIMESTAMP.json` - Complete metrics history
2. `metrics_evolution_TIMESTAMP.png` - 6-panel metric visualization
3. `degree_distribution_TIMESTAMP.png` - Degree distribution at 3 time points

### Interpreting Results

**Successful network evolution shows:**
✓ Connected Components = 1 (always, due to hub)
✓ Clustering Coefficient: 0 → high value (community formation)
✓ Network Density: 0.18 → higher value (increased connectivity)
✓ Degree Gini: 0.41 → lower value (power equalization)
✓ Avg Path Length: 1.8 → lower value (efficiency gains)
✓ Many new connections early, declining over time

## Key Findings & Insights

1. **Hub as Intermediary**
   - Central institution remains essential for initial network formation
   - Once peer connections established, hub becomes less critical
   - Network evolves from centralized to distributed

2. **Emergence of Communities**
   - Clustering coefficient increases sharply once first connections form
   - Suggests natural formation of tight-knit sub-groups
   - Power law dynamics: early connections enable more

3. **Power Dynamics**
   - Initial inequality (hub dominates) decreases over time
   - Final network more egalitarian in node degrees
   - However, hub retains slight advantage (always connected to all)

4. **Network Efficiency**
   - Path lengths decrease significantly
   - Network becomes more efficient for resource/information flow
   - Reflects real-world benefit of peer connections

## Extensions & Future Work

### Possible Enhancements

1. **Connection Dissolution**
   - Connections fade if no recent interaction
   - Implement: decay connections if token exchange gaps too long
   - Parameter: `CONNECTION_DECAY_RATE`

2. **Heterogeneous Nodes**
   - Different threshold levels per node
   - Different probability functions
   - Reflects varying trust/openness levels

3. **Resource Flow**
   - Track actual resources (not just tokens counted)
   - Model wealth/resource concentration
   - Measure inequality in final distribution

4. **Hub Competition**
   - Multiple hubs competing for nodes
   - Hub might fail or be replaced
   - Reflects institutional competition

5. **Selective Connection**
   - Nodes choose not to connect with certain peers
   - Weighted probability based on peer attributes
   - Reflects homophily/assortativity

6. **Temporal Dynamics**
   - Vary token distribution over time
   - Seasonal patterns
   - Shock events affecting network

## File Structure

```
central_institution/
├── __init__.py                          # Package initialization
├── parameters.py                        # Configuration parameters
├── node.py                              # Node class (tracks tokens, probability)
├── network.py                           # Network management
├── simulation.py                        # Main simulation engine
├── metrics.py                           # Metrics calculations
├── visualizer.py                        # Plotting and visualization
├── main.py                              # Entry point
└── README.md                            # This file
```

## Class Descriptions

### Node
- Tracks token count from each peer
- Calculates connection probability
- Manages peer connections

### CentralInstitutionNetwork
- Manages graph structure
- Coordinates token distribution
- Tracks connection formation

### CentralInstitutionSimulation
- Orchestrates iteration loop
- Collects metrics
- Manages results

### SimulationVisualizer
- Plots metrics over time
- Visualizes degree distribution evolution
- Generates publication-ready figures

### NetworkMetrics
- Calculates all graph statistics
- Handles disconnected graph edge cases
- Provides metric aggregation

## Dependencies

- `networkx`: Graph structures and algorithms
- `numpy`: Numerical operations
- `matplotlib`: Visualization

## References

This model integrates concepts from:
- **Network science**: Star topologies, phase transitions
- **Agent-based modeling**: Individual decision-making
- **Institutional economics**: Role of intermediaries
- **Social network analysis**: Emergence and evolution

---

**Last Updated**: January 30, 2026
**Maintained By**: [Your Name]
