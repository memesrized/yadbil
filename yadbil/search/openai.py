from pathlib import Path
from typing import Union

import numpy as np
from openai import OpenAI

from yadbil.pipeline.creds import OpenAICreds
from yadbil.search.base import BaseEmbeddingSearch


class Embedder:
    def __init__(self, api_key: str, model: str = "text-embedding-3-small"):
        """
        Initialize the Embedder with the provided API key and model.

        :param api_key: Your OpenAI API key.
        :param model: The OpenAI embeddings model to use.
        """
        self.client = OpenAI(api_key=api_key)
        self.model = model

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
            print("Error fetching embedding:", e)
            return []


# TODO: add matryoshka reduction
# TODO: add batch processing
class OpenAISearch(BaseEmbeddingSearch):
    def __init__(
        self,
        input_path: Union[str, Path] = None,
        output_path: Union[str, Path] = None,
        creds: OpenAICreds = None,
        record_processed_data_key_list: list[str] = None,
        model: str = "text-embedding-3-small",
    ):
        self.input_path = Path(input_path) if input_path else None
        self.output_path = Path(output_path) if output_path else None
        self.record_processed_data_key_list = record_processed_data_key_list or ["orig_text"]
        self.embedder = Embedder(api_key=creds.api_key, model=model)
        self.emb_table = None
        self.is_pretrained = True  # OpenAI models are always pretrained

    def load(self, path: str) -> None:
        self.emb_table = np.load(Path(path) / "emb_table.npy")

    def save(self) -> None:
        if self.output_path and self.emb_table is not None:
            self.output_path.mkdir(parents=True, exist_ok=True)
            np.save(self.output_path / "emb_table.npy", self.emb_table)

    def _embed_and_normalize_query(self, query: Union[str, list[str]]) -> np.ndarray:
        if isinstance(query, list):
            query = " ".join(query)

        embedding = self.embedder.get_embedding(query)
        if not embedding:
            return np.zeros(3072)  # Default dimension for text-embedding-3-small
        return embedding  # normalized by default


# Example usage:
if __name__ == "__main__":
    from yadbil.pipeline.config import PipelineConfig

    config = PipelineConfig()

    processor = OpenAISearch(**config["OpenAISearch"])
    processor.run()
