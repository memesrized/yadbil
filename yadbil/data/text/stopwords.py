from typing import List, Tuple

import nltk
from nltk.corpus import stopwords
from stop_words import get_stop_words


nltk.download("punkt")
nltk.download("stopwords")


class MultilingualStopwordRemover:
    def __init__(self, languages: Tuple[str, ...]):
        self.stop_words = set()
        for language in languages:
            self.stop_words.update(get_stop_words(language))
            self.stop_words.update(stopwords.words(language))

    def remove(self, words: List[str]) -> List[str]:
        return [word for word in words if word not in self.stop_words]
