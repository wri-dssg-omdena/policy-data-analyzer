from sentence_transformers import SentenceTransformer
from scipy.spatial import distance

class SentenceEmbeddings:
    '''
    Utility class to calculate the sentence embedding distance
    between two texts, an approach to find semantically similar sentences in a document.
    Reference:
    - https://arxiv.org/abs/1908.10084
    '''
    def __init__(self, transformer_name='xlm-r-100langs-bert-base-nli-mean-tokens'):
        self._model = SentenceTransformer(transformer_name)

    def get_similarity(self, text1, text2):
        '''
        Given two texts, calculate the cosine similarity between their sentence embeddings.
        '''
        text1_embedding = self._model.encode(text1)
        text2_embedding = self._model.encode(text2)
        return 1 - distance.cosine(text1_embedding, text2_embedding)
