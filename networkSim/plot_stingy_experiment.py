import matplotlib.pyplot as plt
import numpy as np
import parameters as P
from setup import Setup
from simulation import TokenSimulation

# Experiment settings
max_stingy_values = list(range(0, P.NUM_NODES + 1, 2))  # Every other value from 0 to NUM_NODES
num_trials = 1  # Number of runs per setting for averaging
from collections import defaultdict
results_by_actual_stingy = defaultdict(list)

for max_stingy in max_stingy_values:
    for _ in range(num_trials):
        sim = TokenSimulation(max_stingy_behaviors=max_stingy)
        g, edge_mat, node_list = Setup.gen_graph(t=P.GRAPH_TYPE, n_nodes=P.NUM_NODES, seed=42)
        states, layout, edge_mat = sim.run_simulation(iterations=P.NUM_ITERATIONS)
        last_graph = states[-1][0]
        # Record by actual number of stingy behaviors added
        actual_stingy_added = last_graph.graph.get('stingy_count', 0)
        end_monies = [last_graph.nodes[n]["money"] for n in node_list]
        results_by_actual_stingy[actual_stingy_added].append(end_monies)

# Average results for each actual stingy count
actual_stingy_values = sorted(results_by_actual_stingy.keys())
end_money_results = []
for stingy_count in actual_stingy_values:
    trials = results_by_actual_stingy[stingy_count]
    avg_end_monies = np.mean(trials, axis=0)
    end_money_results.append(avg_end_monies)

# Plotting


# Each group is the actual number of stingy behaviors added, bars within group are node end money values
num_nodes = len(end_money_results[0])
x = np.arange(len(actual_stingy_values))  # group positions for actual stingy behaviors added
bar_width = 0.8 / num_nodes
fig, ax = plt.subplots(figsize=(14, 7))

for node_idx in range(num_nodes):
    node_money = [end_money_results[i][node_idx] for i in range(len(actual_stingy_values))]
    ax.bar(x + node_idx * bar_width, node_money, bar_width, label=f"Node {node_idx}")

ax.set_xticks(x + (num_nodes * bar_width) / 2 - bar_width / 2)
ax.set_xticklabels([f"Added: {val}" for val in actual_stingy_values])
ax.set_xlabel("Actual Stingy Behaviors Added")
ax.set_ylabel("End Money Value")
ax.set_title("Grouped Bar Chart: Node End Money vs. Actual Stingy Behaviors Added")
ax.legend(title="Node Index", bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()
