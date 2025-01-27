from yadbil.search.bm25 import BM25
from yadbil.search.fasttext import FastTextWrapper
from yadbil.search.word2vec import Word2VecWrapper


SEARCH_EMB_STEPS = [FastTextWrapper, Word2VecWrapper]

SEARCH_STEPS = [BM25, *SEARCH_EMB_STEPS]
