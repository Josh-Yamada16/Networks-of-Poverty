from __future__ import annotations

from dataclasses import dataclass
from statistics import mean, pstdev

import networkx as nx


def _largest_connected_subgraph(graph: nx.Graph) -> nx.Graph:
	"""Return the largest connected component as an undirected simple graph."""
	if graph.number_of_nodes() == 0:
		return graph.copy()
	if graph.is_directed():
		graph = graph.to_undirected()
	if nx.is_connected(graph):
		return graph.copy()
	largest_nodes = max(nx.connected_components(graph), key=len)
	return graph.subgraph(largest_nodes).copy()


def _safe_average_shortest_path_length(graph: nx.Graph) -> float | None:
	if graph.number_of_nodes() < 2:
		return None
	try:
		return float(nx.average_shortest_path_length(graph))
	except nx.NetworkXError:
		return None


def _safe_diameter(graph: nx.Graph) -> int | None:
	if graph.number_of_nodes() < 2:
		return None
	try:
		return int(nx.diameter(graph))
	except nx.NetworkXError:
		return None


def degree_metrics(graph: nx.Graph) -> dict:
	degrees = [degree for _, degree in graph.degree()]
	if not degrees:
		return {
			"node_count": 0,
			"edge_count": 0,
			"density": 0.0,
			"average_degree": 0.0,
			"degree_std": 0.0,
			"min_degree": 0,
			"max_degree": 0,
			"degree_sequence": [],
		}

	return {
		"node_count": graph.number_of_nodes(),
		"edge_count": graph.number_of_edges(),
		"density": float(nx.density(graph)),
		"average_degree": float(mean(degrees)),
		"degree_std": float(pstdev(degrees)) if len(degrees) > 1 else 0.0,
		"min_degree": int(min(degrees)),
		"max_degree": int(max(degrees)),
		"degree_sequence": sorted((int(degree) for degree in degrees), reverse=True),
	}


def clustering_metrics(graph: nx.Graph) -> dict:
	undirected = graph.to_undirected() if graph.is_directed() else graph
	local_clustering = nx.clustering(undirected)
	values = list(local_clustering.values())
	return {
		"average_clustering": float(nx.average_clustering(undirected)) if undirected.number_of_nodes() else 0.0,
		"transitivity": float(nx.transitivity(undirected)) if undirected.number_of_nodes() else 0.0,
		"local_clustering_mean": float(mean(values)) if values else 0.0,
		"top_clustering_nodes": sorted(local_clustering.items(), key=lambda item: item[1], reverse=True)[:10],
	}


def path_metrics(graph: nx.Graph) -> dict:
	undirected = graph.to_undirected() if graph.is_directed() else graph
	largest_component = _largest_connected_subgraph(undirected)
	component_fraction = (
		largest_component.number_of_nodes() / undirected.number_of_nodes()
		if undirected.number_of_nodes()
		else 0.0
	)
	return {
		"is_connected": bool(nx.is_connected(undirected)) if undirected.number_of_nodes() else False,
		"largest_component_fraction": float(component_fraction),
		"average_shortest_path_length": _safe_average_shortest_path_length(largest_component),
		"diameter": _safe_diameter(largest_component),
		"radius": int(nx.radius(largest_component)) if largest_component.number_of_nodes() > 1 else None,
	}


def assortativity_metrics(graph: nx.Graph) -> dict:
	undirected = graph.to_undirected() if graph.is_directed() else graph
	try:
		assortativity = float(nx.degree_assortativity_coefficient(undirected))
	except (nx.NetworkXError, ZeroDivisionError, ValueError):
		assortativity = None
	return {"degree_assortativity": assortativity}


def centrality_metrics(graph: nx.Graph, top_k: int = 10) -> dict:
	undirected = graph.to_undirected() if graph.is_directed() else graph
	if undirected.number_of_nodes() == 0:
		return {
			"degree_centrality_top": [],
			"betweenness_centrality_top": [],
			"closeness_centrality_top": [],
			"eigenvector_centrality_top": [],
		}

	degree_centrality = nx.degree_centrality(undirected)
	betweenness_centrality = nx.betweenness_centrality(undirected, normalized=True)
	closeness_centrality = nx.closeness_centrality(undirected)
	try:
		eigenvector_centrality = nx.eigenvector_centrality(undirected, max_iter=1000)
	except nx.PowerIterationFailedConvergence:
		eigenvector_centrality = {node: 0.0 for node in undirected.nodes()}

	def _top_items(values: dict) -> list[tuple[str, float]]:
		return sorted(values.items(), key=lambda item: item[1], reverse=True)[:top_k]

	return {
		"degree_centrality_top": _top_items(degree_centrality),
		"betweenness_centrality_top": _top_items(betweenness_centrality),
		"closeness_centrality_top": _top_items(closeness_centrality),
		"eigenvector_centrality_top": _top_items(eigenvector_centrality),
	}


def community_metrics(graph: nx.Graph) -> dict:
	undirected = graph.to_undirected() if graph.is_directed() else graph
	if undirected.number_of_nodes() == 0:
		return {"community_count": 0, "modularity": None, "community_sizes": []}

	communities = list(nx.algorithms.community.greedy_modularity_communities(undirected))
	modularity = None
	try:
		modularity = float(nx.algorithms.community.modularity(undirected, communities))
	except (nx.NetworkXError, ZeroDivisionError, ValueError):
		modularity = None

	community_sizes = sorted((len(community) for community in communities), reverse=True)
	return {
		"community_count": len(communities),
		"modularity": modularity,
		"community_sizes": community_sizes,
	}


def canonical_model_comparison(graph: nx.Graph, seed: int = 42) -> dict:
	"""Compare the observed graph with common reference graph families.

	The returned distances are heuristic: smaller values mean the observed graph
	looks more like that model on the selected summary statistics.
	"""
	undirected = graph.to_undirected() if graph.is_directed() else graph
	n = undirected.number_of_nodes()
	m = undirected.number_of_edges()
	if n < 3:
		return {"models": {}, "best_match": None}

	observed = {
		"density": float(nx.density(undirected)),
		"average_clustering": float(nx.average_clustering(undirected)),
		"assortativity": assortativity_metrics(undirected)["degree_assortativity"],
		"average_path_length": _safe_average_shortest_path_length(_largest_connected_subgraph(undirected)),
	}

	# Keep the synthetic graphs close to the observed graph size.
	er_p = observed["density"]
	er_graph = nx.gnp_random_graph(n, er_p, seed=seed)

	ws_k = max(2, round(2 * m / n))
	if ws_k >= n:
		ws_k = n - 1 if (n - 1) % 2 == 0 else n - 2
	ws_k = max(2, ws_k)
	if ws_k % 2 == 1:
		ws_k -= 1
	ws_k = max(2, ws_k)
	ws_graph = nx.watts_strogatz_graph(n, ws_k, 0.1, seed=seed)

	ba_m = max(1, min(n - 1, round(m / n)))
	ba_graph = nx.barabasi_albert_graph(n, ba_m, seed=seed)

	models = {
		"erdos_renyi": er_graph,
		"watts_strogatz": ws_graph,
		"barabasi_albert": ba_graph,
	}

	def _distance(candidate: nx.Graph) -> float:
		candidate_metrics = {
			"density": float(nx.density(candidate)),
			"average_clustering": float(nx.average_clustering(candidate)),
			"assortativity": assortativity_metrics(candidate)["degree_assortativity"],
			"average_path_length": _safe_average_shortest_path_length(_largest_connected_subgraph(candidate)),
		}
		distance = 0.0
		for key, observed_value in observed.items():
			candidate_value = candidate_metrics[key]
			if observed_value is None or candidate_value is None:
				continue
			distance += abs(observed_value - candidate_value)
		return float(distance)

	model_distances = {name: _distance(candidate) for name, candidate in models.items()}
	best_match = min(model_distances, key=model_distances.get) if model_distances else None
	return {
		"observed": observed,
		"models": model_distances,
		"best_match": best_match,
	}


def summarize_graph(graph: nx.Graph) -> dict:
	"""Return a single dictionary with the main graph measures."""
	summary = {}
	summary.update(degree_metrics(graph))
	summary.update(clustering_metrics(graph))
	summary.update(path_metrics(graph))
	summary.update(assortativity_metrics(graph))
	summary.update(centrality_metrics(graph))
	summary.update(community_metrics(graph))
	summary["canonical_model_comparison"] = canonical_model_comparison(graph)
	return summary


@dataclass(frozen=True)
class GraphMeasureReport:
	"""Typed wrapper around the summary dictionary for convenience."""

	degree: dict
	clustering: dict
	paths: dict
	assortativity: dict
	centrality: dict
	communities: dict
	model_comparison: dict

	@classmethod
	def from_graph(cls, graph: nx.Graph) -> "GraphMeasureReport":
		return cls(
			degree=degree_metrics(graph),
			clustering=clustering_metrics(graph),
			paths=path_metrics(graph),
			assortativity=assortativity_metrics(graph),
			centrality=centrality_metrics(graph),
			communities=community_metrics(graph),
			model_comparison=canonical_model_comparison(graph),
		)