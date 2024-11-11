import json
from collections import defaultdict
from pathlib import Path

from tqdm import tqdm

from yadbil.utils.logger import get_logger


logger = get_logger(__name__)


class TelegramDataProcessor:
    def __init__(
        self,
        input_dir: Path,
        output_dir: Path,
        channels_info_dir: Path,
    ):
        channels_info_dir = Path(channels_info_dir) if isinstance(channels_info_dir, str) else channels_info_dir
        self.channels_info_path = channels_info_dir / "channels_meta.json"
        self.output_dir = Path(output_dir) if isinstance(output_dir, str) else output_dir
        self.input_dir = Path(input_dir) if isinstance(input_dir, str) else input_dir

    def sub_urls(self, data):
        text = data["message"]
        urls_to_replace = [
            ent["entity"]["extracted_text"] for ent in data["entities"] if ent["entity"]["type"] == "MessageEntityUrl"
        ]
        urls_to_replace = sorted(urls_to_replace, key=len, reverse=True)
        for url in urls_to_replace:
            text = text.replace(url, " ")
        return text.strip()

    def process_reactions(self, reactions):
        rs = defaultdict(int)
        for reaction in reactions:
            rs[reaction["emoticon"]] += reaction["count"]
        return dict(rs)

    def keep_or_not(self, data, text_length=40):
        if data["message"] is None or len(data["message"]) < text_length:
            return False
        if self.channels and data["fwd_from"] and data["fwd_from"].get("from_id", {}).get("id") in self.channels:
            return False
        return True

    def process_record(self, data, channel):
        return {
            "channel": channel,
            "id": data["id"],
            "date": data["date"],
            "orig_text": data["message"],
            "text_no_links": self.sub_urls(data),
            "views": data["views"],
            "reply_to_msg_id": (data["reply_to"]["reply_to_msg_id"] if data["reply_to"] else None),
            "fwd_from_chnl": (data["fwd_from"].get("from_id", {}).get("id") if data["fwd_from"] else None),
            "ents": data["entities"],
            "reactions": (self.process_reactions(data["reactions"]) if data["reactions"] else None),
        }

    def run(self):
        logger.info("Loading channels info")
        with open(self.channels_info_path) as file:
            self.channels = [ch["id"] for ch in json.load(file)]
        self.output_dir.mkdir(parents=True, exist_ok=True)

        results = []
        for chl in tqdm(list(self.input_dir.glob("*")), desc="Processing channels"):
            with open(chl) as file:
                (self.output_dir / "channels").mkdir(exist_ok=True, parents=True)
                with open(self.output_dir / "channels" / chl.name, "w") as file_out:
                    for line in tqdm(file):
                        line = json.loads(line)
                        if self.keep_or_not(line):
                            try:
                                res = self.process_record(line, chl.stem)
                                results.append(res)
                                file_out.write(json.dumps(res, ensure_ascii=False))
                                file_out.write("\n")
                            except Exception as e:
                                print(e)
                                print(line)
                                raise e
        logger.info("Finished processing")
        logger.info(f"Saving all_channels.jsonl at {self.output_dir}")
        with open(self.output_dir / "all_channels.jsonl", "w") as file:
            for result in results:
                file.write(json.dumps(result, ensure_ascii=False))
                file.write("\n")
        logger.info("Saved all_channels.jsonl")


if __name__ == "__main__":
    from yadbil.pipeline.config import PipelineConfig

    config = PipelineConfig()
    processor = TelegramDataProcessor(
        **config["TelegramDataProcessor"],
    )
    processor.run()
