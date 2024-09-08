from typing import Dict, Optional, Set, Tuple

import nltk


nltk.download("punkt")
nltk.download("stopwords")

# Define character sets for different languages
LANGUAGE_CHARS: Dict[str, Set[str]] = {
    "russian": set("".join(chr(i) for i in range(1072, 1104))),
    "english": set("abcdefghijklmnopqrstuvwxyz"),
    # Add more languages as needed
}


def detect_language(word: str, languages: Tuple[str, ...]) -> Optional[str]:
    """
    Detect the language of a word based on its characters.

    Args:
        word (str): The word to detect the language for.
        languages (Tuple[str, ...]): Tuple of languages to consider.

    Returns:
        Optional[str]: The detected language or None if no match is found.
    """
    word_chars = set(word.lower())
    for lang in languages:
        if word_chars.intersection(LANGUAGE_CHARS[lang]):
            return lang
    return None  # Return None if no language is detected
