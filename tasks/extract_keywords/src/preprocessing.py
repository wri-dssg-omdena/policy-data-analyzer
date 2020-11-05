import os
import random
import unicodedata
from collections import defaultdict

from bs4 import BeautifulSoup
from nltk import word_tokenize
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.utils.validation import check_is_fitted


class CorpusPreprocess(BaseEstimator, TransformerMixin):
    def __init__(self, language='english', stop_words=None, lowercase=True, strip_accents=False,
                 strip_numbers=False, strip_punctuation=None, stemmer=None, max_df=1.0, min_df=1):
        """
        Scikit-learn like Transformer for Corpus preprocessing
        :param stop_words:
        :param lowercase:
        :param strip_accents:
        :param strip_numbers:
        :param strip_punctuation:
        :param stemmer: 
        :param max_df:
        :param min_df:

        :attr vocabulary_: dict
            A mapping of terms to document frequencies.
        :attr stop_words_ : set
            Terms that were ignored because they either:
              - occurred in too many documents (`max_df`)
              - occurred in too few documents (`min_df`)
              - also contains the same terms as stop_words
        """
        self.language = language
        self.stop_words = stop_words
        self.lowercase = lowercase
        self.strip_accents = strip_accents
        self.strip_numbers = strip_numbers
        self.strip_punctuation = strip_punctuation
        self.strip_numbers
        self.stemmer = stemmer
        self.max_df = max_df
        self.min_df = min_df
        if max_df < 0 or min_df < 0:
            raise ValueError("negative value for max_df or min_df")

    def fit(self, X, y=None):
        # Building vocabulary_ and stop_words_
        self.fit_transform(X)

        return self

    def fit_transform(self, X, y=None, tokenize=True):
        # Preprocess and tokenize corpus
        corpus = self._word_tokenizer(X)

        # Build vocabulary document frequencies
        vocab_df = defaultdict(int)
        for doc in corpus:
            for unique in set(doc):
                vocab_df[unique] += 1

        # Find stop_words_ based on max_df and min_df
        self.stop_words_ = set(self.stop_words)

        if self.max_df is not None:
            if isinstance(self.max_df, float):
                vocab_rel_df = {k: v / len(X) for k, v in vocab_df.items()}
                self.stop_words_.update({k for k, v in vocab_rel_df.items() if v > self.max_df})
            elif isinstance(self.max_df, int):
                self.stop_words_.update({k for k, v in vocab_df.items() if v > self.max_df})
            else:
                raise ValueError("max_df parameter should be int or float")

        if self.min_df is not None:
            if isinstance(self.min_df, float):
                vocab_rel_df = {k: v / len(X) for k, v in vocab_df.items()}
                self.stop_words_.update({k for k, v in vocab_rel_df.items() if v < self.min_df})
            elif isinstance(self.min_df, int):
                self.stop_words_.update({k for k, v in vocab_df.items() if v < self.min_df})
            else:
                raise ValueError("min_df parameter should be int or float")

        # Remove stop_words_ from vocabulary
        for k in self.stop_words_:
            vocab_df.pop(k, None)

        # Set vocabulary_
        self.vocabulary_ = vocab_df

        # Remove stop_words from corpus
        if self.stop_words is not None:
            corpus = [[token for token in doc if token not in self.stop_words]
                      for doc in corpus]
        
        # Split vs merged
        if not tokenize:
            corpus = [" ".join(doc) for doc in corpus]

        return corpus

    def transform(self, X, y=None, tokenize=True):
        # Check if fit has been called
        check_is_fitted(self)

        # Preprocess and tokenize corpus
        corpus = self._word_tokenizer(X)

        # Remove stop_words from corpus
        corpus = [[token for token in doc if token not in self.stop_words_] for doc in corpus]

        # Split vs merged
        if not tokenize:
            corpus = [" ".join(doc) for doc in corpus]

        return corpus

    def _word_tokenizer(self, X):
        """
        Preprocesses and tokenizes documents
        :param X: list of documents
        :return: list of preprocessed and tokenized documents
        """
        # Define function conditionally so we only need to evaluate the condition once instead at every document
        if self.strip_accents and self.lowercase and self.strip_numbers and self.strip_punctuation is not None:
            def doc_preprocessing(doc):
                # Removes HTML tags
                doc = BeautifulSoup(doc, features="lxml").get_text()
                # Lowercase
                doc = doc.lower()
                # Remove accentuation
                doc = unicodedata.normalize('NFKD', doc).encode('ASCII', 'ignore').decode('ASCII')
                # Remove numbers
                doc = doc.translate(str.maketrans('', '', "0123456789"))
                # Remove punctuation
                doc = doc.translate(str.maketrans('', '', self.strip_punctuation))
                return doc
        elif self.strip_accents and self.lowercase and self.strip_punctuation is not None:
            def doc_preprocessing(doc):
                # Removes HTML tags
                doc = BeautifulSoup(doc, features="lxml").get_text()
                # Lowercase
                doc = doc.lower()
                # Remove accentuation
                doc = unicodedata.normalize('NFKD', doc).encode('ASCII', 'ignore').decode('ASCII')
                # Remove punctuation
                doc = doc.translate(str.maketrans('', '', self.strip_punctuation))
                return doc
        if self.strip_accents and self.lowercase and self.strip_numbers:
            def doc_preprocessing(doc):
                # Removes HTML tags
                doc = BeautifulSoup(doc, features="lxml").get_text()
                # Lowercase
                doc = doc.lower()
                # Remove accentuation
                doc = unicodedata.normalize('NFKD', doc).encode('ASCII', 'ignore').decode('ASCII')
                # Remove numbers
                doc = doc.translate(str.maketrans('', '', "0123456789"))
                return doc
        if self.strip_accents and self.strip_numbers and self.strip_punctuation is not None:
            def doc_preprocessing(doc):
                # Removes HTML tags
                doc = BeautifulSoup(doc, features="lxml").get_text()
                # Remove accentuation
                doc = unicodedata.normalize('NFKD', doc).encode('ASCII', 'ignore').decode('ASCII')
                # Remove numbers
                doc = doc.translate(str.maketrans('', '', "0123456789"))
                # Remove punctuation
                doc = doc.translate(str.maketrans('', '', self.strip_punctuation))
                return doc
        if self.lowercase and self.strip_numbers and self.strip_punctuation is not None:
            def doc_preprocessing(doc):
                # Removes HTML tags
                doc = BeautifulSoup(doc, features="lxml").get_text()
                # Lowercase
                doc = doc.lower()
                # Remove numbers
                doc = doc.translate(str.maketrans('', '', "0123456789"))
                # Remove punctuation
                doc = doc.translate(str.maketrans('', '', self.strip_punctuation))
                return doc
        elif self.strip_accents and self.lowercase:
            def doc_preprocessing(doc):
                # Removes HTML tags
                doc = BeautifulSoup(doc, features="lxml").get_text()
                # Lowercase
                doc = doc.lower()
                # Remove accentuation
                doc = unicodedata.normalize('NFKD', doc).encode('ASCII', 'ignore').decode('ASCII')
                return doc
        elif self.strip_accents and self.strip_numbers:
            def doc_preprocessing(doc):
                # Removes HTML tags
                doc = BeautifulSoup(doc, features="lxml").get_text()
                # Remove accentuation
                doc = unicodedata.normalize('NFKD', doc).encode('ASCII', 'ignore').decode('ASCII')
                # Remove numbers
                doc = doc.translate(str.maketrans('', '', "0123456789"))
                return doc
        elif self.strip_accents and self.strip_punctuation is not None:
            def doc_preprocessing(doc):
                # Removes HTML tags
                doc = BeautifulSoup(doc, features="lxml").get_text()
                # Remove accentuation
                doc = unicodedata.normalize('NFKD', doc).encode('ASCII', 'ignore').decode('ASCII')
                # Remove punctuation
                doc = doc.translate(str.maketrans('', '', self.strip_punctuation))
                return doc
        elif self.lowercase and self.strip_numbers:
            def doc_preprocessing(doc):
                # Removes HTML tags
                doc = BeautifulSoup(doc, features="lxml").get_text()
                # Lowercase
                doc = doc.lower()
                # Remove numbers
                doc = doc.translate(str.maketrans('', '', "0123456789"))
                return doc
        elif self.lowercase and self.strip_punctuation is not None:
            def doc_preprocessing(doc):
                # Removes HTML tags
                doc = BeautifulSoup(doc, features="lxml").get_text()
                # Lowercase
                doc = doc.lower()
                # Remove punctuation
                doc = doc.translate(str.maketrans('', '', self.strip_punctuation))
                return doc
        elif self.strip_numbers and self.strip_punctuation is not None:
            def doc_preprocessing(doc):
                # Removes HTML tags
                doc = BeautifulSoup(doc, features="lxml").get_text()
                # Remove numbers
                doc = doc.translate(str.maketrans('', '', "0123456789"))
                # Remove punctuation
                doc = doc.translate(str.maketrans('', '', self.strip_punctuation))
                return doc
        elif self.strip_accents:
            def doc_preprocessing(doc):
                # Removes HTML tags
                doc = BeautifulSoup(doc, features="lxml").get_text()
                # Remove accentuation
                doc = unicodedata.normalize('NFKD', doc).encode('ASCII', 'ignore').decode('ASCII')
                return doc
        elif self.lowercase:
            def doc_preprocessing(doc):
                # Removes HTML tags
                doc = BeautifulSoup(doc, features="lxml").get_text()
                # Lowercase
                doc = doc.lower()
                return doc
        elif self.strip_numbers:
            def doc_preprocessing(doc):
                # Removes HTML tags
                doc = BeautifulSoup(doc, features="lxml").get_text()
                # Remove numbers
                doc = doc.translate(str.maketrans('', '', "0123456789"))
                return doc
        elif self.strip_punctuation is not None:
            def doc_preprocessing(doc):
                # Removes HTML tags
                doc = BeautifulSoup(doc, features="lxml").get_text()
                # Remove punctuation
                doc = doc.translate(str.maketrans('', '', self.strip_punctuation))
                return doc
        else:
            def doc_preprocessing(doc):
                # Removes HTML tags
                doc = BeautifulSoup(doc, features="lxml").get_text()
                return doc

        # Apply cleaning function over X
        corpus = map(doc_preprocessing, X)

        # Word tokenizer
        corpus = [word_tokenize(doc, language=self.language) for doc in corpus]

        if self.stemmer is not None:
            corpus = [[self.stemmer.stem(token) for token in doc] for doc in corpus]
            return corpus

        return corpus