import math
import wandb
import time
from pathlib import Path
import os
import random
import subprocess
from typing import Iterable, Dict

import cupy as cp
import spacy
import torch
from sentence_transformers import SentencesDataset, SentenceTransformer, InputExample
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from torch import nn, Tensor
from torch.utils.data import DataLoader

from tasks.data_augmentation.src.zero_shot_classification.latent_embeddings_classifier import *
from tasks.data_loading.src.utils import *
from tasks.data_visualization.src.plotting import *
#from tasks.fine_tuning_sbert.src.sentence_transformer import EarlyStoppingSentenceTransformer
from tasks.fine_tuning_sbert.src.custom_evaluator import CustomLabelAccuracyEvaluator
from tasks.model_evaluation.src.model_evaluator import *

if spacy.prefer_gpu():
    print("Using the GPU")
else:
    print("Using the CPU")


train_sents = None
train_labels = None
label_names = None


class SoftmaxClassifier(nn.Module):
    """
    This loss adds a softmax classifier on top of the output of the transformer network.
    It takes a sentence embedding and learns a mapping between it and the corresponding category.
    :param model: SentenceTransformer model
    :param sentence_embedding_dimension: Dimension of your sentence embeddings
    :param num_labels: Number of different labels
    """

    def __init__(self,
                 model: SentenceTransformer,
                 sentence_embedding_dimension: int,
                 num_labels: int):
        super(SoftmaxClassifier, self).__init__()
        self.model = model
        self.num_labels = num_labels
        self.classifier = nn.Linear(sentence_embedding_dimension, num_labels)

    def forward(self, sentence_features: Iterable[Dict[str, Tensor]], labels: Tensor):
        # Get batch sentence embeddings
        features = self.model(sentence_features[0])['sentence_embedding']

        # Get batch loss
        output = self.classifier(features)
        loss_fct = nn.CrossEntropyLoss()

        if labels is not None:
            loss = loss_fct(output, labels.view(-1))
            return loss
        else:
            return features, output


def single_run_fine_tune_HSSC(train_params, train_sents, train_labels, label_names):
    """
    Find the optimal SBERT model by doing a hyperparameter search over random seeds, dev percentage, and different types of SBERT models
    """
    output_path = train_params["output_path"]
    dev_perc = train_params["all_dev_perc"]
    model_name = train_params["model_names"]
    max_num_epochs = train_params["max_num_epochs"]
    group_name = train_params["group_name"]

    print(f"Fine tuning parameters:\n{json.dumps(train_params, indent=4)}")
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

    # Load base model
    model = SentenceTransformer(model_name)

    # Splitting training and validation datasets
    label2int = dict(zip(label_names, range(len(label_names))))
    X_train, X_dev, y_train, y_dev = train_test_split(train_sents, train_labels, test_size=dev_perc,
                                                      stratify=train_labels, random_state=100)

    X_train, X_dev, y_train, y_dev = X_train.to(device), X_dev.to(device), y_train.to(device), y_dev.to(device)

    # Load data samples into batches
    train_batch_size = 16
    train_samples = build_data_samples(X_train, label2int, y_train)
    dev_samples = build_data_samples(X_dev, label2int, y_dev)

    # Train set config
    train_dataset = SentencesDataset(train_samples, model=model)
    train_dataloader = DataLoader(
        train_dataset.to(device), shuffle=True, batch_size=train_batch_size)

    # Dev set config
    dev_dataset = SentencesDataset(dev_samples, model=model)
    dev_dataloader = DataLoader(
        dev_dataset.to(device), shuffle=True, batch_size=train_batch_size)

    # Define the way the loss is computed
    classifier = SoftmaxClassifier(model=model,
                                   sentence_embedding_dimension=model.get_sentence_embedding_dimension(),
                                   num_labels=len(label2int))
    warmup_steps = math.ceil(
        len(train_dataset) * max_num_epochs / train_batch_size * 0.1)  # 10% of train data for warm-up

    # Train the model
    start = time.time()
    dev_evaluator = CustomLabelAccuracyEvaluator(dataloader=dev_dataloader, softmax_model=classifier,
                                                 name='lae-dev', label_names=label_names)

    # Init WandB
    wandb.init(project='HSSC', group=group_name, entity='jordi_planas')

    model.fit(train_objectives=[(train_dataloader, classifier)],
              evaluator=dev_evaluator,
              epochs=max_num_epochs,
              evaluation_steps=1000,
              warmup_steps=warmup_steps,
              output_path=output_path
              #   show_progress_bar=False
              )

    if output_path != None:
        torch.save(model, output_path+'/saved_model.pt')
        wandb.save(output_path+'/saved_model.pt')
        wandb.finish()

    else:
        wandb.finish()

    return model


def make_dataset_public(train_sents_, train_labels_, label_names_):
    global train_sents, train_labels, label_names
    train_sents = train_sents_
    train_labels = train_labels_
    label_names = label_names_


def build_data_samples(X_train, label2int, y_train):
    train_samples = []
    for sent, label in zip(X_train, y_train):
        label_id = label2int[label]
        train_samples.append(InputExample(texts=[sent], label=label_id))
    return train_samples


def evaluate_using_sklearn(clf, model, train_sents, train_labels, test_sents, test_labels, label_names):
    """
    Evaluate an S-BERT model on a previously unseen test set, visualizing the embeddings, confusion matrix,
    and returning. Evaluation method:
     - A sklearn classifier, such as a RandomForest or SVM
    """
    # Sentence encoding
    print("Classifying sentences...")
    train_embs = encode_all_sents(train_sents, model)
    test_embs = encode_all_sents(test_sents, model)

    # Classifier training
    clf.fit(np.vstack(train_embs), train_labels)

    # Classifier predictions
    clf_preds = list(clf.predict(np.vstack(test_embs)))

    print("Evaluating predictions...")
    print(classification_report(test_labels, clf_preds))
    numeric_preds = labels2numeric(clf_preds, label_names)
    numeric_test_labels = labels2numeric(test_labels, label_names)
    evaluator = ModelEvaluator(
        label_names, y_true=numeric_test_labels, y_pred=numeric_preds)

    evaluator.plot_confusion_matrix(color_map='Blues')
    print("Macro/Weighted Avg F1-score:", evaluator.avg_f1.tolist())

    return evaluator.avg_f1.tolist()
