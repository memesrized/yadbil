import json
from dataclasses import dataclass, field

import streamlit as st
import yaml

from yadbil.data.processing.text.processing import TextProcessor
from yadbil.pipeline.config import PipelineConfig
from yadbil.pipeline.utils import STEPS_MAPPING


@st.cache_data
def load_configs(path: str = "configs/ui.yml") -> tuple[dict, PipelineConfig]:
    with open(path) as file:
        ui_config = yaml.safe_load(file)

    config = PipelineConfig(ui_config["CONFIG_PATH"])
    return ui_config, config


# for some reason it takes too long to load with st.cache_data
# as if it's not cached at all
# but maybe copy takes too long, idk
@st.cache_resource
def load_data(path: str) -> list:
    with open(path) as file:
        return [json.loads(line) for line in file]


@st.cache_data
def load_text_processor(config: dict):
    return TextProcessor(**config)


@st.cache_resource
def load_embeddings(config: dict, emb_name: str):
    return STEPS_MAPPING[emb_name].load(
        pretrained_emb_model_path=config.get("emb_model_path", config["output_path"] + "/model.kv"),
        data_path=config["output_path"] + "/emb_table.npy",
    )


# it could be cached in streamlit instead of session state
# cache could be cleaned with each run button ofc
# but cache is for everyone and session state is for a particular user
# also in ideal scenario data should be updated on the fly
@dataclass
class UISessionState:
    similar_posts: list = field(default_factory=list)
    scores: list = field(default_factory=list)
    results: list = field(default_factory=list)
    query: str = ""
    processed_query: str = field(default_factory=str)
