import json
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components
import yaml

from yadbil.data.processing.text.processing import TextProcessor
from yadbil.pipeline.config import PipelineConfig
from yadbil.search.bm25 import BM25
from yadbil.ui.utils.st_utils import tg_html


# TODO: rework this mess with session state
if "ui_config" not in st.session_state:
    # TODO: check how to parametrize streamlit app
    with open("configs/ui.yml") as file:
        st.session_state.ui_config = yaml.safe_load(file)

ui_config = st.session_state.ui_config

# Configuration Parameters
CONFIG_PATH = Path(ui_config["CONFIG_PATH"])

if "config" not in st.session_state:
    st.session_state.config = PipelineConfig(CONFIG_PATH)
config = st.session_state.config

if "text_processor" not in st.session_state:
    st.session_state.text_processor = TextProcessor(**config["TextProcessor"])

if "bm25" not in st.session_state:
    st.session_state.bm25 = BM25.load(config["BM25"]["output_path"])

if "data" not in st.session_state:
    with open(config["TextProcessor"]["output_path"]) as file:
        st.session_state.data = [json.loads(line) for line in file]
data = st.session_state.data

# Streamlit UI layout
st.title("Post Search System")

# Sidebar for inputs
with st.sidebar:
    st.header("Input Parameters")

    query = st.session_state.text_processor.process_text(st.text_input("Query"))
    query = query[st.session_state.bm25.record_processed_data_key_list[-1]]
    top_n = st.number_input(
        "Number of search results",
        min_value=1,
        max_value=ui_config["MAX_NUM_RECOMMENDATIONS"],
        value=ui_config["DEFAULT_NUM_RECOMMENDATIONS"],
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
