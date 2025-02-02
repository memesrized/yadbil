from pathlib import Path
from typing import Union

import numpy as np
from gensim.models.fasttext import FastText, FastTextKeyedVectors

from yadbil.search.base import BaseWordEmbeddingSearch
from yadbil.utils.logger import get_logger


logger = get_logger(__name__)


# TODO: change naming?
class FastTextWrapper(BaseWordEmbeddingSearch):
    @property
    def KeyedVectorsClass(self) -> type[FastTextKeyedVectors]:
        return FastTextKeyedVectors

    @property
    def EmbeddingsClass(self) -> type[FastText]:
        return FastText

    @property
    def _record_processed_data_key_list(self) -> list[str]:
        return ["processed_text", "words"]

    @classmethod
    def load(cls, pretrained_emb_model_path: Union[str, Path], data_path: Union[str, Path]) -> "FastTextWrapper":
        inst = cls()
        inst.embeddings = FastTextKeyedVectors.load(pretrained_emb_model_path)
        inst.emb_table = np.load(data_path)
        return inst


if __name__ == "__main__":
    from yadbil.pipeline.config import PipelineConfig

    config = PipelineConfig()

    processor = FastTextWrapper(config["FastTextWrapper"])
    processor.run()
