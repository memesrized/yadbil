from abc import ABC, abstractmethod
from typing import Any, List, Optional, Tuple


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
    def query(self, query: Any, n: int = 10) -> Tuple[List[int], List[float]]:
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
    def run(self, data: Optional[List[List[str]]] = None) -> None:
        """
        Run as a step.

        Args:
            data: A list of processed data objects.
        """
        pass
