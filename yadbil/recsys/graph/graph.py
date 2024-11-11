from typing import Any, Dict, List

import networkx as nx


class GraphProcessor:
    def __init__(
        self,
        posts: List[Dict[str, Any]],
        idf_scores: Dict[str, float],
        words_key: str = "stemmed_words",
    ):
        """Initializes the GraphProcessor with posts and IDF scores.

        Args:
            posts (List[Dict[str, Any]]): The list of posts.
            idf_scores (Dict[str, float]): The IDF scores for words.
            words_key (str): The key to access words in posts. Defaults to 'stemmed_words'.
        """
        self.posts = posts
        self.idf_scores = idf_scores
        self.words_key = words_key
        self.G = self._create_graph()

    def _create_graph(self) -> nx.Graph:
        """Creates an undirected graph based on the posts and IDF scores.

        Returns:
            nx.Graph: The created graph.
        """
        G = nx.Graph()

        # Adding nodes
        for post in self.posts:
            G.add_node(post["id"], words=post[self.words_key])

        # Adding edges based on shared stemmed words
        for i, post1 in enumerate(self.posts):
            for post2 in self.posts[i + 1 :]:
                common_words = set(post1[self.words_key]) & set(post2[self.words_key])
                if common_words:
                    edge_weight = sum(self.idf_scores.get(word, 0) for word in common_words)
                    G.add_edge(post1["id"], post2["id"], weight=edge_weight)

        return G

    def scale_edge_weights(self) -> None:
        """Applies min-max scaling to edge weights in the graph."""
        weights = [data["weight"] for _, _, data in self.G.edges(data=True)]
        min_weight = min(weights)
        max_weight = max(weights)

        for _, _, data in self.G.edges(data=True):
            data["weight"] = (data["weight"] - min_weight) / (max_weight - min_weight)

    def filter_edges_by_threshold(self, threshold: float = 0.5) -> nx.Graph:
        """Filters edges in the graph based on a weight threshold and removes nodes without edges.

        Args:
            threshold (float): The edge weight threshold for filtering. Defaults to 0.5.

        Returns:
            nx.Graph: A new graph containing only edges with weights above the threshold
                      and nodes connected by these edges.
        """
        G_filtered = nx.Graph()
        G_filtered.add_nodes_from(self.G.nodes(data=True))  # Add all nodes to the new graph

        for u, v, data in self.G.edges(data=True):
            if data["weight"] >= threshold:
                G_filtered.add_edge(u, v, weight=data["weight"])

        # Remove nodes with degree 0 (no edges)
        isolated_nodes = list(nx.isolates(G_filtered))
        G_filtered.remove_nodes_from(isolated_nodes)

        return G_filtered
