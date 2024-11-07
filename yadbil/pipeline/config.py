import json
from pathlib import Path
from typing import Any, Dict, List, Union

import yaml


# TODO: do we need access as class attribute?
class PipelineConfig:
    def __init__(self, config_path: Union[str, Path] = "configs/pipeline.yml"):
        self.config_path = Path(config_path) if isinstance(config_path, str) else config_path
        self.config: Dict[str, Dict[str, Any]] = {}
        self.order: List[str] = []
        self._load_config()

    def _load_config(self) -> None:
        """Load and parse the YAML configuration file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        suffix = self.config_path.suffix.lower()
        with open(self.config_path, "r") as f:
            if suffix == ".yml" or suffix == ".yaml":
                raw_config = yaml.safe_load(f)
            elif suffix == ".json":
                raw_config = json.load(f)
            else:
                raise ValueError(f"Unsupported file format: {suffix}. Use .yml, .yaml, or .json")

        self.order = [item["name"] for item in raw_config]
        # Convert list of dicts to dict with name as key
        self.config = {item["name"]: item["parameters"] for item in raw_config}

    def __getitem__(self, key: str) -> Dict[str, Any]:
        """Allow dictionary-style access to configuration."""
        return self.config[key]

    def get(self, key: str, default: Any = None) -> Dict[str, Any]:
        """Get configuration with a default value if key doesn't exist."""
        return self.config.get(key, default)

    def __contains__(self, key: str) -> bool:
        """Enable 'in' operator for config."""
        return key in self.config
