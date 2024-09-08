from typing import Tuple

import nltk
from nltk.stem import SnowballStemmer

from yadbil.data.text.language import detect_language


nltk.download("punkt")
nltk.download("stopwords")


class MultilingualStemmer:
    def __init__(self, languages: Tuple[str, ...]):
        self.languages = languages
        self.stemmers = {lang: SnowballStemmer(lang) for lang in languages}

    def stem(self, word: str) -> str:
        detected_lang = detect_language(word, self.languages)
        if detected_lang:
            return self.stemmers[detected_lang].stem(word)
        return word  # Return the original word if language not detected
