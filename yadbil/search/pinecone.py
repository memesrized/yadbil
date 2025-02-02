import json
from pathlib import Path
from typing import Optional, Union

import numpy as np
from pinecone import ServerlessSpec
from pinecone.core.openapi.data.model.scored_vector import ScoredVector
from pinecone.grpc import PineconeGRPC as Pinecone

from yadbil.pipeline.creds import PineconeCreds
from yadbil.search.base import BaseSearch
from yadbil.utils.logger import get_logger


logger = get_logger(__name__)


class PineconeSearch(BaseSearch):
    def __init__(
        self,
        input_path: Union[str, Path] = None,
        index_name: str = "embeddings",
        dimension: int = 3072,
        metric: str = "cosine",
        creds: PineconeCreds = None,
        namespace: str = "yadbil",
        cloud: str = "aws",
        region: str = "us-east-1",
        # Use host if provided, otherwise use index_name
        # https://docs.pinecone.io/guides/data/target-an-index
        host: Optional[str] = None,
    ):
        self.input_path = Path(input_path) if input_path else None
        self.index_name = index_name
        self.dimension = dimension
        self.metric = metric
        self.namespace = namespace
        self.cloud = cloud
        self.region = region
        self.host = host
        self.index = None
        self.pc = Pinecone(api_key=creds.api_key)

    @classmethod
    def load(cls, path: str) -> "PineconeSearch":
        """Load configuration from JSON file and initialize connection.

        Args:
            path: Path to JSON config file containing Pinecone parameters

        Returns:
            Initialized PineconeSearch instance ready for querying
        """
        with open(path, "r") as f:
            config = json.load(f)
        instance = cls(**config)
        # TODO: move to init with if and remove?
        instance.index = (
            instance.pc.Index(host=instance.host) if instance.host else instance.pc.Index(name=instance.index_name)
        )
        return instance

    def save(self) -> None:
        """Nothing to save as data is stored in Pinecone."""
        pass

    def _init_index(self):
        """Initialize Pinecone index if not already done."""
        if self.index is None:
            if self.index_name not in self.pc.list_indexes():
                logger.info(f"Creating index: {self.index_name}")
                self.pc.create_index(
                    name=self.index_name,
                    dimension=self.dimension,
                    metric=self.metric,
                    spec=ServerlessSpec(
                        cloud=self.cloud,
                        region=self.region,
                    ),
                    deletion_protection="disabled",
                )
            # Use host if provided, otherwise use index_name
            self.index = self.pc.Index(host=self.host) if self.host else self.pc.Index(name=self.index_name)

    def query(self, query: np.ndarray, n: int = 10, filter: Optional[dict] = None) -> list[ScoredVector]:
        """Query Pinecone index with vector.

        Args:
            query: Query vector
            n: Number of results to return
            filter: Optional metadata filter dictionary

        Returns:
            list[ScoredVector]: List of matched vectors with their scores
        """
        response = self.index.query(
            namespace=self.namespace,
            vector=query.tolist(),  # Convert numpy array to list
            top_k=n,
            include_values=False,
            filter=filter,
        )
        return response.matches

    def run(self, data: Optional[np.ndarray] = None) -> None:
        """Store vectors in Pinecone index.

        Args:
            data: Optional numpy array of vectors to store. If None, data will be loaded
                 from input_path.

        Raises:
            ValueError: If neither data nor input_path is provided.
        """
        if data is None:
            if self.input_path is None:
                raise ValueError("No input data provided.")
            data = np.load(self.input_path)

        self._init_index()

        # Prepare vectors with IDs
        vectors = [(str(i), vec.tolist(), None) for i, vec in enumerate(data)]

        # Upsert in batches of 100
        batch_size = 100
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i : i + batch_size]
            self.index.upsert(vectors=batch, namespace=self.namespace)
            logger.info(f"Uploaded vectors {i} to {i + len(batch)}")


if __name__ == "__main__":
    from yadbil.pipeline.config import PipelineConfig

    config = PipelineConfig()

    processor = PineconeSearch(**config["PineconeSearch"])
    processor.run()
