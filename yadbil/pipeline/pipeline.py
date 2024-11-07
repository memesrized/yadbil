from pathlib import Path
from typing import Callable, List, Union

from yadbil.pipeline.config import PipelineConfig
from yadbil.pipeline.utils import CREDS_MAPPING, STEPS_MAPPING


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

    @classmethod
    def from_config(cls, config: Union[str, dict, Path]):
        config = PipelineConfig(config)
        steps = []
        for x in config.order:
            if x in STEPS_MAPPING:
                step_cls = STEPS_MAPPING[x]
                config_cls = config[x]
                if "creds" in config_cls:
                    config_cls["creds"] = CREDS_MAPPING[config_cls["creds"]]()
                    steps.append(step_cls(**config_cls))
            else:
                raise ValueError(f"Unknown step: {x}")
        return cls(steps)
