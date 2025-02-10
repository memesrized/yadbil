from yadbil.search.bm25 import BM25
from yadbil.search.fasttext import FastTextWrapper
from yadbil.search.openai import OpenAISearch
from yadbil.search.pinecone import PineconeSearch
from yadbil.search.word2vec import Word2VecWrapper


SEARCH_EMB_STEPS = [FastTextWrapper, Word2VecWrapper, OpenAISearch, PineconeSearch]

SEARCH_STEPS = [BM25, *SEARCH_EMB_STEPS]
