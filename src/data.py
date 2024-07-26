import re
from typing import List, Dict

# TODO: add len truncation
def keep_only_text_posts(posts: List[Dict[str, str]]) -> List[Dict[str, str]]:
    return [x for x in posts["messages"] if x["text"]]


def extract_boundary_spaces(text: str) -> tuple[str, str, str]:
    """Moves leading and trailing whitespace outside of formatting characters.

    This function uses a regular expression to identify and move
    leading and trailing whitespace characters (spaces and newlines)
    from inside formatting characters to the outside.

    For example:
        " text\n\n" becomes (" ", "text", "\n\n")
        "text " becomes ("", "text", " ")
        " text" becomes (" ", "text", "")
        "text" remains ("", "text", "")

    Args:
        text: The text string to process.

    Returns:
        A tuple containing:
            - Leading whitespace characters.
            - The processed text with boundary whitespace moved outside.
            - Trailing whitespace characters.
    """
    match = re.search(r"^\s*(.*?)\s*$", text)
    return (
        (text[: match.start(1)], match.group(1), text[match.end(1) :])
        if match
        else ("", text, "")
    )


def parse_telegram_message(message: dict) -> dict:
    """Parses a single Telegram message dictionary.

    Args:
        message: A dictionary representing a single Telegram message.

    Returns:
        A dictionary containing the parsed message data.
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
        start_space, text_no_space, end_space = extract_boundary_spaces(entity["text"])

        parsed_message["text"] += entity["text"]  # No need to store 'text' separately

        if entity["type"] == "bold":
            parsed_message["md"] += f"{start_space}**{text_no_space}**{end_space}"
            parsed_message["text_no_links"] += entity["text"]
        elif entity["type"] == "italic":
            parsed_message["md"] += f"{start_space}*{text_no_space}*{end_space}"
            parsed_message["text_no_links"] += entity["text"]
        elif entity["type"] == "link" or entity["type"] == "text_link":
            url = entity.get("href", entity["text"])  # Use 'text' if 'href' is missing
            parsed_message["md"] += f"[{entity['text']}]({url})"
            parsed_message["links"].append(url)
            if entity["type"] == "text_link":
                parsed_message["links_mapping"][entity["text"]] = url
                parsed_message["text_no_links"] += entity["text"]
        else:
            parsed_message["md"] += entity["text"]
            parsed_message["text_no_links"] += entity["text"]

    parsed_message["md"] = re.sub(r"\s+([*_])\s+", r"\1", parsed_message["md"])

    return parsed_message
