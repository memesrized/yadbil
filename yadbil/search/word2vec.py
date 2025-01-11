import json
from pathlib import Path
from typing import Any, Dict, List, Union

import numpy as np
from gensim.models import KeyedVectors
from gensim.models.word2vec import Word2Vec
from tqdm.auto import tqdm

from yadbil.search.base import BaseSearch
from yadbil.utils.data_handling import JsonCorpus, get_dict_field
from yadbil.utils.logger import get_logger


logger = get_logger(__name__)


# TODO: change naming?
class Word2VecWrapper(BaseSearch):
    def __init__(
        self,
        input_path: Union[str, Path] = None,
        output_path: Union[str, Path] = None,
        record_processed_data_key_list: List[str] = (
            "processed_text",
            "stemmed_words",
        ),
        pretrained_emb_model_path: Union[str, Path] = None,
        model_params: Dict[str, Any] = None,
    ):
        self.input_path = input_path if isinstance(input_path, Path) or (input_path is None) else Path(input_path)
        self.output_path = output_path if isinstance(output_path, Path) or (output_path is None) else Path(output_path)

        # params reference:
        # https://github.com/piskvorky/gensim/blob/8b6b69c29fd58a93136e8f591ea9379ac2c8290c/gensim/models/word2vec.py#L241
        if model_params is None:
            model_params = {
                "vector_size": 128,
                "min_count": 4,
                "epochs": 8,
                "alpha": 0.025,
                "min_alpha": 0.0001,
            }

        self.record_processed_data_key_list = record_processed_data_key_list

        if pretrained_emb_model_path is not None:
            self.embeddings = KeyedVectors.load(pretrained_emb_model_path)
            self.is_pretrained = True
        else:
            self.embeddings = Word2Vec(**model_params)
            self.is_pretrained = False

        self.emb_table = None

    @classmethod
    def load(cls, pretrained_emb_model_path: Union[str, Path], data_path: Union[str, Path]) -> "Word2VecWrapper":
        inst = cls()
        inst.embeddings = KeyedVectors.load(pretrained_emb_model_path)
        inst.emb_table = np.load(data_path)
        return inst

    def _get_embedding(self, word: str) -> np.ndarray:
        try:
            return self.embeddings[word]
        except KeyError:
            return np.zeros(self.embeddings.vector_size)

    def _embed_normalize_mean_normalize(self, words: List[str]) -> np.ndarray:
        emb = [self._get_embedding(word) for word in words]
        norm = [np.linalg.norm(x) for x in emb]
        # TODO: handle zero division differently?
        emb = np.mean([x / n if n != 0 else x for x, n in zip(emb, norm)], axis=0)
        norm = np.linalg.norm(emb)
        emb = emb / norm if norm != 0 else emb
        if np.isnan(emb).any():
            emb = np.zeros(self.embeddings.vector_size)
        return emb

    def query(self, query: List[str], n: int = 10, filtered_ids=None) -> List[int]:
        query = self._embed_normalize_mean_normalize(query)

        filtered_ids = np.array(filtered_ids) if filtered_ids is not None else None

        emb_table = self.emb_table if filtered_ids is None else self.emb_table[filtered_ids]

        # emb_table must be normalized at creation time, don't want to do it here
        scores = np.dot(emb_table, query)

        # is it really faster than argsort? or only for large n?
        top_n = np.argpartition(scores, -n)[-n:]
        top_n = sorted(top_n, key=lambda x: scores[x], reverse=True)
        scores = scores[top_n]

        # reverse mapping to original ids
        if filtered_ids is not None:
            top_n = list(filtered_ids[top_n])

        return top_n, scores

    def run(self, data=None):
        if data is None:
            if self.input_path is None:
                raise ValueError("No input data provided.")
            with open(self.input_path, "r") as f:
                data = [json.loads(line) for line in f]

        if not self.is_pretrained:
            logger.info("Training Word2Vec model...")
            self.train(data=data)

        data = [get_dict_field(x, self.record_processed_data_key_list) for x in data]
        self.emb_table = np.array(
            [self._embed_normalize_mean_normalize(x) for x in tqdm(data, desc="Embedding process...")]
        )

        # # normalization to avoid it at query time
        # linalg_norm = np.linalg.norm(self.emb_table, axis=1)[:, None]
        # self.emb_table = self.emb_table / linalg_norm
        self.save()

    # TODO: if trained, then save the model, if loaded, then save the embeddings
    def save(self):
        self.output_path.mkdir(parents=True, exist_ok=True)
        np.save(self.output_path / "emb_table.npy", self.emb_table)
        if not self.is_pretrained:
            # str is necessary, gensim checks for extension by endswith method
            self.embeddings.save(str(self.output_path / "model.kv"))

    def train(self, path_to_corpus: Union[str, Path] = None, data=None):
        # TODO: think of better way to handle this
        corpus = (
            JsonCorpus(path_to_corpus)
            if path_to_corpus is not None
            else JsonCorpus(
                data=data,
                record_processed_data_key_list=self.record_processed_data_key_list,
            )
        )
        self.embeddings.build_vocab(corpus)
        self.embeddings.train(
            corpus_iterable=corpus,
            total_examples=self.embeddings.corpus_count,
            epochs=self.embeddings.epochs,
        )
        self.embeddings = self.embeddings.wv


if __name__ == "__main__":
    from yadbil.pipeline.config import PipelineConfig

    config = PipelineConfig()

    processor = Word2VecWrapper(config["Word2VecWrapper"])
    processor.run()
