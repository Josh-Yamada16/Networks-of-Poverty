import json
from pathlib import Path
from pprint import pp

import networkx as nx
import matplotlib
import matplotlib.pyplot as plt
from utils import Utils

# Debug info to diagnose why plot windows may not appear
print("[debug] Matplotlib backend:", matplotlib.get_backend())
try:
	import tkinter
	print("[debug] tkinter available:", tkinter)
except Exception as e:
	print("[debug] tkinter import failed:", type(e).__name__, e)


GRAPH_PATH = Path(__file__).resolve().parent / "twitch_social_networks" / "ENGB" / "ENGB_graph.json"
FEATURES_PATH = Path(__file__).resolve().parent / "twitch_social_networks" / "ENGB" / "ENGB_features.json"
EDGES_PATH = Path(__file__).resolve().parent / "twitch_social_networks" / "ENGB" / "ENGB_edges.csv"


def load_engb_features():
	with FEATURES_PATH.open("r", encoding="utf-8") as file:
		return json.load(file)

def setup_graph():
	if GRAPH_PATH.exists():
		with GRAPH_PATH.open('r', encoding='utf-8') as file:
			adj_list = json.load(file)
		G = Utils.adj_list_to_graph(adj_list)
	elif EDGES_PATH.exists():
		import csv
		G = nx.Graph()
		with EDGES_PATH.open('r', encoding='utf-8') as f:
			reader = csv.reader(f)
			header = next(reader, None)
			for row in reader:
				if not row:
					continue
				src, dst = row[0].strip(), row[1].strip()
				G.add_edge(src, dst)
	else:
		raise FileNotFoundError(f"No graph file found at {GRAPH_PATH} or {EDGES_PATH}")

	# Print basic stats
	print(f"[debug] Graph nodes: {len(G.nodes())}, edges: {len(G.edges())}")

	# Draw the graph before showing
	plt.figure(figsize=(10, 8))
	pos = nx.spring_layout(G, seed=42)
	nx.draw(G, pos=pos, node_size=50, with_labels=False, edge_color='gray')
	plt.title("ENGB Twitch Network")
	plt.tight_layout()

	plt.show()
	return G

setup_graph()