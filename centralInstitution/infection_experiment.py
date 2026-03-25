import matplotlib.pyplot as plt
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import parameters as params
from infection import Infection
from basicsimSetup import BasicSimSetup
import importlib


# Variables to experiment with
infection_thresholds = [0.2, 0.3, 0.4, 0.5]
percentage_of_infected_nodes = [0.05, 0.10, 0.15, 0.20]
initial_infection_types = [0, 1, 2]
central_institution_connection_percentages = [0.30, 0.40, 0.55, 0.60]

NUM_ITERATIONS = params.NUM_ITERATIONS
results = {}

if not os.path.exists("experiment_graphs"):
    os.makedirs("experiment_graphs")

for ci_conn_perc in central_institution_connection_percentages:
    for threshold in infection_thresholds:
        for perc_infected in percentage_of_infected_nodes:
            for inf_type in initial_infection_types:
                key = f"CI={ci_conn_perc},T={threshold},P={perc_infected},Type={inf_type}"
                print(f"\n--- Running experiment: {key} ---")
                # Set parameters
                params.INFECTION_THRESHOLD = threshold
                params.PERCENTAGE_OF_INFECTED_NODES = perc_infected
                params.INITIAL_INFECTION_TYPE = inf_type
                params.CENTRAL_INSTITUTION_CONNECTION_PERCENTAGE = ci_conn_perc
                importlib.reload(params)
                print(f"Setting CI_CONN_PERC={ci_conn_perc}, INFECTION_THRESHOLD={threshold}, PERCENTAGE_OF_INFECTED_NODES={perc_infected}, INITIAL_INFECTION_TYPE={inf_type}")
                # Setup simulation WITHOUT central institution
                sim = BasicSimSetup()
                sim.setup_basic_simulation(n_nodes=params.NUM_NODES, central_institution_toggle=False)
                G = sim.G
                infection_model = Infection()
                infected_counts = [infection_model.count_infected(G)]
                print(f"Initial infected nodes: {infected_counts[0]}")
                ci_added_at = NUM_ITERATIONS // 2
                for i in range(NUM_ITERATIONS):
                    # Add central institution at halfway point
                    if i == ci_added_at:
                        print(f"Adding central institution at iteration {i+1}")
                        from centralInstitutionNode import CentralInstitutionNode as CI
                        G = CI.add_central_institution(G, list(G.nodes()), ci_conn_perc)
                    # Patch: avoid infinite neighbor growth by using a set
                    for node in G.nodes():
                        if G.nodes[node].get('is_central_institution', False):
                            continue
                        neighbors = set(G.neighbors(node))
                        infected_neighbors = sum(1 for n in neighbors if G.nodes[n].get('infected', False))
                        # If node is connected to central institution, add its neighbors
                        if any(G.nodes[n].get('is_central_institution', False) for n in neighbors):
                            central_neighbors = [n for n in G.neighbors("CENTRAL_INSTITUTION") if G.nodes[n].get('is_central_institution', False)]
                            for central_node in central_neighbors:
                                neighbors.update(G.neighbors(central_node))
                                infected_neighbors += sum(1 for n in G.neighbors(central_node) if G.nodes[n].get('infected', False))
                        infection_fraction = infected_neighbors / len(neighbors) if neighbors else 0
                        if infection_fraction >= threshold:
                            G.nodes[node]['infected'] = True
                    infected_now = infection_model.count_infected(G)
                    infected_counts.append(infected_now)
                    if (i+1) % 1 == 0 or i == NUM_ITERATIONS-1 or i == ci_added_at:
                        print(f"Iteration {i+1}: {infected_now} infected nodes")
                results[key] = (infected_counts, ci_added_at)

                # --- Analysis Section ---
                import pandas as pd

                # Prepare summary table
                summary = []
                for key, (infected_counts, ci_added_at) in results.items():
                    final_infected = infected_counts[-1]
                    before_ci = infected_counts[ci_added_at]
                    after_ci = infected_counts[-1] - infected_counts[ci_added_at]
                    max_growth = max([infected_counts[i+1] - infected_counts[i] for i in range(len(infected_counts)-1)])
                    summary.append({
                        'params': key,
                        'final_infected': final_infected,
                        'infected_before_ci': before_ci,
                        'infected_after_ci': after_ci,
                        'max_growth_per_iter': max_growth
                    })

                df = pd.DataFrame(summary)
                df_sorted = df.sort_values(by=['final_infected', 'max_growth_per_iter'], ascending=False)
                print("\nSummary Table (Top 10):")
                print(df_sorted.head(10))

                # Plot: Top 5 fastest infection growth
                top5 = df_sorted.head(5)
                plt.figure(figsize=(12, 7))
                for idx, row in top5.iterrows():
                    key = row['params']
                    infected_counts, ci_added_at = results[key]
                    plt.plot(range(NUM_ITERATIONS + 1), infected_counts, label=key)
                    plt.axvline(ci_added_at+1, color='red', linestyle='--')
                plt.xlabel('Iteration')
                plt.ylabel('Number of Infected Nodes')
                plt.title('Top 5 Fastest Infection Growth Patterns')
                plt.legend(fontsize=8)
                plt.tight_layout()
                plt.savefig("experiment_graphs/top5_infection_growth.png")
                plt.close()

                # Ranking most influential parameters

                # Only average numeric columns for influence analysis
                numeric_cols = ['final_infected', 'infected_before_ci', 'infected_after_ci', 'max_growth_per_iter']
                ci_groups = df_sorted.groupby(df_sorted['params'].str.extract(r'CI=(.*?),T=(.*?),P=(.*?),Type=(.*)')[0])[numeric_cols].mean()
                print("\nAverage final infected by CI connection percentage:")
                print(ci_groups['final_infected'].sort_values(ascending=False))

                thresh_groups = df_sorted.groupby(df_sorted['params'].str.extract(r'CI=(.*?),T=(.*?),P=(.*?),Type=(.*)')[1])[numeric_cols].mean()
                print("\nAverage final infected by infection threshold:")
                print(thresh_groups['final_infected'].sort_values(ascending=False))

                init_groups = df_sorted.groupby(df_sorted['params'].str.extract(r'CI=(.*?),T=(.*?),P=(.*?),Type=(.*)')[3])[numeric_cols].mean()
                print("\nAverage final infected by initial infection type:")
                print(init_groups['final_infected'].sort_values(ascending=False))

                perc_groups = df_sorted.groupby(df_sorted['params'].str.extract(r'CI=(.*?),T=(.*?),P=(.*?),Type=(.*)')[2])[numeric_cols].mean()
                print("\nAverage final infected by percentage of initially infected nodes:")
                print(perc_groups['final_infected'].sort_values(ascending=False))

                # Plot all results together
                plt.figure(figsize=(14, 8))
                for key, (counts, ci_added_at) in results.items():
                    plt.plot(range(NUM_ITERATIONS + 1), counts, label=key)
                    plt.axvline(ci_added_at+1, color='red', linestyle='--')
                plt.xlabel('Iteration')
                plt.ylabel('Number of Infected Nodes')
                plt.title('Infection Spread Over Iterations (Stochastic Block Model)')
                plt.legend(fontsize=8)
                plt.tight_layout()
                plt.savefig("experiment_graphs/all_infection_patterns.png")
                plt.close()


# --- Analysis Section ---
import pandas as pd

analysis_rows = []
for key, (infected_counts, ci_added_at) in results.items():
    final_infected = infected_counts[-1]
    before_ci = infected_counts[ci_added_at]
    after_ci = infected_counts[-1] - infected_counts[ci_added_at]
    max_growth = max([infected_counts[i+1] - infected_counts[i] for i in range(len(infected_counts)-1)])
    analysis_rows.append({
        'params': key,
        'final_infected': final_infected,
        'infected_before_ci': before_ci,
        'infected_after_ci': after_ci,
        'max_growth': max_growth
    })

df = pd.DataFrame(analysis_rows)
df[['CI','T','P','Type']] = df['params'].str.extract(r'CI=(.*),T=(.*),P=(.*),Type=(.*)')
df = df.sort_values(by=['final_infected','max_growth'], ascending=False)
print("\n--- Summary Table ---")
print(df[['params','final_infected','infected_before_ci','infected_after_ci','max_growth']])

# --- Ranked List ---
print("\n--- Ranked by Final Infected ---")
for i, row in df.iterrows():
    print(f"{row['params']}: Final={row['final_infected']}, MaxGrowth={row['max_growth']}")

# --- Influence Visualization ---
import seaborn as sns
plt.figure(figsize=(12,8))
sns.barplot(data=df, x='CI', y='final_infected', hue='T')
plt.title('Final Infected by CI Connection Percentage and Infection Threshold')
plt.ylabel('Final Number of Infected Nodes')
plt.xlabel('Central Institution Connection Percentage')
plt.tight_layout()
plt.savefig("experiment_graphs/parameter_influence_barplot.png")
plt.close()
