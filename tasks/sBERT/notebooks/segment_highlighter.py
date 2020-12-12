import re
import json
import argparse
from abc import ABCMeta, abstractmethod

import numpy as np
from sklearn.feature_extraction.text import CountVectorizer

from tasks.sBERT.context_word_embeddings import ContextWordEmbeddings
from tasks.sBERT.sentence_embeddings import SentenceEmbeddings
from tasks.sBERT.text_preprocessor import TextPreprocessor

class SegmentHighlighter(metaclass=ABCMeta):
    @abstractmethod
    def highlight(self, document, query):
        """
        Finds the parts of the document which are related to the query.

        Parameters
        ----------
        document : str
            The document to be searched over (or highlighted).
        query : str
            Query to be searched for.

        Returns
        -------
        highlights : [str]
            A list of segments matching the query in the document.
        scores : [float]
            A list with the similarity scores of each of the highlights with
            respect to the query. Must be the same length as `highlights`.
        """
    
    @abstractmethod
    def load(id):
        """
        Loads the SegmentHighlighter object with the given id.

        Parameters
        ----------
        id : str
            Unique identifier for the engine.
        Returns
        -------
        highlighter : SegmentHighlighter
            SegmentHighlighter object.
        """

class BetoHighlighter(SegmentHighlighter):
    def __init__(self):
        self.language_model = ContextWordEmbeddings()
        
    def highlight(self, document, query, precision):
        document = re.sub("[^a-zA-Z\n\.áéíóúÁÉÍÓÚ]+", " ", document)
        highlights = []
        scores = []
        for paragraph in document.split("\n\n"):
            paragraph = re.sub("\n", " ", paragraph)
            paragraph = re.sub(" +", " ", paragraph)
            paragraph = paragraph.strip()
            if len(paragraph) < 5:
                continue
            score = self.language_model.cosine_similarity(paragraph, query)
            if score > precision:
                highlights.append(paragraph)
                scores.append(score)
        sorted_idxs = np.argsort(scores)[::-1]
        highlights = [highlights[idx] for idx in sorted_idxs]
        scores = [scores[idx] for idx in sorted_idxs]
        return highlights, scores

    def load(id):
        return BetoHighlighter()

class SBERTHighlighter(SegmentHighlighter):
    def __init__(self):
        self._model = SentenceEmbeddings("distiluse-base-multilingual-cased")
        
    def highlight(self, document, query, precision):
        
        '''document must be the json document to be able to extract page'''
        highlights = []
        scores = []
        pages = []
        for page_num, text in document.items():
            page_num = page_num.split("_")[1]
            for sentence in text.split("\n\n"):
                sentence = re.sub("\n", " ", sentence)
                sentence = re.sub(" +", " ", sentence)
                sentence = sentence.strip()
                if len(sentence) < 60:
                    continue
                score = self._model.get_similarity(sentence, query)
                if score > precision:
                    highlights.append(sentence)
                    scores.append(score)
                    pages.append(page_num)
        sorted_idxs = np.argsort(scores)[::-1]
        highlights = [highlights[idx] for idx in sorted_idxs]
        scores = [scores[idx] for idx in sorted_idxs]
        pages = [pages[idx] for idx in sorted_idxs]
        return highlights, scores, pages

    def load(id):
        return SBERTHighlighter()

class BoWHighlighter(SegmentHighlighter):
    def __init__(self):        
        self.preprocessor = TextPreprocessor()
        self.counter = CountVectorizer()
        
    def highlight(self, document, query, precision):
        clean_query = self.preprocessor.clean_sentence(query) #, alphabetic_only=True
        word_list = self.preprocessor.tokenize_text(clean_query)
        #Convert query after tokenization as a string
        query_mod = ' '.join(word_list)
        document = re.sub(" +", " ", document)
        document = re.sub("\n\s+", " \n \n ", document)
        document = re.sub("\n+", "\n", document)
        # document = re.sub("\n*", "\n\n ", document)
        document = document.strip()
        highlights = []
        scores = []
        for paragraph in document.split(" \n \n "):
            if len(paragraph) == 0:
                continue
            clean_paragraph = self.preprocessor.clean_sentence(paragraph) #, alphabetic_only=True
            corpus = self.preprocessor.tokenize_text(clean_paragraph)
            paragraph_mod = ' '.join(corpus)
            vectorizer = self.counter.fit([query_mod, paragraph_mod])
            vectors = [vec for vec in vectorizer.transform([query_mod, paragraph_mod]).toarray()]
            norm_vec_query = np.linalg.norm(vectors[0])
            norm_vec_paragraph = np.linalg.norm(vectors[1])
            if norm_vec_paragraph == 0: continue
            cosine_similarity = np.dot(vectors[0], vectors[1]) / (norm_vec_query * norm_vec_paragraph)
            if cosine_similarity > precision:
                print("The cosine similary is: ",cosine_similarity, paragraph, "\n \n")
                highlights.append(paragraph)
                scores.append(cosine_similarity)
        return highlights, scores

    def load(id):
        return BoWHighlighter()   

classes = {
    "beto": BetoHighlighter,
    "bow": BoWHighlighter,
    "sbert": SBERTHighlighter
}

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-class", type=str)
    parser.add_argument("-id", type=str)
    parser.add_argument("-doc_path", type=str)
    parser.add_argument("-query", type=str)
    parser.add_argument("-precision", type=float)
    args = vars(parser.parse_args())
    # Load engine and perform query
    highlighter = classes[args["class"]].load(args["id"])
    with open(args["doc_path"], "r", encoding="utf8") as f:
        document = f.read()
    from time import time
    start = time()
    highlights, scores = highlighter.highlight(
        document, args["query"], args["precision"]
    )
    print([pair for pair in zip(highlights, scores)])
    print("Processing time: {} minutes".format((time() - start) / 60))
