import numpy as np
import networkx as nx
import pytest
from utils import Utils
import parameters as P

@pytest.fixture
def sample_edge_matrix():
    return np.array([
        [0.0, 0.5, 0.5],
        [0.5, 0.0, 0.5],
        [0.5, 0.5, 0.0]
    ])

@pytest.fixture
def end_monies():
    return np.array([100, 200, 300])

def test_calc_eigenvector_returns_vector(sample_edge_matrix):
    eig_vec = Utils.calc_eigenvector(sample_edge_matrix)
    assert isinstance(eig_vec, np.ndarray)
    assert eig_vec.shape == (sample_edge_matrix.shape[0],)

def test_compare_vectors_cosine_similarity_output(end_monies, sample_edge_matrix):
    similarity = Utils.compare_vectors(end_monies, sample_edge_matrix)
    assert 0.0 <= similarity <= 1.0

def test_calc_percent_change_basic():
    G = nx.Graph()
    G.add_nodes_from(["A", "B", "C"])
    previous_money = {"A": 100, "B": 200, "C": 300}
    for node in previous_money:
        G.nodes[node]["money"] = previous_money[node] * 1.1  # 10% gain
    result = Utils.calc_percent_change(G, previous_money)
    for val in result.values():
        assert pytest.approx(val, 0.01) == 10.0
def test_calc_percent_change_with_zero_base():
    G = nx.Graph()
    G.add_nodes_from(["X"])
    previous_money = {"X": 0}
    G.nodes["X"]["money"] = 50
    result = Utils.calc_percent_change(G, previous_money)
    assert result["X"] == float("inf")

def test_calc_and_print_percent_change_prints(capsys):
    G = nx.Graph()
    G.add_nodes_from(["A", "B"])
    prev = {"A": 100, "B": 200}
    G.nodes["A"]["money"] = 110
    G.nodes["B"]["money"] = 180

    P.PRINT_PERCENT_CHANGE = True
    Utils.calc_and_print_percent_change(G, prev, it=0)
    captured = capsys.readouterr()
    assert "Iteration 1 Percent Changes" in captured.out
    assert "A: 10.00%" in captured.out
    assert "B: -10.00%" in captured.out
    P.PRINT_PERCENT_CHANGE = False
