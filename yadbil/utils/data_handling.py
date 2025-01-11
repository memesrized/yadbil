import json
from typing import Any, Dict


# TODO: I must rework this
# it should be hardcoded path or idk what, how to make it flexible and unified
def get_dict_field(record: Dict[str, Any], record_processed_data_key_list) -> str:
    for x in record_processed_data_key_list:
        record = record[x]
    return record


class JsonCorpus:
    def __init__(self, path=None, data=None, record_processed_data_key_list=None):
        self.record_processed_data_key_list = record_processed_data_key_list or [
            "processed_text",
            "words",
        ]
        self.path = path
        self.data = data

    def __iter__(self):
        if self.data:
            for record in self.data:
                yield get_dict_field(record, self.record_processed_data_key_list)
        elif self.path:
            with open(self.path, "r") as f:
                for line in f:
                    yield get_dict_field(json.loads(line), self.record_processed_data_key_list)
