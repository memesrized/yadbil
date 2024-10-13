# load data from jsonl lazy?

# deduplicate
import json
from collections import defaultdict

from tqdm import tqdm

from yadbil.data.source.telegram.scraping.config import Config


def sub_urls(data):
    text = data["message"]
    urls_to_replace = [
        ent["entity"]["extracted_text"] for ent in data["entities"] if ent["entity"]["type"] == "MessageEntityUrl"
    ]

    # ordering needed for cases with links nested in other links
    urls_to_replace = sorted(urls_to_replace, key=len, reverse=True)

    # TODO: regexp to make it fancy??? do we need it?
    for url in urls_to_replace:
        text = text.replace(url, " ")
    return text.strip()


def process_reactions(reactions):
    # to handle custom emojies that have the same emoticon as "id"
    # the idea is to just sum them
    rs = defaultdict(int)
    for reaction in reactions:
        rs[reaction["emoticon"]] += reaction["count"]
    return dict(rs)


def keep_or_not(data, text_length=40, channels=None):
    if data["message"] is None or len(data["message"]) < text_length:
        return False
    if channels and data["fwd_from"] and data["fwd_from"].get("from_id", {}).get("id") in channels:
        return False
    return True


def process_record(data):
    return {
        "id": data["id"],
        "date": data["date"],
        "orig_text": data["message"],
        "text_no_links": sub_urls(data),
        "views": data["views"],
        "reply_to_msg_id": (data["reply_to"]["reply_to_msg_id"] if data["reply_to"] else None),
        "fwd_from_chnl": data["fwd_from"].get("from_id", {}).get("id") if data["fwd_from"] else None,
        "ents": data["entities"],
        "reactions": (process_reactions(data["reactions"]) if data["reactions"] else None),
    }


def main():
    config = Config()

    with open(config.channels_info_output_dir / "channels_meta.json") as file:
        channels = [ch["id"] for ch in json.load(file)]

    config.cleaned_data_output_dir.mkdir(parents=True, exist_ok=True)

    for chl in tqdm(list(config.output_dir.glob("*"))):
        with open(chl) as file:
            with open(config.cleaned_data_output_dir / chl.name, "w") as file_out:
                for line in tqdm(file):
                    line = json.loads(line)
                    if keep_or_not(line, channels=channels):
                        try:
                            file_out.write(json.dumps(process_record(line), ensure_ascii=False))
                            file_out.write("\n")
                        except Exception as e:
                            print(e)
                            print(line)
                            raise e


if __name__ == "__main__":
    main()
