import json
import re
from typing import Any, Dict, List, Tuple

import nltk

from yadbil.data.text.processing import TextPreprocessor


nltk.download("punkt")
nltk.download("stopwords")


# TODO: log instead of print
# TODO: text_processing_params as Pydantic model
class TelegramDataProcessor:
    def __init__(
        self,
        input_data: str,
        min_words_in_post: int = 5,
        text_processing_params: dict = None,
    ):
        """Initializes the TelegramDataProcessor with the path to the input data file.

        Args:
            input_data (str): The path to the input JSON data file.
        """
        self.input_data = input_data
        self.data = self._load_data()
        self.posts: List[Dict[str, Any]] = []
        self.posts_view: Dict[str, Dict[int, Dict[str, Any]]] = {}
        self._post_lengh = min_words_in_post

        text_processing_params = text_processing_params or {}
        self.text_processor = TextPreprocessor(**text_processing_params)

    def _load_data(self) -> Dict[str, Any]:
        """Loads JSON data from the input file.

        Returns:
            Dict[str, Any]: The loaded data.
        """
        try:
            with open(self.input_data, "r", encoding="utf-8") as file:
                data = json.load(file)
            print("All messages:", len(data["messages"]))
            return data
        except FileNotFoundError:
            raise FileNotFoundError(f"The file {self.input_data} was not found.")
        except json.JSONDecodeError:
            raise ValueError(f"The file {self.input_data} is not a valid JSON file.")

    # TODO: add len truncation
    def _keep_only_text_posts(self) -> None:
        """Filters out posts that do not contain text from the loaded data."""
        self.data["messages"] = [msg for msg in self.data["messages"] if "text" in msg and msg["text"]]
        print("Messages with text:", len(self.data["messages"]))

    @staticmethod
    def _extract_boundary_spaces(text: str) -> Tuple[str, str, str]:
        """Moves leading and trailing whitespace outside of formatting characters.

        Args:
            text (str): The text string to process.

        Returns:
            Tuple[str, str, str]: A tuple containing leading whitespace, processed text, and trailing whitespace.
        """
        match = re.search(r"^\s*(.*?)\s*$", text)
        if match:
            return text[: match.start(1)], match.group(1), text[match.end(1) :]
        return "", text, ""

    def _process_entity(self, entity: Dict[str, Any], parsed_message: Dict[str, Any]) -> None:
        """Processes a single entity from a Telegram message.

        Args:
            entity (Dict[str, Any]): The entity to process.
            parsed_message (Dict[str, Any]): The dictionary to store the parsed message data.
        """
        start_space, text_no_space, end_space = self._extract_boundary_spaces(entity["text"])
        parsed_message["text"] += entity["text"]

        if entity["type"] == "bold":
            parsed_message["md"] += f"{start_space}**{text_no_space}**{end_space}"
            parsed_message["text_no_links"] += entity["text"]
        elif entity["type"] == "italic":
            parsed_message["md"] += f"{start_space}*{text_no_space}*{end_space}"
            parsed_message["text_no_links"] += entity["text"]
        elif entity["type"] == "link" or entity["type"] == "text_link":
            url = entity.get("href", entity["text"])
            parsed_message["md"] += f"[{entity['text']}]({url})"
            parsed_message["links"].append(url)
            if entity["type"] == "text_link":
                parsed_message["links_mapping"][entity["text"]] = url
                parsed_message["text_no_links"] += entity["text"]
        else:
            parsed_message["md"] += entity["text"]
            parsed_message["text_no_links"] += entity["text"]

    def _parse_telegram_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Parses a single Telegram message dictionary.

        Args:
            message (Dict[str, Any]): A dictionary representing a single Telegram message.

        Returns:
            Dict[str, Any]: A dictionary containing the parsed message data.
        """
        parsed_message = {
            "id": message["id"],
            "from": message.get("from"),
            "from_id": message.get("from_id"),
            "text": "",
            "md": "",
            "text_no_links": "",
            "links": [],
            "links_mapping": {},
        }

        for entity in message.get("text_entities", []):
            self._process_entity(entity, parsed_message)

        parsed_message["md"] = re.sub(r"\s+([*_])\s+", r"\1", parsed_message["md"])

        return parsed_message

    def _generate_posts_view(self) -> Dict[str, Dict[int, Dict[str, Any]]]:
        """Generates a view of posts organized by channel ID.

        Returns:
            Dict[str, Dict[int, Dict[str, Any]]]: A dictionary where keys are channel IDs and values are dictionaries
                mapping post IDs to post data.
        """
        posts_view = {
            chn: {post["id"]: post for post in self.posts if post["from_id"] == chn}
            for chn in {post["from_id"] for post in self.posts}
        }
        return posts_view

    def process_posts(self) -> "TelegramDataProcessor":
        """Processes the Telegram messages, filtering and parsing them, and generates the posts view.

        Returns:
            TelegramDataProcessor: The instance of the processor.
        """
        self._keep_only_text_posts()
        self.posts = [self._parse_telegram_message(msg) for msg in self.data["messages"]]
        self.posts = [{**post, **self.text_processor.preprocess(post["text_no_links"])} for post in self.posts]
        self.posts = [x for x in self.posts if len(x["words"]) >= self._post_lengh]
        self.posts_view = self._generate_posts_view()
        print("Final length:", len(self.posts))
        return self
