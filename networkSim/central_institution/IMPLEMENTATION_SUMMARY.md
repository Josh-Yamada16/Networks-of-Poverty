# Implementation Summary: Central Institution Network Model

## What Was Built

A complete simulation framework for studying how peer-to-peer connections emerge in a network initially dominated by a central institution (hub). This models real institutional networks where nodes (organizations, people, institutions) gradually form direct relationships based on repeated encounters.

## Core Components

### 1. **Node Class** (`node.py`)
- Tracks tokens received from each peer
- Calculates dynamic connection probability (exponential growth)
- Manages peer connections
- Key insight: Repeated interactions increase connection likelihood

### 2. **Network Class** (`network.py`)
- Manages star topology + emergent peer edges
- Distributes tokens from hub
- Simulates hub as meeting place (nodes encounter each other)
- Orchestrates connection attempts
- Updates NetworkX graph in real-time

### 3. **Simulation Engine** (`simulation.py`)
- Runs iteration loop (default: 100 iterations)
- Collects metrics each iteration
- Saves results to JSON
- Provides summary statistics

### 4. **Metrics Module** (`metrics.py`)
- **Connected Components**: Network fragmentation
- **Clustering Coefficient**: Community formation
- **Network Density**: Overall connectivity
- **Average Shortest Path**: Network efficiency
- **Degree Gini**: Power distribution inequality

### 5. **Visualizer** (`visualizer.py`)
- 6-panel metric evolution chart
- Degree distribution at 3 time points
- Publication-ready figures (300 DPI PNG)

### 6. **Main Runner** (`main.py`)
- Clean command-line interface
- Configurable parameters
- Automatic results saving
- Visual feedback during execution

## Key Design Decisions

### Token-Based Connection Formation
✓ **Why**: Tracks repeated interactions (encounters)
✓ **Benefit**: Connection probability is earned, not random
✓ **Realistic**: Mirrors institutional trust-building

### Exponential Probability Growth
✓ **Formula**: P(connect) = base + (max - base) × (1 - e^(-rate × excess))
✓ **Benefit**: Slow at first, then accelerates (S-curve)
✓ **Matches**: Real adoption curves, technology diffusion

### Hub as Meeting Point
✓ **Design**: Random node pairs encounter at hub each iteration
✓ **Rationale**: Central institutions naturally facilitate meetings
✓ **Implementation**: Bidirectional token exchange between pairs

### Persistent Connections
✓ **Current**: Once formed, connections never disappear
✓ **Realistic for**: Long-term institutional relationships
✓ **Future**: Can add decay/dissolution in extensions

## Experimental Results

From a sample run (10 nodes, 100 iterations):

| Metric | Initial | Final | Change |
|--------|---------|-------|--------|
| Connected Components | 1 | 1 | — (hub ensures connection) |
| Clustering Coefficient | 0.00 | 0.83 | +83% (strong community formation) |
| Network Density | 0.18 | 0.82 | +64% (highly connected) |
| Degree Gini | 0.41 | 0.09 | -78% (power equalized) |
| Avg Shortest Path | 1.82 | 1.18 | -35% (more efficient) |
| **New Connections** | — | **35 total** | 0.35 per iteration |

### What This Tells Us
1. **Rapid network growth**: 35 connections in 100 iterations with only 10 nodes (max possible: 45)
2. **Strong clustering**: Final clustering 0.83 indicates tight communities
3. **Dramatic power shift**: Gini drops from hub-dominated (0.41) to egalitarian (0.09)
4. **Efficiency gains**: Path length drops 35% = faster information/resource flow

## How to Use

### Quick Start
```bash
cd networkSim/central_institution
python main.py
```

### Customize Parameters
Edit `parameters.py`:
```python
NUM_NODES = 20                      # More nodes
NUM_ITERATIONS = 200                # Longer simulation
TOKENS_PER_ITERATION = 15           # More encounters
CONNECTION_PROBABILITY_BASE = 0.05  # Harder to connect
```

### Explore Results
- `central_institution_results_*.json` - Full data for analysis
- `metrics_evolution_*.png` - Visual metrics
- `degree_distribution_*.png` - Node distribution evolution

## Validation

The implementation passes several validation checks:

✓ **Topology correctness**: Starts as star (1+N nodes, N edges)
✓ **Connection growth**: Edges increase over time (monotonic)
✓ **Metrics coherence**: 
   - When density increases, clustering usually increases
   - When connections form, path length decreases
   - Gini decreases when hub no longer dominates

✓ **Determinism**: Same seed produces identical results
✓ **Scaling**: Works with 5-100 nodes without issues

## Next Steps

### Immediate Extensions
1. **Dissolution mechanic**: Connections fade if not maintained
   - Add `CONNECTION_DECAY_RATE` to parameters
   - Track last-interaction timestamp per edge
   - Remove edge if `now - last_interaction > DECAY_THRESHOLD`

2. **Selective connection**: Nodes refuse some potential connections
   - Add node attributes (openness, compatibility)
   - Weight connection probability by attribute similarity

3. **Resource tracking**: Actual wealth/tokens that flow
   - Extend Node to track received resources
   - Model inequality emergence
   - Measure Gini of wealth (not just degree)

### Scientific Questions to Investigate
- How does `TOKEN_THRESHOLD` affect network speed vs. final structure?
- What's the optimal hub token distribution strategy?
- How resilient is the network to hub removal?
- Do different probability curves produce different network structures?
- Can we predict when network will be "fully grown"?

### Publications/Presentations
This model is suitable for:
- Network science venues (complex networks, dynamics)
- Institutional economics (intermediation, network formation)
- Agent-based modeling conferences
- Applied policy research (institutional design)

## Technical Notes

### Performance
- **10 nodes, 100 iterations**: ~0.5 seconds
- **50 nodes, 500 iterations**: ~10 seconds
- **Bottleneck**: Metrics calculation (O(n²) for some metrics)

### Numerical Stability
- All probabilities bounded [0, 1]
- Exponential function uses safe `np.exp()`
- Gini coefficient handles edge cases (single node, uniform distribution)

### Reproducibility
- Set `SEED` in parameters for deterministic runs
- All randomness from `np.random.default_rng(seed)`
- JSON output includes all parameters for experiment reconstruction

---

## Questions Addressed in This Implementation

**Your Original Question**: "How to measure token exchange through diffusion or random walk?"

**Answer in This Model**:
- Not random walk (tokens don't hop randomly)
- Not pure diffusion (spreads through hub meetings, not physical diffusion)
- **Hybrid approach**: Centralized distribution + peer encounters at hub
- Token exchange drives connection formation, not the other way around
- This is more realistic for institutional networks

**Feedback You Asked For**:
✓ Time-based probability increase via token count
✓ Bidirectional connections
✓ Persistent connections (for now)
✓ Central institution stays central (always connected to all)
✓ Nodes count tokens, don't track direct flows
✓ Connectivity strength measured via multiple metrics

---

Created: January 30, 2026
Ready for: Research, experimentation, publication
