import random
import numpy as np
import networkx as nx
import parameters as P
import math
import string


class Utils:
    @staticmethod
    def calc_eigenvector(edge_mat: np.ndarray) -> np.ndarray:
        eigenvalues, eigenvectors = np.linalg.eig(edge_mat)
        # idx = np.argmin(np.abs(eigenvalues - 1))
        idx = np.argmax(np.abs(eigenvalues))  # Find the index of the largest eigenvalue
        # Get the corresponding eigenvector
        closest_to_one_vector = eigenvectors[:, idx].real
        # print(eigenvalues)

        return closest_to_one_vector

    @staticmethod
    def compare_to_eigenvector(end_monies: np.ndarray, edge_mat: np.ndarray) -> float:
        v2 = Utils.calc_eigenvector(edge_mat)
        dot_product = np.dot(v2, end_monies)
        result = dot_product / np.dot(end_monies, end_monies)
        # print(f"Matrix scaling factor: {result:.4f}")
        return result

    @staticmethod
    def compare_vectors(vec: np.ndarray, edge_mat: np.ndarray) -> float:
        """Compare a money vector to the principal eigenvector of edge_mat using cosine similarity.
        Returns a value in [0, 1]."""
        v = Utils.calc_eigenvector(edge_mat)
        a = np.asarray(vec, dtype=float)
        b = np.asarray(v, dtype=float)
        denom = (np.linalg.norm(a) * np.linalg.norm(b))
        if denom == 0:
            return 0.0
        cos = np.dot(a, b) / denom
        return float(abs(cos))

    @staticmethod
    def check_if_eigenvector(end_monies: np.ndarray, edge_mat: np.ndarray) -> bool:
        Av = edge_mat.T @ end_monies.T
        lambda_estimate = np.dot(end_monies, Av) / np.dot(end_monies, end_monies)
        # print(f"Lambda Estimate: {lambda_estimate:.4f}")
        is_eigenvector = np.allclose(Av, lambda_estimate * end_monies, atol=1e-2, rtol=1e-2)
        # print(Av)
        # print("Is eigenvector?", is_eigenvector)

    @staticmethod
    def calc_percent_change(g: nx.Graph, previous_money: dict):
        percent_changes = {}
        for n in g.nodes:
            old = previous_money[n]
            new = g.nodes[n]['money']
            if old == 0:
                percent_changes[n] = float('inf')  # or use None or 0 if more appropriate
            else:
                percent_changes[n] = ((new - old) / old) * 100
        return percent_changes

    @staticmethod
    def calc_and_print_percent_change(g: nx.Graph, previous_money: dict, it):
        if P.PRINT_PERCENT_CHANGE:
            if it is not None:
                print(f"Iteration {it + 1} Percent Changes:")
            else:
                print("Final Money Distribution Change:")
            percent_changes = Utils.calc_percent_change(g, previous_money)
            for idx, (node, pct) in enumerate(percent_changes.items(), 1):
                print(f"{node}: {pct:.2f}%", end=" | ")
                if idx % 5 == 0:
                    print()  # newline after every 5 entries
            if idx % 5 != 0:
                print()  # ensure a newline at the end if total nodes not divisible by 5
            print("=========" * 10)
    
    @staticmethod
    def adj_list_to_graph(adj_list: dict, directed_graph: bool = False, money_amount: dict | None = None) -> nx.Graph:
        """Create a graph from an adjacency list.
        Args:
            adj_list: mapping node->list(neighbors)
            directed_graph: if True, produce a MultiDiGraph (allows multiple edges); else undirected Graph.
            money_amount: optional dict mapping node->money to set on nodes.
        """
        if directed_graph:
            G = nx.MultiDiGraph()
        else:
            G = nx.Graph()
        G.add_nodes_from(list(adj_list.keys()))
        for k, v in adj_list.items():
            for node in v:
                G.add_edge(k, node)
        # assign money if provided
        if money_amount:
            for n, amt in money_amount.items():
                if n in G.nodes:
                    G.nodes[n]["money"] = amt
        return G

    @staticmethod
    def adj_mat_to_graph(graph: nx.Graph, adj_mat: np.array) -> nx.Graph:
        labels = list(graph.nodes)
        for row in range(len(adj_mat)):
            for col in range(len(adj_mat[0])):
            # print(adj_mat[row, col])
                if (row == col) or (adj_mat[row, col] == math.inf):
                    continue
            graph.add_edge(labels[row], labels[col], weight=adj_mat[row, col])
        return graph
    
    @staticmethod
    def graph_to_adjacency_list(G: nx.Graph) -> dict:
        adj_list = {}
        for node in G.nodes():
            adj_list[node] = list(G.successors(node) if G.is_directed() else G.neighbors(node))
        return adj_list
    
    @staticmethod
    def generate_symmetric_prob_matrix(n_blocks):
        mat = np.zeros((n_blocks, n_blocks))
        for i in range(n_blocks):
            for j in range(i, n_blocks):
                if i == j:
                    val = round(random.uniform(P.INTRA_BLOCK_PROB_LOW, P.INTRA_BLOCK_PROB_HIGH), 2)
                    mat[i][i] = val
                else:
                    val = round(random.uniform(P.EXTRA_BLOCK_PROB_LOW, P.EXTRA_BLOCK_PROB_HIGH), 2)
                    mat[i][j] = val
                    mat[j][i] = val
        return mat

    @staticmethod
    def sbm_assortativity_metrics(prob_matrix: np.ndarray, block_proportions: np.ndarray | None = None) -> dict:
        """Compute assortativity-style diagnostics for an undirected SBM.

        Args:
            prob_matrix: KxK SBM probability matrix B.
            block_proportions: Length-K vector pi. If None, assumes uniform block sizes.

        Returns:
            Dictionary with expected within-block edge share and normalized assortativity.
        """
        B = np.asarray(prob_matrix, dtype=float)
        if B.ndim != 2 or B.shape[0] != B.shape[1]:
            raise ValueError("prob_matrix must be a square matrix")

        k = B.shape[0]
        if block_proportions is None:
            pi = np.full(k, 1.0 / k)
        else:
            pi = np.asarray(block_proportions, dtype=float)
            if pi.ndim != 1 or pi.shape[0] != k:
                raise ValueError("block_proportions must be a length-K vector")
            if np.any(pi < 0):
                raise ValueError("block_proportions cannot contain negative values")
            total = float(np.sum(pi))
            if total <= 0:
                raise ValueError("block_proportions must have a positive sum")
            pi = pi / total

        within_mass = 0.5 * float(np.sum((pi ** 2) * np.diag(B)))
        between_mass = 0.0
        for i in range(k):
            for j in range(i + 1, k):
                between_mass += float(pi[i] * pi[j] * B[i, j])

        total_mass = within_mass + between_mass
        expected_within_fraction = (within_mass / total_mass) if total_mass > 0 else 0.0

        chance_within = float(np.sum(pi ** 2))
        denom = 1.0 - chance_within
        normalized_assortativity = (
            (expected_within_fraction - chance_within) / denom if denom > 0 else 0.0
        )

        within_weight = float(np.sum(pi ** 2))
        between_weight = float(np.sum(np.triu(np.outer(pi, pi), k=1)))
        within_prob_mean = (
            float(np.sum((pi ** 2) * np.diag(B))) / within_weight if within_weight > 0 else 0.0
        )
        between_prob_mean = (
            float(np.sum(np.triu(np.outer(pi, pi) * B, k=1))) / between_weight if between_weight > 0 else 0.0
        )

        return {
            "expected_within_fraction": expected_within_fraction,
            "chance_within_fraction": chance_within,
            "normalized_assortativity": normalized_assortativity,
            "within_prob_mean": within_prob_mean,
            "between_prob_mean": between_prob_mean,
            "is_assortative": within_prob_mean > between_prob_mean,
        }
    
    @staticmethod
    def generate_letter_codes(n):
        letters = string.ascii_uppercase
        codes = []
        for first in letters:
            for second in letters:
                for third in letters:
                    if len(codes) < n:
                        codes.append(first + second + third)
                    else:
                        return codes
        if len(codes) < n:
            raise ValueError("Exceeded 26 × 26 × 26 = 17,576 possible three-letter codes")
        return codes
    
    @staticmethod
    def average_degree(G: nx.Graph) -> float:
        avg_degree = sum(dict(G.degree()).values()) / G.number_of_nodes()
        return avg_degree
    
    @staticmethod
    def divide_integer(total, n_parts) -> np.ndarray:
        if n_parts <= 0:
            return np.array([])
        cuts = sorted(random.sample(range(1, int(total)), n_parts - 1))
        return np.array([a - b for a, b in zip(cuts + [int(total)], [0] + cuts)])