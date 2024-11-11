import argparse
import sys
import traceback
from pathlib import Path
from typing import Optional

from yadbil.pipeline.pipeline import Pipeline
from yadbil.utils.logger import get_logger


logger = get_logger(__name__)


def parse_args(args: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run yadbil pipeline from config.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--config_path", type=Path, help="Path to pipeline config file.")
    return parser.parse_args(args)


def main(args: Optional[list[str]] = None) -> int:
    """Main entry point for the CLI.

    Args:
        args: Command line arguments to parse.

    Returns:
        Exit code (0 for success, non-zero for failure).
    """
    try:
        parsed_args = parse_args(args)
        if not parsed_args.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {parsed_args.config_path}")

        pipeline = Pipeline.from_config(parsed_args.config_path)
        pipeline.run()
        return 0
    except Exception as e:
        logger.error(f"Error: {e}")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
