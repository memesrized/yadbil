import json
from pathlib import Path
from typing import Any, Dict, List, Union

from tqdm.auto import tqdm

from yadbil.utils.data_handling import get_dict_field
from yadbil.utils.logger import get_logger


logger = get_logger(__name__)


class DataFilter:
    def __init__(
        self,
        input_path: Union[str, Path] = None,
        output_path: Union[str, Path] = None,
        filters: List[Dict[str, Any]] = None,
    ):
        """Filter data based on provided filters

        Filter dict breakdown:
            - name: str - name of the filter function
            - keys: List[str] - keys to extract from the data (for nested dicts)
            - value: Any - value to compare with
            - bool_to_retain: bool - if True, the data will be retained if the filter is True,
                 and obviously if False, the data will be retained if the filter is False,
                 otherwise the data will be removed

        Filter example:
            {
                "name": "min_len",
                "keys": ["processed_text", "words"],
                "value": 1,
                "bool_to_retain": true
            }

        """
        self.input_path = input_path if isinstance(input_path, Path) else Path(input_path)
        self.output_path = output_path if isinstance(output_path, Path) else Path(output_path)

        self.filters = self.prepare_filters(filters)

    def prepare_filters(self, filters: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        filter_mapping = {
            "min_len": self._min_len_filter,
            "value_eq": self._value_eq_filter,
        }
        for f in filters:
            f["func"] = filter_mapping[f["name"]]
        return filters

    def _min_len_filter(self, data, keys: List[str], min_len: int = 2) -> bool:
        return len(get_dict_field(data, keys)) >= min_len

    def _value_eq_filter(self, data, keys: List[str], value: Any) -> bool:
        return get_dict_field(data, keys) == value

    def apply_filters(self, data: Dict[str, Any]) -> bool:
        for f in self.filters:
            if not f["func"](data, f["keys"], f["value"]) == f["bool_to_retain"]:
                return False
        return True

    # TODO: implement return of processed data if no output path is provided
    def run(self, data=None):
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        counter_filtered = 0
        counter = 0

        if data is None:
            if self.input_path is None:
                raise ValueError("No input data provided.")

        with open(self.input_path) as in_file:
            with open(self.output_path, "w") as out_file:
                for line in tqdm(in_file, desc="Filtering data"):
                    item = json.loads(line)
                    counter += 1
                    if self.apply_filters(item):
                        counter_filtered += 1
                        out_file.write(line)
                        # out_file.write(json.dumps(item, ensure_ascii=False) + "\n")

        logger.info(f"Total number of records: {counter}")
        logger.info(f"Final number of records: {counter_filtered}")
        logger.info(f"Ratio of retained records: {round(counter_filtered / counter, 2)}")


if __name__ == "__main__":
    from yadbil.pipeline.config import PipelineConfig

    config = PipelineConfig()

    processor = DataFilter(config["DataFilter"])
    processor.run()
