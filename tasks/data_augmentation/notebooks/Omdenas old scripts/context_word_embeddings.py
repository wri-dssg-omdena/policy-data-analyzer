import os
import shutil
import tarfile 
import wget

import torch
import numpy as np

from transformers import BertForMaskedLM, BertTokenizer
from scipy.spatial import distance

class ContextWordEmbeddings:
    '''
    Utility class to calculate the contextual word embedding distance
    between two texts, an approach to find semantically similar sentences in a document.
    Reference:
    - https://towardsdatascience.com/nlp-extract-contextualized-word-embeddings-from-bert-keras-tf-67ef29f60a7b
    - https://becominghuman.ai/extract-a-feature-vector-for-any-image-with-pytorch-9717561d1d4c
    '''
    model_dir = "models/beto/pytorch"
    def __init__(self):
        try:
            self._tokenizer = BertTokenizer.from_pretrained(
                self.model_dir, do_lower_case=False
            )
            self._model = BertForMaskedLM.from_pretrained(self.model_dir)
        except:
            self._download_model()
            self._tokenizer = BertTokenizer.from_pretrained(
                self.model_dir, do_lower_case=False
            )
            self._model = BertForMaskedLM.from_pretrained(self.model_dir)

    def _download_model(self):
        '''
        Downloads the BETO model's weights, vocabulary and configuration.
        '''
        weights_filename = wget.download('https://users.dcc.uchile.cl/~jperez/beto/cased_2M/pytorch_weights.tar.gz')
        vocab_filename = wget.download('https://users.dcc.uchile.cl/~jperez/beto/cased_2M/vocab.txt')
        config_filename = wget.download('https://users.dcc.uchile.cl/~jperez/beto/cased_2M/config.json')
        with tarfile.open(weights_filename) as f:
            weights_member = f.getmember("pytorch/pytorch_model.bin")
            weights_member.name = os.path.basename(weights_member.name)
            f.extract(weights_member, path=self.model_dir)
        os.remove(weights_filename)
        shutil.move(config_filename, os.path.join(self.model_dir, config_filename))
        shutil.move(vocab_filename, os.path.join(self.model_dir, vocab_filename))
    
    def _get_tokens_tensor(self, text):
        '''
        Given a text, convert it to BETO's required tokens
        '''
        tokens = self._tokenizer.tokenize(text)
        indexed_tokens = self._tokenizer.convert_tokens_to_ids(tokens)
        tokens_tensor = torch.tensor([indexed_tokens])
        return tokens_tensor
    
    def get_text_embedding(self, text):
        '''
        Using BETO's last four layers, get the contextual embedding of the text.
        1. Get the embedding of each token
        2. Avg pool the token tensor (1,N,768) to a tensor of (1,1,768)
        3. Sum the embeddings from the four layers.
        '''
        # Get the last 4 layers of the encoder.
        context_layers = [self._model._modules.get('bert').encoder.layer[-(4-i)] for i in range(4)]
        context_embeddings = []
        for layer in context_layers:
            tokens = self._get_tokens_tensor(text)
            # Initialize embeddings as zero
            context_embedding = torch.zeros(1, tokens.shape[1], 768)
            # Define hook to copy embedding after layer activation with example.
            def copy_data(m, i, o):
                context_embedding.copy_(o[0])
            # Register the hook after the forward operation in that layer
            h = layer.register_forward_hook(copy_data)
            # Run the model with the text.
            self._model(tokens)
            # Remove hook
            h.remove()
            context_embedding_numpy = np.copy(context_embedding.detach().numpy()[0][0])
            avg_context_embedding = np.mean(context_embedding.detach().numpy(), axis=1)
            # Add layer embedding to array to sum.
            context_embeddings.append(avg_context_embedding)
        return sum(context_embeddings).squeeze()

    def cosine_similarity(self, text1, text2):
        '''
        Given two texts, calculate the cosine similarity between their
        contextualized word embeddings.
        '''
        text1_embedding = self.get_text_embedding(text1)
        text2_embedding = self.get_text_embedding(text2)
        return np.dot(text1_embedding, text2_embedding)\
            / (np.linalg.norm(text1_embedding) * np.linalg.norm(text2_embedding))
