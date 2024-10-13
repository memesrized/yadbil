import json
import logging
import os
from pathlib import Path

from dotenv import load_dotenv


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


# TODO: rework
class Config:
    def __init__(self):
        load_dotenv()
        self.api_id = os.getenv("API_ID")
        self.api_hash = os.getenv("API_HASH")
        self.phone_number = os.getenv("PHONE_NUMBER")

        self._config = self.load_config(os.getenv("TG_PARSING_CONFIG_PATH"))
        self.channels = self._config["channels"]
        self._config = self._config["params"]
        self.batch_size = self._config.get("batch_size", 100)
        self.retry_limit = self._config.get("retry_limit", 3)
        self.output_dir = Path(self._config.get("output_dir", "./tg_data/"))
        self.channels_info_output_dir = Path(self._config.get("channels_info_output_dir", "./"))
        self.cleaned_data_output_dir = Path(self._config.get("cleaned_data_output_dir", "./tg_data/"))
        self.verbose = self._config.get("verbose", True)

        if self.verbose:
            self.log_parameters()

    def load_config(self, path):
        with open(path, "r") as f:
            return json.load(f)

    def log_parameters(self):
        logger.info("Configuration parameters:")
        logger.info(f"API ID: {self.api_id}")
        logger.info(f"API Hash: {'*' * len(self.api_hash)}")  # Mask the API hash for security
        logger.info(f"Phone Number: {self.phone_number}")
        logger.info(f"Channels: {self.channels}")
        logger.info(f"Batch Size: {self.batch_size}")
        logger.info(f"Retry Limit: {self.retry_limit}")
        logger.info(f"Output Directory: {self.output_dir}")
        logger.info(f"Verbose: {self.verbose}")
