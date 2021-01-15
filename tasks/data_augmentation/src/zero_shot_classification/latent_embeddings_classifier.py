from collections import Counter
import numpy as np
import torch
from torch.nn import functional as F
from tqdm import tqdm


def top_k_words(k, document, spacy_model, include_labels=None):
    doc = spacy_model(document)

    # all tokens that arent stop words or punctuations and are longer than 3 letters
    words = [token.text.lower() for token in doc if not token.is_stop and not token.is_punct and len(token.text) > 3]

    # k most common tokens
    word_freq = Counter(words)
    common_words = word_freq.most_common(k)

    result = list(list(zip(*common_words))[0])

    if include_labels:
        result.extend(include_labels)

    return result


def top_k_word_embeddings(top_k_words, spacy_model):
    word_embeddings = []

    for word in top_k_words:
        doc = spacy_model(word)
        vector = doc.vector
        word_embeddings.append(vector.reshape(1, vector.shape[0]))

    return word_embeddings


def top_k_sbert_embeddings(top_k_words, sbert_model):
    sbert_embeddings = []

    for word in top_k_words:
        vector = sbert_model.encode([word], convert_to_numpy=True)
        sbert_embeddings.append(vector)

    return sbert_embeddings


def least_squares_with_reg(X, y, lamda=0.01):
    # Help from: https://stackoverflow.com/questions/27476933/numpy-linear-regression-with-regularization and https://www.kdnuggets.com/2016/11/linear-regression-least-squares-matrix-multiplication-concise-technical-overview.html
    # Multiple Linear Regression with OLS parameter estimation with L2 regularization term. lambda = 0 is equivalent to OLS estimation without regularization
    return np.linalg.inv(X.T.dot(X) + lamda * np.eye(X.shape[1])).dot(X.T).dot(y)


def calc_proj_matrix(sentences, k, spacy_model, sbert_model, lamda=0.01, include_labels=None):
    sents_as_str = ". ".join(sentences)
    top_words = top_k_words(k, sents_as_str, spacy_model, include_labels)
    word_emb = np.vstack(top_k_word_embeddings(top_words, spacy_model))
    print(word_emb)
    sent_emb = np.vstack(top_k_sbert_embeddings(top_words, sbert_model))
    print(sent_emb)
    proj_matrix = least_squares_with_reg(sent_emb, word_emb, lamda)

    return proj_matrix


def encode_sentence(sentence, model, Z):
    sentence_rep = torch.from_numpy(np.matmul(model.encode(sentence), Z))
    sentence_rep = sentence_rep.reshape((1, sentence_rep.shape[0]))
    return sentence_rep


def encode_labels(labels, model, Z):
    return torch.from_numpy(np.matmul(model.encode(labels), Z))


def classify_sentence(sentence, label_names, model, Z):
    sentence_rep = encode_sentence(sentence, model, Z)
    label_reps = encode_labels(label_names, model, Z)

    return calc_cos_similarity(sentence_rep, label_reps, label_names)


def calc_cos_similarity(sentence_rep, label_reps, label_names):
    similarities = F.cosine_similarity(sentence_rep, label_reps)
    closest = similarities.argsort(descending=True)

    top_index = closest[0]
    return label_names[top_index], similarities[top_index]


def classify_sentence_given_label_reps(sentence, label_names, label_reps, model, Z):
    sentence_rep = encode_sentence(sentence, model, Z)

    return calc_cos_similarity(sentence_rep, label_reps, label_names)


def calc_all_cos_similarity(all_sents_reps, label_reps, label_names):
    model_preds, model_scores = [], []
    for sent_rep in tqdm(all_sents_reps):
        pred, score = calc_cos_similarity(sent_rep, label_reps, label_names)
        model_preds.append(pred)
        model_scores.append(score)

    return model_preds, model_scores


def classify_all_sentences(all_sents, label_names, sbert_model, proj_matrix):
    model_preds, model_scores = [], []
    label_reps = encode_labels(label_names, sbert_model, proj_matrix)

    for sent in tqdm(all_sents):
        pred, score = classify_sentence_given_label_reps(sent, label_names, label_reps, sbert_model, proj_matrix)
        model_preds.append(pred)
        model_scores.append(score)

    return model_preds, model_scores


def encode_all_sents(all_sents, sbert_model, proj_matrix=None):
    if proj_matrix is None:
        stacked = np.vstack([sbert_model.encode(sent) for sent in tqdm(all_sents)])
    else:
        stacked = np.vstack([encode_sentence(sent, sbert_model, proj_matrix) for sent in tqdm(all_sents)])
    return [torch.from_numpy(element).reshape((1, element.shape[0])) for element in stacked]
