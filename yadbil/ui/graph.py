import streamlit as st
import streamlit.components.v1 as components

from yadbil.graph import find_similar_posts_pagerank
from yadbil.graph.io import load_resources
from yadbil.utils.st_utils import tg_html


# Configuration Parameters
GRAPH_FILE_PATH = "data/filtered_graph.graphml"
POSTS_FILE_PATH = "data/posts.json"
POSTS_VIEW_FILE_PATH = "data/posts_view.json"
DEFAULT_POST_ID = 1
MIN_POST_ID = 1
MAX_POST_ID = 1000  # Adjust according to your dataset
DEFAULT_NUM_RECOMMENDATIONS = 5
MAX_NUM_RECOMMENDATIONS = 20


G, posts, posts_view = load_resources(GRAPH_FILE_PATH, POSTS_FILE_PATH, POSTS_VIEW_FILE_PATH)

# Streamlit UI layout
st.title("Post Recommendation System")

# Sidebar for inputs
with st.sidebar:
    st.header("Input Parameters")

    post_id = st.selectbox("Post ID", G.nodes)
    top_n = st.number_input(
        "Number of Recommendations",
        min_value=1,
        max_value=MAX_NUM_RECOMMENDATIONS,
        value=DEFAULT_NUM_RECOMMENDATIONS,
    )
    # Display input post details
    input_post_details = posts_view["channel1150855655"][str(post_id)]
    button = st.sidebar.button("Find Similar Posts")
    st.markdown("### Input Post Details")
    st.markdown("**Markdown Content:**")
    st.markdown(input_post_details.get("md", "No details available"))


# Main area for output
if button:
    similar_posts = find_similar_posts_pagerank(G, str(post_id), top_n)

    if similar_posts:
        for post_id, score in similar_posts:
            post_details = posts_view["channel1150855655"].get(str(post_id), {})
            md_text = post_details.get("md", "")
            st.markdown("### Post ID: " + str(post_id))
            st.markdown("#### Similarity Score: " + f"{score:.4f}")
            components.html(tg_html("gonzo_ML", str(post_id)), height=800)
            st.markdown("---")  # Line to separate different posts
    else:
        st.write("No similar posts found.")
