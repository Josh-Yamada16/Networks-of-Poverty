import networkx as nx
import networkx.algorithms.community as nx_comm
import random
import numpy as np
import parameters as P
from collections import defaultdict
from typing import Tuple
from utility.utils import Utils as utils
from utility.visualizer import Visualization as viz

class Setup:

    @staticmethod
    def _generate_hub_leaf_block_graph(sizes: np.ndarray, probs: np.ndarray) -> nx.Graph:
        """Generate a block-structured graph with hub-leaf wiring inside blocks.

        This pattern tends to keep modularity high (mostly within-block edges)
        while pushing degree assortativity down (high-degree hubs connect to low-degree leaves).
        """
        G = nx.Graph()
        block_nodes = []
        start = 0
        for block_id, size in enumerate(sizes):
            nodes = list(range(start, start + int(size)))
            block_nodes.append(nodes)
            for n in nodes:
                G.add_node(n, block=block_id)
            start += int(size)

        # Intra-block edges: hub-leaf dominant
        for nodes in block_nodes:
            if len(nodes) <= 1:
                continue
            hub_count = max(1, int(round(len(nodes) * P.SBM_HUB_FRACTION)))
            hub_count = min(hub_count, len(nodes) - 1)
            hubs = set(random.sample(nodes, hub_count))
            leaves = [n for n in nodes if n not in hubs]

            # Ensure each leaf gets at least one hub link when possible.
            for leaf in leaves:
                chosen_hub = random.choice(tuple(hubs))
                G.add_edge(leaf, chosen_hub)

            # Additional stochastic edges inside the block.
            for i in range(len(nodes)):
                for j in range(i + 1, len(nodes)):
                    u, v = nodes[i], nodes[j]
                    if G.has_edge(u, v):
                        continue
                    u_is_hub = u in hubs
                    v_is_hub = v in hubs
                    if u_is_hub and v_is_hub:
                        p_intra = P.SBM_HUB_HUB_PROB
                    elif (u_is_hub and not v_is_hub) or (v_is_hub and not u_is_hub):
                        p_intra = P.SBM_HUB_LEAF_PROB
                    else:
                        p_intra = P.SBM_LEAF_LEAF_PROB
                    if random.random() < p_intra:
                        G.add_edge(u, v)

        # Inter-block edges remain sparse to preserve community separation.
        for i in range(len(block_nodes)):
            for j in range(i + 1, len(block_nodes)):
                p_between = float(probs[i, j]) * P.SBM_INTER_BLOCK_PROB_SCALE
                p_between = max(0.0, min(1.0, p_between))
                for u in block_nodes[i]:
                    for v in block_nodes[j]:
                        if random.random() < p_between:
                            G.add_edge(u, v)
        return G

    @staticmethod
    def rename_nodes_with_codes(G: nx.Graph):
        codes = utils.generate_letter_codes(len(G.nodes))
        mapping = dict(zip(G.nodes, codes))
        nx.relabel_nodes(G, mapping, copy=False)

    @staticmethod
    def gen_graph(t: str, n_nodes: int) -> Tuple[nx.Graph, np.ndarray, list]:
        if P.CONTROL_RANDOM_SEED:
            random.seed(P.RANDOM_SEED)
            np.random.seed(P.RANDOM_SEED)
        graph_types = {
            "erd": (lambda: nx.erdos_renyi_graph(n=n_nodes, p=0.3, seed=P.RANDOM_SEED), "erdos_renyi"),
            "wat": (lambda: nx.newman_watts_strogatz_graph(n=n_nodes, k=2, p=0.5, seed=P.RANDOM_SEED), "watts_strogatz"),
            "bara": (lambda: nx.barabasi_albert_graph(n=n_nodes, m=2, seed=P.RANDOM_SEED), "barabasi_albert"),
            "cir": (lambda: nx.circulant_graph(n=n_nodes, offsets=[1, 3]), "circulant"),
            "lat": (lambda: nx.triangular_lattice_graph(m=3, n=3), "triangular_lattice"),
            "barb": (lambda: nx.barbell_graph(m1=10, m2=15), "barbell"),
        }

        if t in graph_types:
            G = graph_types[t][0]()
            G.graph["type"] = graph_types[t][1]
        elif t == "sto":
            blocks = P.STOCHASTIC_BLOCKS
            parts = utils.divide_integer(n_nodes, blocks)
            probs = utils.generate_symmetric_prob_matrix(n_blocks=blocks)
            block_proportions = np.array(parts) / n_nodes
            sbm_assortativity_metrics = utils.sbm_assortativity_metrics(probs, block_proportions=block_proportions)
            print("SBM (matrix) assortativity:", f"{sbm_assortativity_metrics['normalized_assortativity']:.2f}")

            if P.SBM_STRUCTURE_MODE == "hub_leaf":
                G = Setup._generate_hub_leaf_block_graph(sizes=parts, probs=probs)
            else:
                G = nx.stochastic_block_model(sizes=parts, p=probs, seed=P.RANDOM_SEED)

            print("SBM Degree Assortativity:", f"{nx.degree_assortativity_coefficient(G):.2f}")
            planted_communities = [
                set(n for n, d in G.nodes(data=True) if d.get("block") == b)
                for b in range(blocks)
            ]
            Q = nx_comm.modularity(G, planted_communities)
            print("SBM Modularity:", f"{Q:.2f}")
            G.graph["type"] = "stochastic_block"
        elif t == "dir":
            G = nx.MultiDiGraph()
            G.add_nodes_from(range(n_nodes))
            for _ in range(n_nodes + n_nodes // 3):
                u, v = random.choices(list(G.nodes), k=2)
                G.add_edge(u, v)
            G.graph["type"] = "multi_directed"
            Setup.rename_nodes_with_codes(G)
            if P.DRAW_INITIAL_GRAPH:
                viz.draw_graph_initial(g=G, layout=viz.spring_lay(G), title="Initial Directed Graph", node_colors=[1]*n_nodes)
            while not nx.is_strongly_connected(G):
                G, added_edges = Setup.make_strongly_connected(G)
                # print(f"Added edges to make the graph strongly connected: {added_edges}")
        elif t == "default":
            G_undirected = nx.generators.classic.circulant_graph(n_nodes, [1, 2])
            G = nx.DiGraph()
            G.add_nodes_from(G_undirected.nodes())
            G.add_edges_from([(u, v) for u, v in G_undirected.edges()] + [(v, u) for u, v in G_undirected.edges()])
            G.graph["type"] = "default"
        # elif t == "custom":
        #     G = utils.adj_list_to_graph(P.CUSTOM_GRAPH, directed_graph=True)
        #     G.graph["type"] = "custom"
        else:
            G = nx.random_regular_graph(d=3, n=n_nodes, seed=P.RANDOM_SEED)
            G.graph["type"] = "random_regular"

        if t != "dir":
            Setup.rename_nodes_with_codes(G)
        node_list = sorted(G.nodes())
        node_neighbors = Setup.get_node_neighbors(G)
        edge_mat = Setup.generate_edge_matrix(node_neighbors=node_neighbors, node_names=node_list)
        # Assign money before initializing gains_losses and original_money
        Setup.assign_money(G)
        for node in node_list:
            G.nodes[node]['gains_losses'] = []
            G.nodes[node]['original_money'] = G.nodes[node]['money']
        return G, edge_mat, node_list

    @staticmethod
    def assign_money(G: nx.Graph):
        if G.graph["type"] == "stochastic_block":
            block_means = {0: 100, 1: 80, 2: 60, 3: 40, 4: 20}
            for node, data in G.nodes(data=True):
                block = data["block"]
                G.nodes[node]["money"] = int(random.gauss(block_means[block], P.STD_DEV))
        if G.graph["type"] == "custom":
            for node, money in zip(G.nodes(), P.CUSTOM_MONEY):
                G.nodes[node]["money"] = money
        else:
            for node in G.nodes:
                G.nodes[node]["money"] = random.randint(10, 100)

    @staticmethod
    def assign_edge_weights_from_matrix(G: nx.Graph, edge_matrix: np.ndarray, directed: bool = True) -> nx.Graph:
        seen_edges = set()
        node_list = list(G.nodes())
        node_index = {node: i for i, node in enumerate(node_list)}
        for u, v in G.edges():
            if not directed:
                edge_key = sorted((u, v))  # ensures (A, B) and (B, A) are treated the same
            else:
                edge_key = (u, v)
            if edge_key in seen_edges:
                continue  # skip if already handled
            seen_edges.add(edge_key)
            # Your edge weight logic here
            row = node_index[u]
            col = node_index[v]
            G[u][v]["weight"] = edge_matrix[row][col]
        return G
    
    @staticmethod
    def generate_edge_matrix(node_neighbors: dict, node_names: list) -> np.ndarray:
        n_nodes = len(node_names)
        mat = np.zeros((n_nodes, n_nodes))
        # maybe add a keep value to the diagonal for future use
        for i in range(n_nodes):
            neighbors = node_neighbors[node_names[i]]
            if not neighbors:
                continue
            if P.RANDOMIZE_WEIGHTS:
                weights = Setup.divide_integer(total=100, n_parts=len(neighbors))
                weight_index = 0
                for j, neighbor in enumerate(neighbors):
                    col = node_names.index(neighbor)
                    mat[i, col] = weights[weight_index] / 100.0
                    weight_index += 1
            else:
                for neighbor in neighbors:
                    col = node_names.index(neighbor)
                    mat[i, col] = 1.0 / len(neighbors)
        Setup.check_for_loners(mat)
        return mat
    
    @staticmethod
    def get_node_neighbors(G: nx.Graph):
        node_neighbors = defaultdict(set)
        if G.is_directed():
            for edge in G.edges():
                u, v = edge
                node_neighbors[u].add(v)
        else:
            for edge in G.edges():
                u, v = edge
                node_neighbors[u].add(v)
                node_neighbors[v].add(u)
        return node_neighbors
    
    @staticmethod
    def check_for_loners(mat: np.ndarray):
        row_sums = np.sum(mat, axis=1)
        zero_rows = np.where(row_sums == 0)[0]
        for i in zero_rows:
            mat[i, i] = 1.0

    @staticmethod
    def make_strongly_connected(G: nx.DiGraph):
        C = nx.condensation(G)
        mapping = C.graph["mapping"]  # original node → SCC ID
        inverse_mapping = Setup.invert_mapping(mapping)  # SCC ID → nodes

        sources = []
        sinks = []
        isolated = []

        for n in C.nodes:
            in_deg = C.in_degree(n)
            out_deg = C.out_degree(n)
            if in_deg == 0 and out_deg == 0:
                isolated.append(n)
            elif in_deg == 0:
                sources.append(n)
            elif out_deg == 0:
                sinks.append(n)
                
        added_edges = []

        # Step 1: Connect sinks → sources
        for i in range(max(len(sources), len(sinks))):
            src = sources[i % len(sources)]
            dst = sinks[i % len(sinks)]
            u = sorted(inverse_mapping[dst])[0]
            v = sorted(inverse_mapping[src])[0]
            if u != v and not G.has_edge(u, v):
                G.add_edge(u, v)
                added_edges.append((u, v))

        # Step 2: Connect isolated SCCs to a non-isolated one
        for j, src_scc in enumerate(isolated):
            src = random.choice(list(inverse_mapping[src_scc]))
            for i, dst_scc in enumerate(isolated):
                if i == j:
                    continue
                dst = random.choice(list(inverse_mapping[dst_scc]))
                if src != dst and not G.has_edge(src, dst):
                    G.add_edge(src, dst)
                    added_edges.append((src, dst))

        return G, added_edges

    
    @staticmethod
    def invert_mapping(mapping):
        from collections import defaultdict
        inverse = defaultdict(set)
        for node, scc_id in mapping.items():
            inverse[scc_id].add(node)
        return inverse