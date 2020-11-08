import unicodedata
from collections import defaultdict
import re
from bs4 import BeautifulSoup
from nltk import word_tokenize
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.utils.validation import check_is_fitted
from string import punctuation
from nltk.stem.snowball import SnowballStemmer


class CorpusPreprocess(BaseEstimator, TransformerMixin):
    def __init__(self, language='english', stop_words=None, lowercase=True, strip_accents=False,
                 strip_numbers=False, strip_punctuation=False, strip_urls=True, stemmer=None,
                 max_df=1.0, min_df=1):
        """Scikit-learn like Transformer for Corpus preprocessing.
        Preprocesses text by applying multiple tasks (e.g. lowecasing, stemming, etc).
        Fits the data for obtaining vocabulary_ (mapping of terms to document frequencies)
         and stop_words_ (terms that were ignored because of either 'max_df', 'min_df' or 'stop_words').

        Args:
            language (str, optional): language of input text. Passed to word tokenizer. Defaults to 'english'.
            stop_words (list, optional): list of stop words to be removed. Defaults to None.
            lowercase (bool, optional): lowercases text if True. Defaults to True.
            strip_accents (bool, optional): strips accents from text if True. Defaults to False.
            strip_numbers (bool, optional): strips numbers from text if True. Defaults to False.
            strip_punctuation (bool, optional): strips provided punctuation from text if not False.
             Defaults to False.
            strip_urls: removes URLs from text if True. Defaults to True
            stemmer (Stemmer instance, optional): applies the provided Stemmer's stem method to text.
             Defaults to None.
            max_df (float in range [0.0, 1.0] or int, optional): ignore terms with a document frequency higher 
             than the given threshold. If float, the parameter represents a proportion of documents, integer 
             absolute counts. Defaults to 1.0.
            min_df (float in range [0.0, 1.0] or int, optional): ignore terms with a document frequency lower 
             than the given threshold. If float, the parameter represents a proportion of documents, integer 
             absolute counts. Defaults to 1.

        Raises:
            ValueError: max_df and min_df are bounded to range [0.0, 1.0]
        """
        self.language = language
        self.stop_words = stop_words
        self.lowercase = lowercase
        self.strip_accents = strip_accents
        self.strip_numbers = strip_numbers
        self.strip_punctuation = strip_punctuation
        self.strip_urls = strip_urls
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
        if self.stop_words is None:
            self.stop_words_ = set()
        else:
            self.stop_words_ = set(self.stop_words)

        if self.max_df is not None:
            if isinstance(self.max_df, float):
                vocab_rel_df = {k: v / len(X) for k, v in vocab_df.items()}
                self.stop_words_.update(
                    {k for k, v in vocab_rel_df.items() if v > self.max_df})
            else:
                self.stop_words_.update(
                    {k for k, v in vocab_df.items() if v > self.max_df})

        if self.min_df is not None:
            if isinstance(self.min_df, float):
                vocab_rel_df = {k: v / len(X) for k, v in vocab_df.items()}
                self.stop_words_.update(
                    {k for k, v in vocab_rel_df.items() if v < self.min_df})
            else:
                self.stop_words_.update(
                    {k for k, v in vocab_df.items() if v < self.min_df})

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
        corpus = [[token for token in doc if token not in self.stop_words_]
                  for doc in corpus]

        # Split vs merged
        if not tokenize:
            corpus = [" ".join(doc) for doc in corpus]

        return corpus

    def _word_tokenizer(self, X):
        """Preprocesses and tokenizes each document by applying a
         preprocessing function.

        Args:
            X (iterable): documents to preprocess

        Returns:
            list: preprocessed and tokenized documents
        """

        X = map(remove_html_tags, X)
        if self.lowercase:
            X = map(str.lower, X)
        if self.strip_urls:
            X = map(remove_urls, X)
        if self.strip_accents:
            X = map(remove_accents, X)
        if self.strip_numbers:
            X = map(remove_numbers, X)
        if self.strip_punctuation:
            X = map(remove_punctuation, X)

        # Word tokenizer
        corpus = [word_tokenize(doc, language=self.language) for doc in X]

        if self.stemmer is not None:
            corpus = [[self.stemmer.stem(token)
                       for token in doc] for doc in corpus]

        return corpus


def remove_html_tags(text):
    return BeautifulSoup(text, features="lxml").get_text()


def remove_urls(text):
    # Remove URLs with http
    text_without_http = re.sub(r'http\S+', '', text)

    # Remove URLs with only www. start
    return re.sub(r'www\S+', '', text_without_http)


def remove_accents(text):
    return unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('ASCII')


def remove_numbers(text):
    return text.translate(str.maketrans('', '', "0123456789"))


def remove_punctuation(text):
    return text.translate(str.maketrans('', '', punctuation))