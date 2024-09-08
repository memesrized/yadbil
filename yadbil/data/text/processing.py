from typing import Any, Dict, Tuple

import nltk

from yadbil.data.text.stemmer import MultilingualStemmer
from yadbil.data.text.stopwords import MultilingualStopwordRemover
from yadbil.data.utils import is_word


class TextPreprocessor:
    def __init__(
        self,
        languages: Tuple[str, ...] = ("russian", "english"),
        to_lower: bool = True,
        remove_stopwords: bool = True,
        do_stemming: bool = True,
        min_word_length: int = 2,
    ):
        self.languages = languages
        self.to_lower = to_lower
        self.remove_stopwords = remove_stopwords
        self.do_stemming = do_stemming
        self.min_word_length = min_word_length

        if self.remove_stopwords:
            self.stopword_remover = MultilingualStopwordRemover(self.languages)

        if self.do_stemming:
            self.stemmer = MultilingualStemmer(self.languages)

    def preprocess(self, text: str) -> Dict[str, Any]:
        """Preprocesses text data for graph-based recommendation system.

        Args:
            text (str): The input text.

        Returns:
            dict: A dictionary with preprocessed words, words-to-stemmed mapping, and stemmed-to-words mapping.
        """
        if self.to_lower:
            text = text.lower()

        words = nltk.word_tokenize(text)
        words = [word for word in words if is_word(word) and len(word) >= self.min_word_length]

        if self.remove_stopwords:
            words = self.stopword_remover.remove(words)

        if self.do_stemming:
            stemmed_dict = {word: self.stemmer.stem(word) for word in words}
        else:
            stemmed_dict = {word: word for word in words}

        stemmed_to_orig_dict = {
            v: [k for k, vv in stemmed_dict.items() if vv == v] for v in set(stemmed_dict.values())
        }
        stemmed_words = set(stemmed_dict.values())

        return {
            "stemmed_words": list(stemmed_words),
            "words": words,
            "words_to_stemmed": stemmed_dict,
            "stemmed_to_words": stemmed_to_orig_dict,
        }
