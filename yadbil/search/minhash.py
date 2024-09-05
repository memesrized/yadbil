from typing import Any, Dict, Tuple

import nltk
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
from stop_words import get_stop_words

from yadbil.data.utils import is_ru, is_word


nltk.download("punkt")
nltk.download("stopwords")


def preprocess_text(
    text: str,
    languages: Tuple[str, str] = ("russian", "english"),
    stemming=True,
    unique=True,
) -> Dict[str, Any]:
    """Preprocesses text data for graph-based recommendation system.

    Args:
        text (str): The input text.
        languages (tuple): Tuple of languages in the text. Defaults to ('russian', 'english').
        stemming (bool): toggle stemming,
        unique (bool): whether to return list of unique words

    Returns:
        dict: A dictionary with preprocessed words, words-to-stemmed mapping, and stemmed-to-words mapping.
    """
    text = text.lower()
    words = nltk.word_tokenize(text)
    words = [word for word in words if is_word(word)]

    stop_words = set()
    for language in languages:
        stop_words.update(get_stop_words(language))
        stop_words.update(stopwords.words(language))
    words = [word for word in words if word not in stop_words]

    if stemming:
        stemmer = {language: SnowballStemmer(language) for language in languages}

        stemmed_dict = {word: stemmer[is_ru(word)].stem(word) for word in words}
        stemmed_to_orig_dict = {v: [kk for kk, vv in stemmed_dict.items() if vv == v] for v in stemmed_dict.values()}

        # TODO: why not stemmed dict from above why do we need to process it again
        stemmed_words = [stemmer[is_ru(word)].stem(word) for word in words]

        if unique:
            stemmed_words = list(set(unique))

        return {
            "stemmed_words": stemmed_words,
            "words_to_stemmed": stemmed_dict,
            "stemmed_to_words": stemmed_to_orig_dict,
        }
    else:
        if unique:
            words = list(set(words))
        return words
