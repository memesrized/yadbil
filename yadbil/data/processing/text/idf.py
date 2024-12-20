from collections import defaultdict

import numpy as np


# TODO: move somewhere
def calculate_idf(posts, words_key="stemmed_words", min_max_scale=False):
    """Calculates the inverse document frequency (IDF) for each stemmed word.

    Args:
        posts: A list of dictionaries, where each dictionary represents a post.
        words_key: dict key with target words
        min_max_scale (bool): If True, apply min-max scaling to the IDF values.

    Returns:
        A dictionary where keys are stemmed words and values are their IDF scores.
    """

    df = defaultdict(int)
    for post in posts:
        for word in set(post[words_key]):
            df[word] += 1

    num_docs = len(posts)
    idf = {word: np.log(num_docs / df) for word, df in df.items()}

    if min_max_scale:
        min_idf = min(idf.values())
        max_idf = max(idf.values())
        idf = {word: (idf[word] - min_idf) / (max_idf - min_idf) for word in idf}

    return idf
