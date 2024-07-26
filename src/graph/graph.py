import networkx as nx


def scale_edge_weights(G):
    """Applies min-max scaling to edge weights in the graph.

    Args:
        G: The NetworkX graph.

    Returns:
        The graph with scaled edge weights.
    """
    weights = [data["weight"] for _, _, data in G.edges(data=True)]
    min_weight = min(weights)
    max_weight = max(weights)

    for u, v, data in G.edges(data=True):
        data["weight"] = (data["weight"] - min_weight) / (max_weight - min_weight)

    return G


def filter_edges_by_threshold(G, threshold=0.5):
    """Filters edges in the graph based on a weight threshold and
       removes nodes without edges.

    Args:
        G: The NetworkX graph.
        threshold: The edge weight threshold for filtering.

    Returns:
        A new graph containing only edges with weights above the threshold
        and nodes connected by these edges.
    """
    G_filtered = nx.Graph()
    G_filtered.add_nodes_from(G.nodes(data=True))  # Add all nodes to the new graph

    for u, v, data in G.edges(data=True):
        if data["weight"] >= threshold:
            G_filtered.add_edge(u, v, weight=data["weight"])

    # Remove nodes with degree 0 (no edges)
    isolated_nodes = list(nx.isolates(G_filtered))
    G_filtered.remove_nodes_from(isolated_nodes)

    return G_filtered


def create_graph(posts, idf_scores, words_key="stemmed_words"):
    # Initialize an undirected graph
    G = nx.Graph()
    # posts = posts_for_graph
    # Adding nodes
    for post in posts:
        G.add_node(post["id"], words=post[words_key])

    # Adding edges based on shared stemmed words
    for i, post1 in enumerate(posts):
        for post2 in posts[i + 1 :]:
            # Find common stemmed words
            common_words = set(post1[words_key]) & set(post2[words_key])
            if common_words:
                # Add an edge with a weight equal to the number of common words
                edge_weight = sum(
                    idf_scores.get(word, 0) for word in common_words
                )  # Sum of IDF scores
                G.add_edge(post1["id"], post2["id"], weight=edge_weight)
    return G
