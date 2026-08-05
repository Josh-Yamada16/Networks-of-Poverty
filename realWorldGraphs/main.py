import json
from pathlib import Path

import networkx as nx
import matplotlib.pyplot as plt
from utils import Utils
from network_measures import summarize_graph


GRAPH_PATH = Path(__file__).resolve().parent / "twitch_social_networks" / "ENGB" / "ENGB_graph.json"
FEATURES_PATH = Path(__file__).resolve().parent / "twitch_social_networks" / "ENGB" / "ENGB_features.json"


def load_engb_features():
	with FEATURES_PATH.open("r", encoding="utf-8") as file:
		return json.load(file)

def setup_graph():
	with GRAPH_PATH.open('r', encoding='utf-8') as file:
		adj_list = json.load(file)

	G = Utils.adj_list_to_graph(adj_list)

	plt.show()
	return G


def analyze_graph():
	graph = setup_graph()
	report = summarize_graph(graph)
	print("Best matching reference model:", report["canonical_model_comparison"]["best_match"])
	return report


if __name__ == "__main__":
	analyze_graph()