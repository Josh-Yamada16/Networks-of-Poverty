import random
import numpy as np
import networkx as nx
import parameters as P
import math

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
    def adj_list_to_graph(adj_list: dict) -> nx.Graph:
        G = nx.MultiDiGraph()
        G.add_nodes_from(list(adj_list.keys()))
        for k, v in adj_list.items():
            for node in v:
                G.add_edge(k, node)
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