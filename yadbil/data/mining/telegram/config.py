import json
import logging
import os
from pathlib import Path

from dotenv import load_dotenv


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


# TODO: rework
class TelegramParserConfig:
    def __init__(self, config_path=None):
        load_dotenv()

        # mandatory parameters
        self._config = config_path or self.load_config(os.getenv("TG_PARSING_CONFIG_PATH"))
        self.channels = self._config["channels"]
        self._config = self._config["params"]

        # save intermediate data to file
        self.save_to_disk = self._config.get("save_to_disk", True)
        self.output_dir = Path(self._config.get("output_dir", "./tg_data/"))
        self.channels_info_output_dir = Path(self._config.get("channels_info_output_dir", "./"))
        self.cleaned_data_output_dir = Path(self._config.get("cleaned_data_output_dir", "./tg_data/"))

        # processing parameters
        self.batch_size = self._config.get("batch_size", 100)
        self.retry_limit = self._config.get("retry_limit", 3)
        self.verbose = self._config.get("verbose", True)

        if self.verbose:
            self.log_parameters()

    def load_config(self, path):
        with open(path, "r") as f:
            return json.load(f)

    def log_parameters(self):
        logger.info("Configuration parameters:")
        logger.info(f"Channels: {self.channels}")
        logger.info(f"Batch Size: {self.batch_size}")
        logger.info(f"Retry Limit: {self.retry_limit}")
        logger.info(f"Output Directory: {self.output_dir}")
        logger.info(f"Verbose: {self.verbose}")
