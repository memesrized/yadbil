import json

import bm25s
import streamlit as st
import streamlit.components.v1 as components

from yadbil.data.text.processing import TextPreprocessor
from yadbil.utils.st_utils import tg_html


text_processor = TextPreprocessor()


if "bm25" not in st.session_state:
    st.session_state.bm25 = bm25s.BM25.load("data/bm_25_index_tg", load_corpus=False)

with open("data/tg_data/whole_stemmed.json") as file:
    data = json.load(file)

# Configuration Parameters
DEFAULT_NUM_RECOMMENDATIONS = 10
MAX_NUM_RECOMMENDATIONS = 20


# Streamlit UI layout
st.title("Post Recommendation System")

# Sidebar for inputs
with st.sidebar:
    st.header("Input Parameters")

    query = text_processor.preprocess(st.text_input("Query"))["stemmed_words"]
    top_n = st.number_input(
        "Number of search results",
        min_value=1,
        max_value=MAX_NUM_RECOMMENDATIONS,
        value=DEFAULT_NUM_RECOMMENDATIONS,
    )

    results, scores = st.session_state.bm25.retrieve([query], k=top_n)

    button = st.sidebar.button("Find Similar Posts")
    st.markdown("### Processed query:")
    st.markdown(query)


# Main area for output
if button:
    similar_posts = [data[i] for i in results[0]]

    if similar_posts:
        for i, post in enumerate(similar_posts):
            st.markdown("### Post ID: " + str(post["id"]))
            st.markdown("#### Similarity Score: " + f"{scores[0][i]:.4f}")
            with st.expander("text"):
                st.markdown(post["orig_text"])
            with st.expander("post"):
                # TODO: try to add scroll into html
                components.html(tg_html(post["channel"], str(post["id"])), height=800)

            st.markdown("---")  # Line to separate different posts
    else:
        st.write("No similar posts found.")
