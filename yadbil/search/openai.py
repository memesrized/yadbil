import json
from pathlib import Path
from typing import Union

import numpy as np
from openai import OpenAI
from tqdm.auto import tqdm

from yadbil.pipeline.creds import OpenAICreds
from yadbil.search.base import BaseEmbeddingSearch
from yadbil.utils.data_handling import get_dict_field
from yadbil.utils.logger import get_logger
from yadbil.utils.retry import retry_with_backoff


logger = get_logger(__name__)


class Embedder:
    def __init__(self, api_key: str, model: str = "text-embedding-3-small", emb_dim: int = 1536):
        """
        Initialize the Embedder with the provided API key and model.

        :param api_key: Your OpenAI API key.
        :param model: The OpenAI embeddings model to use.
        """
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.emb_dim = emb_dim

    # TODO: keep only batch?
    @retry_with_backoff()
    def get_embedding(self, text: str) -> list:
        """
        Retrieve the embedding vector for the provided text using OpenAI's API.

        :param text: The input text to be embedded.
        :return: A list of floats representing the embedding vector.
        """
        try:
            response = self.client.embeddings.create(input=text, model=self.model)
            # The API returns embeddings in the data array
            embedding = response.data[0].embedding
            return embedding
        except Exception as e:
            logger.error("Error fetching embedding: %s", e)
            return np.zeros(self.emb_dim)

    @retry_with_backoff()
    def get_embeddings_batch(self, texts: list[str]) -> list:
        """
        Retrieve the embedding vectors for the provided list of texts using OpenAI's API.

        :param texts: A list of input texts to be embedded.
        :return: A list of lists of floats representing the embedding vectors.
        """
        try:
            response = self.client.embeddings.create(input=texts, model=self.model)
            # The API returns embeddings in the data array
            embeddings = [item.embedding for item in response.data]
            return embeddings
        except Exception as e:
            logger.error("Error fetching embeddings: %s", e)
            return [np.zeros(self.emb_dim) for _ in range(len(texts))]


# TODO: add matryoshka reduction
# TODO: add batch processing
# TODO: add optimized requests (1M tokens per minute is max)
# check this https://cookbook.openai.com/examples/how_to_handle_rate_limits for smth useful
class OpenAISearch(BaseEmbeddingSearch):
    def __init__(
        self,
        input_path: Union[str, Path] = None,
        output_path: Union[str, Path] = None,
        creds: OpenAICreds = None,
        record_processed_data_key_list: list[str] = None,
        model: str = "text-embedding-3-small",
        batch_size: int = 1,
    ):
        self.input_path = Path(input_path) if input_path else None
        self.output_path = Path(output_path) if output_path else None
        self.record_processed_data_key_list = record_processed_data_key_list or ["orig_text"]
        self.embedder = Embedder(api_key=creds.api_key, model=model)
        self.emb_table = None
        # looks like max batch size is 2048
        # https://community.openai.com/t/embeddings-api-max-batch-size/655329/3
        self.batch_size = min(batch_size, 2048)

    def load(self, path: str) -> None:
        self.emb_table = np.load(Path(path) / "emb_table.npy")

    def save(self) -> None:
        if self.output_path and self.emb_table is not None:
            self.output_path.mkdir(parents=True, exist_ok=True)
            np.save(self.output_path / "emb_table.npy", self.emb_table)
        elif not self.output_path:
            raise ValueError("Output path not provided.")

    # TODO: use only batch?
    def _embed_and_normalize_query(self, query: str) -> np.ndarray:
        embedding = self.embedder.get_embedding(query)
        return embedding  # normalized by default

    def _embed_and_normalize_batch(self, batch: list[str]) -> np.ndarray:
        embeddings = self.embedder.get_embeddings_batch(batch)
        return embeddings

    def run(self, data=None):
        if data is None:
            if self.input_path is None:
                raise ValueError("No input data provided.")
            with open(self.input_path, "r") as f:
                data = [json.loads(line) for line in f]

        data = [get_dict_field(x, self.record_processed_data_key_list) for x in data]

        # Added batch processing logic if batch_size > 1
        if self.batch_size > 1:
            embeddings = []
            for i in tqdm(range(0, len(data), self.batch_size), desc="Embedding process..."):
                batch = data[i : i + self.batch_size]
                batch_embeddings = self._embed_and_normalize_batch(batch)
                embeddings.extend(batch_embeddings)
            self.emb_table = np.array(embeddings)
        else:
            self.emb_table = np.array(
                [self._embed_and_normalize_query(x) for x in tqdm(data, desc="Embedding process...")]
            )
        self.save()


# Example usage:
if __name__ == "__main__":
    from yadbil.pipeline.config import PipelineConfig

    config = PipelineConfig()

    processor = OpenAISearch(**config["OpenAISearch"])
    processor.run()
