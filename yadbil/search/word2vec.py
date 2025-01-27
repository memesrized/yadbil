from pathlib import Path
from typing import Union

import numpy as np
from gensim.models import KeyedVectors
from gensim.models.word2vec import Word2Vec

from yadbil.search.base import BaseWordEmbeddingSearch
from yadbil.utils.logger import get_logger


logger = get_logger(__name__)


# TODO: change naming?
class Word2VecWrapper(BaseWordEmbeddingSearch):
    @property
    def KeyedVectorsClass(self) -> type[KeyedVectors]:
        return KeyedVectors

    @property
    def EmbeddingsClass(self) -> type[Word2Vec]:
        return Word2Vec

    @property
    def record_processed_data_key_list(self) -> list[str]:
        return ["processed_text", "stemmed_words"]

    @classmethod
    def load(cls, pretrained_emb_model_path: Union[str, Path], data_path: Union[str, Path]) -> "Word2VecWrapper":
        inst = cls()
        inst.embeddings = KeyedVectors.load(pretrained_emb_model_path)
        inst.emb_table = np.load(data_path)
        return inst


if __name__ == "__main__":
    from yadbil.pipeline.config import PipelineConfig

    config = PipelineConfig()

    processor = Word2VecWrapper(config["Word2VecWrapper"])
    processor.run()
