import re
from collections import defaultdict

import nltk
import numpy as np
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
from stop_words import get_stop_words

from src.data_utils import is_ru, is_word

nltk.download("stopwords", quiet=True)
nltk.download("punkt", quiet=True)


# TODO: improve preprocessing
# TODO: lemmatization?
def preprocess_text(text, languages=["russian", "english"]):
    """Preprocesses text data for graph-based recommendation system.

    Args:
        text (str): The input text.
        languages (list): List of languages in the text. Defaults to ['russian', 'english'].

    Returns:
        list: A list of preprocessed words.
    """

    # Make lowercase
    text = text.lower()
    # Tokenize into words
    words = nltk.word_tokenize(text)  # Tokenize without specifying language
    # Filter for valid words
    words = [word for word in words if is_word(word)]
    # Remove stop words for all specified languages
    stop_words = set()
    for language in languages:
        stop_words.update(get_stop_words(language))
        stop_words.update(stopwords.words(language))
    words = [word for word in words if word not in stop_words]

    # TODO: refactor to make it applicable for all languages
    # Stemming (apply to each language separately)
    stemmer = {}
    for language in languages:
        stemmer[language] = SnowballStemmer(language)

    stemmed_dict = {word: stemmer[is_ru(word)].stem(word) for word in words}
    stemmed_to_orig_dict = {
        v: [kk for kk, vv in stemmed_dict.items() if vv == v]
        for v in stemmed_dict.values()
    }
    stemmed_words = {stemmer[is_ru(word)].stem(word) for word in words}

    return {
        "stemmed_words": list(stemmed_words),
        "words_to_stemmed": stemmed_dict,
        "stemmed_to_words": stemmed_to_orig_dict,
    }


def calculate_idf(posts, min_max_scale=False):
    """Calculates the inverse document frequency (IDF) for each stemmed word.

    Args:
        posts: A list of dictionaries, where each dictionary represents a post.
        min_max_scale (bool): If True, apply min-max scaling to the IDF values.

    Returns:
        A dictionary where keys are stemmed words and values are their IDF scores.
    """

    df = defaultdict(int)
    for post in posts:
        for word in set(post["stemmed_words"]):
            df[word] += 1

    num_docs = len(posts)
    idf = {word: np.log(num_docs / df) for word, df in df.items()}

    if min_max_scale:
        min_idf = min(idf.values())
        max_idf = max(idf.values())
        idf = {word: (idf[word] - min_idf) / (max_idf - min_idf) for word in idf}

    return idf
