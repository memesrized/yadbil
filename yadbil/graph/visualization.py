import networkx as nx
import plotly.graph_objects as go


def get_graph_plot(G_filtered, idf_scores):
    def get_top_idf_words(words, idf_scores, top_n=5):
        """Returns the top N words with the highest IDF scores."""
        sorted_words = sorted(
            words, key=lambda word: idf_scores.get(word, 0), reverse=True
        )
        return sorted_words[:top_n]

    hover_data = []
    for node, data in G_filtered.nodes(data=True):
        top_words = get_top_idf_words(data["words"], idf_scores)
        hover_data.append(f"Post ID: {node}<br>Top Words: {', '.join(top_words)}")

    # --- Create Plotly Visualization ---
    pos = nx.spring_layout(G_filtered, k=0.3)  # Layout for the filtered graph

    # Extract node positions
    node_x = [pos[node][0] for node in G_filtered.nodes()]
    node_y = [pos[node][1] for node in G_filtered.nodes()]

    # Create edges
    edge_x = []
    edge_y = []
    for edge in G_filtered.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])  # The None creates a break in the line
        edge_y.extend([y0, y1, None])

    # Create the Plotly figure
    fig = go.Figure(
        data=[
            go.Scatter(
                x=edge_x,
                y=edge_y,
                mode="lines",
                line=dict(width=0.5, color="#888"),  # Customize edge appearance
                hoverinfo="none",  # No hover info for edges
            ),
            go.Scatter(
                x=node_x,
                y=node_y,
                mode="markers",
                marker=dict(size=10, color="skyblue"),  # Customize node appearance
                text=hover_data,
                hoverinfo="text",  # Display hover data
            ),
        ],
        layout=go.Layout(
            title="Interactive Post Similarity Graph",
            showlegend=False,
            hovermode="closest",  # Show hover data on closest node
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        ),
    )
    return fig
