from typing import Tuple

from nltk.stem import SnowballStemmer

from yadbil.data.processing.text.utils.language import detect_language
from yadbil.data.processing.text.utils.load import load_nltk_data


load_nltk_data()


class MultilingualStemmer:
    def __init__(self, languages: Tuple[str, ...]):
        self.languages = languages
        self.stemmers = {lang: SnowballStemmer(lang) for lang in languages}

    def stem(self, word: str) -> str:
        detected_lang = detect_language(word, self.languages)
        if detected_lang:
            return self.stemmers[detected_lang].stem(word)
        return word  # Return the original word if language not detected
