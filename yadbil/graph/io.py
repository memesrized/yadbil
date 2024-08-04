import json

import networkx as nx

def load_resources(graph_path, posts_path, posts_view_path):
    # Load the graph
    G = nx.read_graphml(graph_path)

    # Convert node attributes back from JSON strings
    for node, attrs in G.nodes(data=True):
        for attr_key, attr_value in attrs.items():
            try:
                # Attempt to load the attribute value from JSON string
                attrs[attr_key] = json.loads(attr_value)
            except json.JSONDecodeError:
                # In case the value is not a JSON string, keep it as is
                pass

    # Assuming loading posts and posts_view as before
    with open(posts_path) as f:
        posts = json.load(f)
    with open(posts_view_path) as f:
        posts_view = json.load(f)

    return G, posts, posts_view
