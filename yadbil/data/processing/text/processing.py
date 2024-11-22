import json
import re
from pathlib import Path
from typing import Any, Dict, Tuple, Union

import nltk
from tqdm.auto import tqdm

from yadbil.data.processing.text.utils.regexps import EMAIL_REGEX, URL_REGEX
from yadbil.data.processing.text.utils.stemmer import MultilingualStemmer
from yadbil.data.processing.text.utils.stopwords import MultilingualStopwordRemover


class TextProcessor:
    def __init__(
        self,
        input_path: Union[str, Path] = None,
        output_path: Union[str, Path] = None,
        split_into_words: bool = True,
        email_replacement_str: str = None,
        url_replacement_str: str = None,
        column_to_process: str = "text",
        languages: Tuple[str, ...] = ("russian", "english"),
        to_lower: bool = True,
        remove_stopwords: bool = True,
        do_stemming: bool = True,
        min_word_length: int = 2,
    ):
        self.input_path = input_path if isinstance(input_path, Path) else Path(input_path)
        self.output_path = output_path if isinstance(output_path, Path) else Path(output_path)
        self.column_to_process = column_to_process
        self.languages = languages
        self.to_lower = to_lower
        self.remove_stopwords = remove_stopwords
        self.do_stemming = do_stemming
        self.min_word_length = min_word_length

        self.split_into_words = split_into_words

        self.email_replacement_str = email_replacement_str
        if self.email_replacement_str is not None:
            self.email_regex = re.compile(EMAIL_REGEX)

        self.url_replacement_str = url_replacement_str
        if self.url_replacement_str is not None:
            self.url_regex = re.compile(URL_REGEX)

        if self.remove_stopwords:
            self.stopword_remover = MultilingualStopwordRemover(self.languages)

        if self.do_stemming:
            self.stemmer = MultilingualStemmer(self.languages)

    def sub_emails(self, text: str) -> str:
        """Substitute emails with a placeholder"""
        return self.email_regex(self.email_replacement_str, text)

    def sub_urls(self, text: str) -> str:
        """Substitute URLs with a placeholder"""
        return self.url_regex(self.url_replacement_str, text)

    def is_word(self, word: str) -> bool:
        return any(char.isalpha() for char in word)

    def process_text(self, text: str) -> Dict[str, Any]:
        """Processes text data for graph-based recommendation system.

        Args:
            text (str): The input text.

        Returns:
            dict: A dictionary with preprocessed words, words-to-stemmed mapping, and stemmed-to-words mapping.
        """
        if self.email_replacement_str is not None:
            text = self.sub_emails(text)
        if self.url_replacement_str is not None:
            text = self.sub_urls(text)
        if self.to_lower:
            text = text.lower()

        if not self.split_into_words:
            return {"text": text}

        words = nltk.word_tokenize(text)
        words = [word for word in words if self.is_word(word) and len(word) >= self.min_word_length]

        if self.remove_stopwords:
            words = self.stopword_remover.remove(words)

        result = {
            "words": words,
        }

        # TODO: do we need to ensure the same order of stemmed words?
        # well, it should be with dict in latest python versions, but still
        # idk about .values() method
        if self.do_stemming:
            stemmed_dict = {word: self.stemmer.stem(word) for word in words}
            stemmed_to_orig_dict = {
                v: [k for k, vv in stemmed_dict.items() if vv == v] for v in set(stemmed_dict.values())
            }

            result["stemmed_words"] = list(stemmed_dict.values())
            result["words_to_stemmed"] = stemmed_dict
            result["stemmed_to_words"] = stemmed_to_orig_dict

        return result

    # TODO: implement return of processed data if no output path is provided
    def run(self, data=None):
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

        if data is None:
            if self.input_path is None:
                raise ValueError("No input data provided.")

        with open(self.input_path) as in_file:
            with open(self.output_path, "w") as out_file:
                for line in tqdm(in_file):
                    item = json.loads(line)
                    item["processed_text"] = self.process_text(item[self.column_to_process])
                    out_file.write(json.dumps(item, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    from yadbil.pipeline.config import PipelineConfig

    config = PipelineConfig()

    processor = TextProcessor(config["TextProcessor"])
    processor.run()
