import json
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components
import yaml

from yadbil.data.processing.text.processing import TextProcessor
from yadbil.pipeline.config import PipelineConfig
from yadbil.search.word2vec import Word2VecWrapper
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

if "w2v" not in st.session_state:
    st.session_state.w2v = Word2VecWrapper.load(
        pretrained_emb_model_path=config["Word2VecWrapper"].get(
            "emb_model_path", config["Word2VecWrapper"]["output_path"] + "/model.kv"
        ),
        data_path=config["Word2VecWrapper"]["output_path"] + "/emb_table.npy",
    )

if "data" not in st.session_state:
    with open(config["Word2VecWrapper"]["input_path"]) as file:
        st.session_state.data = [json.loads(line) for line in file]
data = st.session_state.data

# Streamlit UI layout
st.title("Post Search System")

# Sidebar for inputs
with st.sidebar:
    st.header("Input Parameters")

    query = st.text_input("Query")
    if query:
        query = st.session_state.text_processor.process_text(query)
        query = query[st.session_state.w2v.record_processed_data_key_list[-1]]
        top_n = st.number_input(
            "Number of search results",
            min_value=1,
            max_value=ui_config["MAX_NUM_RECOMMENDATIONS"],
            value=ui_config["DEFAULT_NUM_RECOMMENDATIONS"],
        )

        results, scores = st.session_state.w2v.query(query, n=top_n)
        st.markdown("### Processed query:")
        st.markdown(query)
    button = st.button("Find Similar Posts")


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
