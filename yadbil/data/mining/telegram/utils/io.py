import json
from pathlib import Path
from typing import Dict, List, Union

import aiofiles


async def save_messages_to_file(channel: str, messages: List[Dict], base_path: Union[Path, str]):
    """
    Save a batch of messages from a channel to a JSONL file.

    Args:
        channel (str): The name of the channel.
        messages (List[Dict]): A list of processed message dictionaries.
        base_path (Path): The directory path where files will be saved.
    """
    if isinstance(base_path, str):
        base_path = Path(base_path)

    base_path.mkdir(parents=True, exist_ok=True)

    filename = base_path / f"{channel.replace('/', '_')}.jsonl"

    async with aiofiles.open(filename, "a", encoding="utf-8") as f:
        for message in messages:
            json_line = json.dumps(message, ensure_ascii=False)
            await f.write(json_line + "\n")
