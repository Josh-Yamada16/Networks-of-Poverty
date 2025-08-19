from setup import Setup
import sandbox.JoshTokenExchange.parameters as P
import numpy as np
import pytest
import networkx as nx
from utils import Utils as utils

dir_list = {
    "A": ["B", "C"],
    "B": ["A", "D", "E"],
    "C": ["A", "F"],
    "D": ["B"],
    "E": ["B", "G", "H"],
    "F": ["C"],
    "G": ["E", "I"],
    "H": ["E", "J"],
    "I": ["G"],
    "J": ["H"]
}

direct_list = {
    'AA': ['AG', 'AH', 'AJ', 'AD', 'AI'], 
    'AB': ['AC', 'AE'], 
    'AC': ['AA', 'AE'], 
    'AD': ['AA', 'AH'], 
    'AE': ['AB', 'AG', 'AH'], 
    'AF': [], 
    'AG': ['AG', 'AA', 'AB', 'AC'], 
    'AH': ['AA', 'AJ'], 
    'AI': ['AE'], 
    'AJ': ['AB']
}

undir_list = {
    "A": ["B", "C"],
    "B": ["A", "D", "E"],
    "C": ["A", "F"],
    "D": ["B"],
    "E": ["B", "G", "H"],
    "F": ["C"],
    "G": ["E", "I"],
    "H": ["E", "J"],
    "I": ["G"],
    "J": ["H"]
}

node_names = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]

@pytest.fixture
def edge_mat_directed():
    edge_matrix_directed = Setup.generate_edge_matrix(node_neighbors=dir_list, node_names=node_names)
    return edge_matrix_directed

@pytest.fixture
def edge_mat_undirected():
    edge_matrix_undirected = Setup.generate_edge_matrix(node_neighbors=undir_list, node_names=node_names)
    return edge_matrix_undirected

@pytest.fixture
def directed_graph():
    G = utils.adj_list_to_graph(direct_list, directed_graph=True, money_amount={})
    G.graph["type"] = "directed"
    return G
    
    
def test_shape_of_edge_matrix(edge_mat_directed):
    # Check the shape of the matrix
    assert edge_mat_directed.shape == (len(dir_list), len(dir_list)), "Edge matrix shape is incorrect"

# def test_diagonal_is_close_to_keep_values(edge_mat_directed):
#     # Check that diagonal elements are close to the mean of KEEP_LOW and KEEP_HIGH
#     for i in range(len(node_names)):
#         assert P.KEEP_LOW <= edge_mat_directed[i, i] <= P.KEEP_HIGH, \
#             f"Diagonal element {i} = {edge_mat_directed[i, i]} is not within the range [{P.KEEP_LOW}, {P.KEEP_HIGH}]"

def test_edge_values_are_non_negative(edge_mat_directed):
    # Check that off-diagonal elements are non-negative
    for i in range(len(node_names)):
        for j in range(len(node_names)):
            if i != j:
                assert edge_mat_directed[i, j] >= 0, f"Off-diagonal element ({i}, {j}) is negative"

def test_matrix_rows_sum_to_one_directed(edge_mat_directed):
    # Check that the sum of each row is close to 1
    for i in range(len(node_names)):
        row_sum = np.sum(edge_mat_directed[i, :])
        assert np.isclose(row_sum, 1.0), f"Row {i} does not sum to 1, sum is {row_sum}"
        
def test_matrix_rows_sum_to_one_undirected(edge_mat_undirected):
    # Check that the sum of each row is close to 1
    for i in range(len(node_names)):
        row_sum = np.sum(edge_mat_undirected[i, :])
        assert np.isclose(row_sum, 1.0), f"Row {i} does not sum to 1, sum is {row_sum}"

def test_non_zero_edges_for_neighbors(edge_mat_directed):
    # Check that there are only non-zero values where there are neighbors
    for i, node in enumerate(node_names):
        neighbors = dir_list[node]
        for neigh in neighbors:
            assert edge_mat_directed[node_names.index(node), node_names.index(neigh)] > 0, f"Edge weight from {node} to {node_names[i]} should be positive"

def test_edge_matrix_is_row_stochastic():
    g, edge_mat = Setup.gen_graph(t="sto", n_nodes=10, seed=42)
    row_sums = edge_mat.sum(axis=1)
    assert np.allclose(row_sums, np.ones_like(row_sums)), "Each row of the edge matrix should sum to 1."

def test_gen_multidirected_graph():
    n_nodes = 10
    G, edge_mat = Setup.gen_graph(t="dir", n_nodes=n_nodes, seed=123)
    # Check graph type
    assert isinstance(G, nx.MultiDiGraph), "Generated graph is not a MultiDiGraph"
    # Check node count
    assert len(G.nodes) == n_nodes, f"Expected {n_nodes} nodes, got {len(G.nodes)}"
    # Check that multiple directed edges exist
    edge_counts = {}
    for u, v in G.edges():
        edge_counts[(u, v)] = edge_counts.get((u, v), 0) + 1
    has_duplicates = any(count > 1 for count in edge_counts.values())
    assert has_duplicates, "No multiple directed edges found in MultiDiGraph"
    # Check edge matrix shape matches node count
    assert edge_mat.shape == (n_nodes, n_nodes), "Edge matrix shape does not match node count"

def test_make_strongly_connected_connects_sccs_example(directed_graph):
    # Confirm it's initially not strongly connected
    assert not nx.is_strongly_connected(directed_graph), "Graph should NOT be strongly connected initially"
    initial_scc_count = nx.number_strongly_connected_components(directed_graph)

    # Repair it
    G_fixed, added_edges = Setup.make_strongly_connected(directed_graph)

    # Assertions
    assert nx.is_strongly_connected(G_fixed), "Graph should be strongly connected after repair"
    assert isinstance(added_edges, list) and len(added_edges) > 0, "No edges were added to connect components"

    # Check SCCs reduced to 1
    final_scc_count = nx.number_strongly_connected_components(G_fixed)
    assert final_scc_count == 1, "Graph should have only one strongly connected component after repair"

    # Ensure no self-loops were added
    assert all(u != v for u, v in added_edges), "Self-loops should not be added during repair"
