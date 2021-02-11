import os
import re
import sys
import json
import argparse
from time import time

import nltk
from tqdm import tqdm
from unidecode import unidecode
from gensim.corpora import Dictionary
from gensim.corpora.mmcorpus import MmCorpus

from src.data.text_preprocessor import TextPreprocessor
from src.models.search_engine import BM25Engine

# Output files
tokenizer_file = BM25Engine.tokenizer_file
corpus_file = BM25Engine.corpus_file
doc_idxs_file = BM25Engine.doc_idxs_file
# Transformations
try:
    stopwords = nltk.corpus.stopwords.words("spanish")
except:
    nltk.download(["stopwords", "punkt"])
    stopwords = nltk.corpus.stopwords.words("spanish")
stemmer = nltk.stem.SnowballStemmer("spanish")

def normalize_words(document):
    normalized = document.lower() # lowercase
    normalized = unidecode(normalized) # remove accents
    normalized = re.sub("[^a-zA-Z]+", " ", normalized) # alphabetic only
    normalized = nltk.word_tokenize(normalized)
    normalized = [stemmer.stem(word) for word in normalized]
    normalized = [word for word in normalized if word not in stopwords]
    return normalized

class IterativeCorpusBuilder():
    def __init__(self, document_paths, max_words):
        self.tokenizer = IterativeCorpusBuilder.extract_dictionary(
            document_paths, max_words=max_words
        )
        self.document_paths = iter(document_paths)
        self.preprocessor = TextPreprocessor()
        self.clock = time()
        self.iterations = 0
        self.inform_frequency = 1000
        self.max_words = 2 * 10 ** 6
    
    def __next__(self):
        with open(next(self.document_paths), "r") as f:
            document = f.read()
        document = self.preprocessor.clean_sentence(document, alphabetic_only=True)
        words = self.preprocessor.tokenize_text(document)
        bow_representation = self.tokenizer.doc2bow(words)
        # Inform progress as specified
        self.iterations += 1
        if self.iterations % self.inform_frequency == 0:
            print("{} iterations took {} seconds. {} done.".format(
                self.inform_frequency, time() - self.clock, self.iterations
            ))
            self.clock = time()
        return bow_representation

    def __iter__(self):
        print("Building corpus term-document matrices")
        return self

    def extract_dictionary(document_paths, max_words):
        """
        Extracts a gensim Dictionary object from a set of documents.

        Parameters
        ----------
        document_paths : [str]
            List of document paths that make up the corpus.
        
        Returns
        -------
        dictionary : gensim.corpora.Dictionary
            Extracted dictionary (or tokenizer).
        """
        print("Extracting dictionary from corpus")
        dictionary = Dictionary(prune_at=None)
        preprocessor = TextPreprocessor()
        for document_path in tqdm(document_paths):
            with open(document_path, "r") as f:
                document = f.read()
            document = preprocessor.clean_sentence(document, alphabetic_only=True)
            words = preprocessor.tokenize_text(document)
            dictionary.add_documents([words])
            if len(dictionary) > max_words:
                start = time()
                dictionary.filter_extremes(no_below=10, no_above=0.5, keep_n=int(max_words * 0.9))
                print("Dictionary filtered in {} seconds".format(time() - start))
        return dictionary

if __name__ == "__main__":
    """
    Builds a tokenizer from the corpus, and then stores the term-document matrix
    for the corpus.

    Parameters
    ----------
    docs_dir : str
        Directory containing `.txt` files to be used for tokenizer construction.
        A token frequency vector will be generated and stored for each of the
        files. Only `.txt` files will be taken into account.
    dataset_name : str
        A name for the directory where the processed corpus is to be placed.
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-docs_dir", type=str)
    parser.add_argument("-dataset_name", type=str)
    args = vars(parser.parse_args())
    documents_dir = args["docs_dir"]
    dataset_name = args["dataset_name"]
    document_paths = [
        os.path.join(documents_dir, d) for d in os.listdir(documents_dir)
        if d.endswith(".txt")
    ]
    # Write document index to id mapping
    doc_ids = [
        d.replace(".txt", "") for d in os.listdir(documents_dir)
        if d.endswith(".txt")
    ]
    doc_idxs = {i: doc_ids[i] for i in range(len(doc_ids))}
    os.makedirs(os.path.dirname(doc_idxs_file.format(id=dataset_name)))
    with open(doc_idxs_file.format(id=dataset_name), "w") as f:
        json.dump(doc_idxs, f, indent=2)
    # Create tokenizer and tokenize corpus in a single pass
    corpus_file = corpus_file.format(id=dataset_name)
    tokenizer_file = tokenizer_file.format(id=dataset_name)
    os.makedirs(os.path.dirname(corpus_file), exist_ok=True)
    corpus_builder = IterativeCorpusBuilder(document_paths, 2 * 10**6)
    MmCorpus.serialize(fname=corpus_file, corpus=corpus_builder)
    corpus_builder.tokenizer.save(tokenizer_file)