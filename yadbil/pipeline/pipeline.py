from pathlib import Path
from typing import Callable, List, Union

from yadbil.pipeline.config import PipelineConfig
from yadbil.pipeline.utils import CREDS_MAPPING, STEPS_MAPPING
from yadbil.utils.logger import get_logger


logger = get_logger(__name__)


class Pipeline:
    def __init__(self, steps: List[Callable]):
        self.steps = steps

    def run(self, data=None):
        for step in self.steps:
            if data:
                logger.info(f"Running step {step.__class__.__name__} with data...")
                data = step.run(data)
            else:
                logger.info(f"Running step {step.__class__.__name__}...")
                data = step.run()
        logger.info("Pipeline finished")
        return data

    @classmethod
    def from_config(cls, config: Union[str, dict, Path]):
        config = PipelineConfig(config)
        logger.info("Pipeline config:" + str(config))
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
