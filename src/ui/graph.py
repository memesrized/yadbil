# import streamlit as st
# import streamlit.components.v1 as components


# class TelegramEmbed(object):
#     """
#     Display the embedded telegram widge for a public telegram url
#     as per https://core.telegram.org/widgets/post

#     Based on https://discuss.streamlit.io/t/dispalying-a-tweet/16061
#     """

#     @st.cache_data(ttl=3600)
#     def fetch_telegram_embed_html(t_url: str):
#         # https://core.telegram.org/widgets/post
#         # split off the t.me part to get the post id.
#         # so https://t.me/EarthJusticeLeague_DataLibrary/11687
#         # becomes EarthJusticeLeague_DataLibrary/11687
#         post_id = t_url.replace("https://t.me/", "")
#         html = f"""
#         <script async src="https://telegram.org/js/telegram-widget.js?22"
#         data-telegram-post="{post_id}" data-width="100%"></script>
#         """
#         return html

#     def __init__(self, t_url, embed_str=False):
#         if not embed_str:
#             self.text = TelegramEmbed.fetch_telegram_embed_html(t_url)
#         else:
#             self.text = f"""
#             <a href='{t_url}' target="_blank" rel="noopener noreferrer">view on Telegram</a>
#             """

#     def _repr_html_(self):
#         """
#         This seems to be needed to work around a bug
#         """
#         return ""

#     def component(self):
#         return components.html(f"<body>{self.text}</body>", height=800)


# TelegramEmbed("https://t.me/durov/242").component()


import streamlit as st
import streamlit.components.v1 as components
from src.graph import find_similar_posts_pagerank  # Adjust the import path as necessary
from src.utils.st_utils import tg_html
from src.graph.io import load_resources

# Configuration Parameters
GRAPH_FILE_PATH = "data/filtered_graph.graphml"
POSTS_FILE_PATH = "data/posts.json"
POSTS_VIEW_FILE_PATH = "data/posts_view.json"
DEFAULT_POST_ID = 1
MIN_POST_ID = 1
MAX_POST_ID = 1000  # Adjust according to your dataset
DEFAULT_NUM_RECOMMENDATIONS = 5
MAX_NUM_RECOMMENDATIONS = 20


G, posts, posts_view = load_resources(
    GRAPH_FILE_PATH, POSTS_FILE_PATH, POSTS_VIEW_FILE_PATH
)

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
