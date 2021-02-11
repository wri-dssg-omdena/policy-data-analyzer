import json
import argparse
from abc import ABCMeta, abstractmethod

import numpy as np
from gensim.corpora import Dictionary
from gensim.corpora.mmcorpus import MmCorpus
from gensim.summarization.bm25 import BM25

from src.data.text_preprocessor import TextPreprocessor

class SearchEngine(metaclass=ABCMeta):
    @abstractmethod
    def top_k_matches(self, query, k):
        """
        Calculates the top `k` most relevant documents in the engine's corpus
        relative to the query.

        Parameters
        ----------
        query : str
            Query to be searched for.
        k : int
            Number of documents to return.

        Returns
        -------
        top_k_matches : [str]
            Length k list of document ids.
        """

    @abstractmethod
    def load(id):
        """
        Loads the SearchEngine object with the given id.

        Parameters
        ----------
        id : str
            Unique identifier for the engine.
        Returns
        -------
        engine : SearchEngine
            SearchEngine object.
        """
class BM25Engine(SearchEngine):
    tokenizer_file = "data/processed/{id}/tokenizer"
    corpus_file = "data/processed/{id}/corpus"
    doc_idxs_file = "data/processed/{id}/doc_idxs.json"
    def __init__(self, tokenizer, corpus, idxs2id):
        """
        Parameters
        ----------
        tokenizer : gensim.corpora.Dictionary
            Word tokenizer.
        corpus : gensim.corpora.mmcorpus.MmCorpus
            Bag-of-words formatted corpus of documents.
        """
        self.preprocessor = TextPreprocessor()
        self.tokenizer = tokenizer
        self.corpus = corpus
        self.internal_engine = BM25(self.corpus)
        self.idxs2id = idxs2id
        print("BM25 engine loaded")
    
    def top_k_matches(self, query, k):
        clean = self.preprocessor.clean_sentence(query, alphabetic_only=True)
        word_list = self.preprocessor.tokenize_text(clean)
        bow_representation = self.tokenizer.doc2bow(word_list)
        scores = self.internal_engine.get_scores(bow_representation)
        top_k_idxs = np.argsort(scores)[::-1][:k]
        return [self.idxs2id[str(idx)] for idx in top_k_idxs]

    def load(id):
        tokenizer = Dictionary.load(BM25Engine.tokenizer_file.format(id=id))
        corpus = MmCorpus(BM25Engine.corpus_file.format(id=id))
        with open(BM25Engine.doc_idxs_file.format(id=id), "r") as f:
            idxs2id = json.load(f)
        return BM25Engine(tokenizer, corpus, idxs2id)

classes = {
    "bm25": BM25Engine
}

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-class", type=str)
    parser.add_argument("-id", type=str)
    parser.add_argument("-query", type=str)
    parser.add_argument("-k", type=int)
    args = vars(parser.parse_args())
    # Load engine and perform query
    engine = classes[args["class"]].load(args["id"])
    print(engine.top_k_matches(args["query"], args["k"]))