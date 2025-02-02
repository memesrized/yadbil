import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Optional, Union

import numpy as np
from gensim.models import KeyedVectors
from gensim.models.word2vec import Word2Vec
from tqdm.auto import tqdm

from yadbil.utils.data_handling import JsonCorpus, get_dict_field
from yadbil.utils.logger import get_logger


logger = get_logger(__name__)


class BaseSearch(ABC):
    @abstractmethod
    def load(self, path: str) -> None:
        """Load the search model from the specified path."""
        pass

    @abstractmethod
    def save(self) -> None:
        """Save the search model."""
        pass

    @abstractmethod
    def query(self, query: Any, n: int = 10) -> tuple[list[int], list[float]]:
        """
        Perform a search query and return the top n results.

        Args:
            query: The processed query object.
            n: Number of top results to return.

        Returns:
            A tuple containing a list of result IDs and their corresponding scores.
        """
        pass

    @abstractmethod
    def run(self, data: Optional[list[list[str]]] = None) -> None:
        """
        Run as a step.

        Args:
            data: A list of processed data objects.
        """
        pass


class BaseEmbeddingSearch(BaseSearch, ABC):
    @abstractmethod
    def _embed_and_normalize_query(self, query) -> np.ndarray:
        pass

    def query(self, query, n: int = 10, filtered_ids=None) -> tuple[list[int], list[float]]:
        query = self._embed_and_normalize_query(query)

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
            logger.info("Training embedding model...")
            self.train(data=data)

        data = [get_dict_field(x, self.record_processed_data_key_list) for x in data]
        self.emb_table = np.array(
            [self._embed_and_normalize_query(x) for x in tqdm(data, desc="Embedding process...")]
        )
        self.save()


# TODO: think about generalized load method
class BaseWordEmbeddingSearch(BaseEmbeddingSearch, ABC):
    def __init__(
        self,
        input_path: Union[str, Path] = None,
        output_path: Union[str, Path] = None,
        record_processed_data_key_list: list[str] = None,
        pretrained_emb_model_path: Union[str, Path] = None,
        model_params: dict[str, Any] = None,
    ):
        self.input_path = input_path if isinstance(input_path, Path) or (input_path is None) else Path(input_path)
        self.output_path = output_path if isinstance(output_path, Path) or (output_path is None) else Path(output_path)

        if model_params:
            self.model_params = model_params

        self.record_processed_data_key_list = record_processed_data_key_list or self._record_processed_data_key_list

        if pretrained_emb_model_path is not None:
            self.embeddings = self.KeyedVectorsClass.load(pretrained_emb_model_path)
            self.is_pretrained = True
        else:
            self.embeddings = self.EmbeddingsClass(**self.model_params)
            self.is_pretrained = False

        self.emb_table = None

    @property
    @abstractmethod
    def KeyedVectorsClass(self) -> type[KeyedVectors]:
        pass

    @property
    @abstractmethod
    def EmbeddingsClass(self) -> type[Word2Vec]:
        pass

    @property
    @abstractmethod
    def _record_processed_data_key_list(self) -> list[str]:
        pass

    @property
    def model_params(self) -> dict[str, Any]:
        # params reference:
        # w2v
        # https://github.com/piskvorky/gensim/blob/8b6b69c29fd58a93136e8f591ea9379ac2c8290c/gensim/models/word2vec.py#L241
        # fasttext
        # https://github.com/piskvorky/gensim/blob/8b6b69c29fd58a93136e8f591ea9379ac2c8290c/gensim/models/fasttext.py#L272
        return {
            "vector_size": 128,
            "min_count": 4,
            "epochs": 8,
            "alpha": 0.025,
            "min_alpha": 0.0001,
        }

    def _get_embedding(self, word: str) -> np.ndarray:
        try:
            return self.embeddings[word]
        except KeyError:
            return np.zeros(self.embeddings.vector_size)

    # TODO: urgent, rework this messy OOV handling and normalization
    def _embed_and_normalize_query(self, query: list[str]) -> np.ndarray:
        if not query:
            return np.zeros(self.embeddings.vector_size)
        emb = [self._get_embedding(word) for word in query]
        norm = [np.linalg.norm(x) for x in emb]
        # TODO: handle zero division differently? is epsilon ok?
        emb = np.mean([x / n if n != 0 else x for x, n in zip(emb, norm)], axis=0)
        norm = np.linalg.norm(emb)
        emb = emb / norm if norm != 0 else emb
        if np.isnan(emb).any():
            emb = np.zeros(self.embeddings.vector_size)
        return emb

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
