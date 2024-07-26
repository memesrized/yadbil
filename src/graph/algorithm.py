import networkx as nx


def find_similar_posts_pagerank(G, post_id, top_n=5):
    """
    Finds similar posts using personalized PageRank.

    Parameters:
    - G: The graph of posts.
    - post_id: The ID of the post to find similarities for.
    - top_n: The number of similar posts to return.

    Returns:
    A list of post IDs sorted by their similarity to the given post.
    """
    # Initialize personalization vector
    personalization = {node: 0 for node in G}
    personalization[post_id] = 1

    # Compute personalized PageRank
    pagerank_scores = nx.pagerank(G, personalization=personalization)

    # Exclude the original post and sort the rest based on their PageRank score
    similar_posts = sorted(pagerank_scores.items(), key=lambda x: x[1], reverse=True)

    # Exclude the original node and return the top_n
    return [(node, score) for node, score in similar_posts if node != post_id][:top_n]
