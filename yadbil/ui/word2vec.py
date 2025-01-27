from time import perf_counter

import streamlit as st
import streamlit.components.v1 as components

from yadbil.ui.utils.search import (
    UISessionState,
    load_configs,
    load_data,
    load_embeddings,
    load_text_processor,
)
from yadbil.ui.utils.st_utils import tg_html
from yadbil.utils.logger import get_logger


logger = get_logger(__name__, level="DEBUG")

logger.debug("New run")
t0 = perf_counter()


if "state" not in st.session_state:
    st.session_state.state = UISessionState()

# just to make it easier to access
state = st.session_state.state

logger.debug(f"Time to load: {perf_counter() - t0}")
t0 = perf_counter()


ui_config, config = load_configs()
logger.debug(f"Time to load config: {perf_counter() - t0}")
t0 = perf_counter()

data = load_data(config["Word2VecWrapper"]["input_path"])
logger.debug(f"Time to load data: {perf_counter() - t0}")
t0 = perf_counter()

emb = load_embeddings(config["Word2VecWrapper"], "Word2VecWrapper")
logger.debug(f"Time to load emb: {perf_counter() - t0}")
t0 = perf_counter()

text_processor = load_text_processor(config["TextProcessor"])
logger.debug(f"Time to text processor: {perf_counter() - t0}")
t0 = perf_counter()


# APP
st.title("Post Search System")

# INPUTS
with st.sidebar:
    st.header("Input Parameters")
    with st.form("input"):
        query = st.text_input("Query")  # value=state.query won't work here
        top_n = st.number_input(
            "Number of search results",
            min_value=1,
            max_value=ui_config["MAX_NUM_RECOMMENDATIONS"],
            value=ui_config["DEFAULT_NUM_RECOMMENDATIONS"],
        )
        button = st.form_submit_button("Find Similar Posts")

logger.debug(f"Time to draw sidebar: {perf_counter() - t0}")
t0 = perf_counter()

# PROCESSING BUTTON
if button:
    if query:
        processed_query = text_processor.process_text(query)
        processed_query = processed_query[emb.record_processed_data_key_list[-1]]
        results, scores = emb.query(processed_query, n=top_n)

        state = UISessionState(
            similar_posts=[data[i] for i in results],
            scores=scores,
            results=results,
            query=query,
            processed_query=processed_query,
        )
        st.session_state.state = state

logger.debug(f"Time to process query: {perf_counter() - t0}")
t0 = perf_counter()

# DISPLAY QUERY
with st.sidebar:
    st.markdown("### Processed query:")
    st.markdown(state.processed_query)
    st.markdown("### Query:")
    st.markdown(state.query)


# DISPLAY RESULTS
if state.similar_posts:
    for i, post in enumerate(state.similar_posts):
        st.markdown(f"### Similarity Score: {state.scores[i]:.4f}")
        st.markdown(f"Post: https://t.me/{str(post['channel'])}/{str(post['id'])}")
        with st.expander("text"):
            st.markdown(post["orig_text"])
        with st.expander("Embedded post"):
            # TODO: how to make height dynamic?
            components.html(
                tg_html(post["channel"], str(post["id"])),
                height=ui_config["TG_POST_HEIGHT"],
                scrolling=True,
            )
        st.markdown("---")  # Line to separate different posts
else:
    st.write("No similar posts found.")

logger.debug(f"Time to display results: {perf_counter() - t0}")
logger.debug("End of run")
