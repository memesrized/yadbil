from pathlib import Path
from typing import List, Optional, Union

import bm25s


# TODO: reowrk completely
# just a draft, now it's stupid
class BM25:
    def __init__(self, data: Optional[List[List[str]]] = None):
        self.retriever = bm25s.BM25()
        if data:
            self.retriever.index(data)

    @classmethod
    def load(cls, path: Union[str, Path]):
        inst = cls()
        inst.retriever = bm25s.BM25.load(path, load_corpus=True)
        return inst

    def save(self, path):
        self.retriever.save(path)
