import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import bm25s

from yadbil.search.base import BaseSearch
from yadbil.utils.data_handling import get_dict_field


class BM25(BaseSearch):
    def __init__(
        self,
        input_path: Union[str, Path] = None,
        output_path: Union[str, Path] = None,
        record_processed_data_key_list: Tuple[str] = (
            "processed_text",
            "stemmed_words",
        ),
        bm25_params: Dict[str, Any] = None,
    ):
        if bm25_params is None:
            bm25_params = {}

        self.record_processed_data_key_list = record_processed_data_key_list

        self.retriever = bm25s.BM25(**bm25_params)
        self.input_path = input_path if isinstance(input_path, Path) or (input_path is None) else Path(input_path)
        self.output_path = output_path if isinstance(output_path, Path) or (output_path is None) else Path(output_path)

    @classmethod
    def load(cls, path: Union[str, Path]) -> "BM25":
        inst = cls()
        inst.retriever = bm25s.BM25.load(path, load_corpus=True)
        return inst

    def save(self):
        self.retriever.save(self.output_path)

    def run(self, data: Optional[List[List[str]]] = None):
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

        if data is None:
            if self.input_path is None:
                raise ValueError("No input data provided.")

            # TODO: decide how to handle corpus loading and processing and saving
            # now "we" do the handling and you need to keep corpus somewhere near the index
            # but it can be done with the bm25s lib as I understand
            # the question is how to make this lib get the data for index from a particular nested keys/dicts
            # for now it's ok I guess
            with open(self.input_path, "r") as f:
                data = [json.loads(line) for line in f]

        data = [get_dict_field(x, self.record_processed_data_key_list) for x in data]

        self.retriever.index(data)
        self.save()

    def query(self, query: str, n: int = 10):
        results, scores = self.retriever.retrieve([query], k=n)
        return results[0], scores[0]


if __name__ == "__main__":
    from yadbil.pipeline.config import PipelineConfig

    config = PipelineConfig()

    processor = BM25(config["BM25"])
    processor.run()
