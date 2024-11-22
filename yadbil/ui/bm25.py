import json
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from yadbil.data.processing.text.processing import TextProcessor
from yadbil.pipeline.config import PipelineConfig
from yadbil.search.bm25 import BM25
from yadbil.ui.utils.st_utils import tg_html


# Configuration Parameters
CONFIG_PATH = Path("configs/pipeline.yml")
print(CONFIG_PATH.absolute())

DEFAULT_NUM_RECOMMENDATIONS = 10
MAX_NUM_RECOMMENDATIONS = 20

config = PipelineConfig(CONFIG_PATH)
text_processor = TextProcessor(**config["TextProcessor"])

if "bm25" not in st.session_state:
    st.session_state.bm25 = BM25.load(config["BM25"]["output_path"])
    # st.session_state.bm25 = bm25s.BM25.load("data/bm_25_index_tg", load_corpus=False)

with open(config["TextProcessor"]["output_path"]) as file:
    data = [json.loads(line) for line in file]

# Streamlit UI layout
st.title("Post Search System")

# Sidebar for inputs
with st.sidebar:
    st.header("Input Parameters")

    query = text_processor.process_text(st.text_input("Query"))
    query = query[st.session_state.bm25.record_processed_data_key_list[-1]]
    top_n = st.number_input(
        "Number of search results",
        min_value=1,
        max_value=MAX_NUM_RECOMMENDATIONS,
        value=DEFAULT_NUM_RECOMMENDATIONS,
    )

    results, scores = st.session_state.bm25.query(query, n=top_n)

    button = st.sidebar.button("Find Similar Posts")
    st.markdown("### Processed query:")
    st.markdown(query)


# Main area for output
if button:
    similar_posts = [data[i] for i in results]

    if similar_posts:
        for i, post in enumerate(similar_posts):
            if scores[i] <= 0:
                continue
            st.markdown("### Post ID: " + str(post["id"]))
            st.markdown("#### Similarity Score: " + f"{scores[i]:.4f}")
            with st.expander("text"):
                st.markdown(post["orig_text"])
            with st.expander("post"):
                # TODO: try to add scroll into html
                components.html(tg_html(post["channel"], str(post["id"])), height=800)

            st.markdown("---")  # Line to separate different posts
    else:
        st.write("No similar posts found.")
