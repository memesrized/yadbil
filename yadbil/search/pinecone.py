import json
from pathlib import Path
from typing import Optional, Union

import numpy as np
from pinecone import ServerlessSpec
from pinecone.core.openapi.data.model.scored_vector import ScoredVector

from yadbil.pipeline.config import PipelineConfig
from yadbil.pipeline.creds import PineconeCreds
from yadbil.search.base import BaseSearch
from yadbil.utils.logger import get_logger


try:
    from pinecone.grpc import PineconeGRPC as Pinecone
except ImportError:
    from pinecone import Pinecone


logger = get_logger(__name__)


class PineconeSearch(BaseSearch):
    def __init__(
        self,
        input_path: Union[str, Path] = None,
        input_path_data: Union[str, Path] = None,
        index_name: str = "embeddings",
        dimension: int = 1536,
        metric: str = "cosine",
        creds: PineconeCreds = None,
        namespace: str = "yadbil",
        cloud: str = "aws",
        region: str = "us-east-1",
        # Use host if provided, otherwise use index_name
        # https://docs.pinecone.io/guides/data/target-an-index
        host: Optional[str] = None,
        data_fields: Optional[dict] = None,
        batch_size: int = 100,
    ):
        self.input_path = Path(input_path) if input_path else None
        self.input_path_data = Path(input_path_data) if input_path_data else None
        self.index_name = index_name
        self.dimension = dimension
        self.metric = metric
        self.namespace = namespace
        self.cloud = cloud
        self.region = region
        self.host = host
        self.index = None
        self.pc = Pinecone(api_key=creds.api_key)
        if self.index_name in self._list_indexes_to_names():
            self.index = self.pc.Index(host=self.host) if self.host else self.pc.Index(name=self.index_name)
        self.data_fields = data_fields
        self.batch_size = batch_size

    def _list_indexes_to_names(self):
        """List all indexes in Pinecone."""
        indexes = self.pc.list_indexes()
        return [x["name"] for x in indexes]

    def _load_text_data(self):
        """Load data from input_path."""
        if self.input_path_data is None:
            raise ValueError("No input data provided.")
        with open(self.input_path_data) as file:
            data = [json.loads(line.strip()) for line in file]
        return data

    def _filter_record_fields(self, record: dict) -> dict:
        """Filter record fields."""
        if self.data_fields is None:
            return record
        elif self.data_fields["keep"]:
            return {k: v for k, v in record.items() if k in self.data_fields["keep"]}
        elif self.data_fields["drop"]:
            return {k: v for k, v in record.items() if k not in self.data_fields["drop"]}
        else:
            raise ValueError("Invalid data_fields configuration, must specify 'keep' or 'drop'.")

    # TODO: rework
    @classmethod
    def load(cls, config_path: str) -> "PineconeSearch":
        """Load configuration from JSON file and initialize connection.

        Args:
            config_path: Path to yaml pipeline config file containing Pinecone parameters

        Returns:
            Initialized PineconeSearch instance ready for querying
        """
        config = PipelineConfig(config_path)
        config["PineconeSearch"]["creds"] = PineconeCreds()
        instance = cls(**config)
        return instance

    def save(self) -> None:
        """Nothing to save as data is stored in Pinecone."""
        pass

    # TODO: rework to return index instead or set it????
    def _init_index(self):
        """Initialize Pinecone index if not already done."""
        if self.index is None:
            if self.index_name not in self._list_indexes_to_names():
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

    def query(
        self,
        query_vector: Union[np.ndarray, list],
        n: int = 10,
        filter: Optional[dict] = None,
        include_values: bool = False,
        include_metadata: bool = True,
    ) -> list[ScoredVector]:
        """Query Pinecone index with vector.

        Args:
            query_vector: Query vector
            n: Number of results to return
            filter: Optional metadata filter dictionary

        Returns:
            list[ScoredVector]: List of matched vectors with their scores
        """
        response = self.index.query(
            namespace=self.namespace,
            vector=list(query_vector),  # Convert numpy array to list
            top_k=n,
            include_values=include_values,
            include_metadata=include_metadata,
            filter=filter,
        )
        return [x.to_dict() for x in response.matches]

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

        records = self._load_text_data()
        records = [self._filter_record_fields(x) for x in records]

        self._init_index()

        for i in range(0, len(data), self.batch_size):
            batch = data[i : i + self.batch_size]
            batch_data = records[i : i + self.batch_size]
            batch = [
                {
                    "id": batch_data[j]["uid"],
                    "values": batch[j].tolist(),
                    "metadata": batch_data[j],
                }
                for j in range(len(batch))
            ]
            self.index.upsert(vectors=batch, namespace=self.namespace)
            # TODO: improve logging
            logger.info(f"Uploaded vectors {i} to {i + len(batch)}")


if __name__ == "__main__":
    config = PipelineConfig()

    processor = PineconeSearch(**config["PineconeSearch"])
    processor.run()
