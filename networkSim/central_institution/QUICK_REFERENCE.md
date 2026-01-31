# Quick Reference: Central Institution Experiment

## Run Experiment
```bash
cd networkSim/central_institution
python main.py
```

## Outputs Generated
```
central_institution_results_YYYYMMDD_HHMMSS.json    # Full data
metrics_evolution_YYYYMMDD_HHMMSS.png               # 6 metrics over time
degree_distribution_YYYYMMDD_HHMMSS.png             # Degree evolution
```

## Key Metrics at a Glance

| Metric | Meaning | Direction | Range |
|--------|---------|-----------|-------|
| Connected Components | Network fragmentation | ↓ Lower = Better | 1+ |
| Clustering | Community formation | ↑ Higher = Better | 0-1 |
| Density | Overall connectivity | ↑ Higher = Better | 0-1 |
| Avg Path Length | Network efficiency | ↓ Lower = Better | 1+ |
| Degree Gini | Power inequality | ↓ Lower = Better | 0-1 |

## Typical Evolution Pattern

```
Iteration  Components  Clustering  Density  Gini    New Connections
───────────────────────────────────────────────────────────────────
0          1           0.00        0.18     0.41    —
10         1           0.00        0.18     0.41    0
20         1           0.10        0.22     0.38    1-2
30         1           0.25        0.35     0.30    2-3
40         1           0.40        0.45     0.22    2-3
50         1           0.55        0.55     0.15    1-2
...
100        1           0.80+       0.80+    0.08    Tapering off
```

## Parameter Presets

### Conservative (Slow Growth)
```python
TOKEN_THRESHOLD = 8
CONNECTION_PROBABILITY_BASE = 0.05
CONNECTION_PROBABILITY_MAX = 0.6
TOKEN_ACCUMULATION_RATE = 0.1
TOKENS_PER_ITERATION = 5
```

### Moderate (Balanced)
```python
TOKEN_THRESHOLD = 5
CONNECTION_PROBABILITY_BASE = 0.1
CONNECTION_PROBABILITY_MAX = 0.9
TOKEN_ACCUMULATION_RATE = 0.2
TOKENS_PER_ITERATION = 10
```

### Aggressive (Rapid Growth)
```python
TOKEN_THRESHOLD = 3
CONNECTION_PROBABILITY_BASE = 0.2
CONNECTION_PROBABILITY_MAX = 0.95
TOKEN_ACCUMULATION_RATE = 0.4
TOKENS_PER_ITERATION = 15
```

## Expected Results by Preset

**Conservative**
- Slower peer connection formation
- More gradual metrics changes
- Final network less dense
- Use for: studying resistance/barriers to connection

**Moderate** (Default)
- Balanced growth trajectory
- Clear S-curve in metrics
- Realistic connection rates
- Use for: baseline behavior understanding

**Aggressive**
- Rapid network densification
- Fast clustering growth
- Near-complete network possible
- Use for: testing algorithm robustness

## Common Analysis Questions

### "Why aren't peer connections forming?"
**Check:**
- Is `TOKEN_THRESHOLD` too high?
- Is `CONNECTION_PROBABILITY_BASE` too low?
- Run with `TOKENS_PER_ITERATION` increased to 20+

### "Network filled too fast - want slower growth?"
**Solutions:**
- Increase `TOKEN_THRESHOLD` (need more encounters)
- Decrease `CONNECTION_PROBABILITY_BASE` (harder to connect)
- Decrease `TOKEN_ACCUMULATION_RATE` (slower probability growth)
- Decrease `TOKENS_PER_ITERATION` (fewer encounters)

### "How to test robustness?"
**Variations:**
```python
for threshold in [3, 5, 8, 10]:
    for base_prob in [0.05, 0.1, 0.2]:
        # Run simulation with these parameters
        # Track: time-to-full-connection, final structure, stability
```

### "What does final structure tell us?"
- **High clustering**: Natural sub-communities form
- **Low Gini**: Power decentralizes successfully
- **Low path length**: Efficient information flow
- **Interpretation**: Peer connections are functionally valuable

## Troubleshooting

| Problem | Likely Cause | Solution |
|---------|-------------|----------|
| No connections forming | Thresholds too high | Lower TOKEN_THRESHOLD or increase TOKENS_PER_ITERATION |
| Network completely filled by iteration 30 | Parameters too aggressive | Increase TOKEN_THRESHOLD, decrease TOKENS_PER_ITERATION |
| Metrics look noisy | Randomness or too few nodes | Increase NUM_NODES or increase NUM_ITERATIONS |
| Slow to run | Network too large | Reduce NUM_NODES or NUM_ITERATIONS |

## Understanding the Probability Curve

```
Connection Probability vs Tokens Received
(with base=0.1, max=0.9, rate=0.2, threshold=5)

   1.0 |                         ___________
   0.9 |                      /
   0.8 |                    /
   0.7 |                  /
   0.6 |               /
   0.5 |             /
   0.4 |          /
   0.3 |       /
   0.2 |    /
   0.1 |__/________________  (base probability)
   0.0 |________________________
       0  5 10 15 20 25 30 (tokens)
          ↑
        threshold
```

Key points:
- Below 5 tokens: 0% chance
- At 5 tokens: 10% chance (base)
- At 10 tokens: ~43% chance
- At 15 tokens: ~70% chance
- At 20+ tokens: 90% chance (max)

## Interpreting JSON Results

```json
{
  "simulation_params": {
    "num_nodes": 10,
    "num_iterations": 100,
    "tokens_per_iteration": 10,
    ...
  },
  "initial_metrics": {
    "connected_components": 1,
    "clustering_coefficient": 0.0,
    "network_density": 0.1818,
    ...
  },
  "final_metrics": {
    "connected_components": 1,
    "clustering_coefficient": 0.8307,
    "network_density": 0.8182,
    ...
  },
  "metrics_history": [
    { iteration 0 metrics },
    { iteration 1 metrics },
    ...
  ]
}
```

## Experiment Workflow

1. **Baseline run**: Use default parameters, observe behavior
2. **Parameter sweep**: Vary one parameter at a time, track results
3. **Compare runs**: Look at differences in final metrics
4. **Identify mechanism**: Understand which parameters drive behavior
5. **Optimize**: Find parameters that match your research questions

## Quick Variants to Try

**Variant A: "Gatekeeper Effect"**
- Low TOKEN_THRESHOLD, high TOKENS_PER_ITERATION
- Hub actively promotes connections
- Result: Rapid network growth, low final Gini

**Variant B: "Slow Trust Building"**
- High TOKEN_THRESHOLD, low TOKENS_PER_ITERATION
- Connections rare and hard-won
- Result: Slow growth, high final Gini (hub remains powerful)

**Variant C: "Natural Growth"**
- TOKEN_THRESHOLD = 5-8 (moderate)
- TOKENS_PER_ITERATION = 8-12 (moderate)
- Result: Realistic S-curve growth

## Research Ideas

1. **Phase transitions**: At what threshold does network "flip" from sparse to dense?
2. **Resilience**: Remove hub, measure network survival
3. **Inequality**: Track wealth concentration, not just connectivity
4. **Assortativity**: Do rich nodes connect with rich nodes?
5. **Clustering dynamics**: When do triangles form vs isolated connections?

---

**TL;DR**: Simulation shows how central hub enables peer connection formation through repeated encounters. Parameters control speed and nature of network evolution.
