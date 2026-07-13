import json
from pathlib import Path

import networkx as nx
import matplotlib.pyplot as plt


FEATURES_PATH = Path(__file__).resolve().parent / "twitch_social_networks" / "ENGB" / "ENGB_features.json"


def load_engb_features():
	with FEATURES_PATH.open("r", encoding="utf-8") as file:
		return json.load(file)

def setup_graph():
