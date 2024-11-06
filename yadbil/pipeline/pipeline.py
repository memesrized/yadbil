import json
from pathlib import Path
from typing import Callable, List, Union

import yaml


class Pipeline:
    def __init__(self, steps: List[Callable]):
        self.steps = steps

    def run(self, data=None):
        for step in self.steps:
            if data:
                data = step.run(data)
            else:
                data = step.run()
        return data

    def from_config(self, config: Union[str, dict, Path]):
        raise NotImplementedError
        config = self.load_config(config)

    def load_config(self, config: Union[str, dict, Path]):
        if isinstance(config, dict):
            return config
        if isinstance(config, str):
            config = Path(config)

        if config.suffix == ".json":
            with open(config, "r") as f:
                config = json.load(f)
        elif config.suffix == ".yaml":
            with open(config, "r") as f:
                config = yaml.safe_load(f)
        return config
