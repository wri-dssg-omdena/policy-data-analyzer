import math
import wandb
import time
from pathlib import Path
import os
import random
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
from tasks.fine_tuning_sbert.src.sentence_transformer import EarlyStoppingSentenceTransformer
from tasks.fine_tuning_sbert.src.custom_evaluator import CustomLabelAccuracyEvaluator
from tasks.model_evaluation.src.model_evaluator import *

if spacy.prefer_gpu():
    print("Using the GPU")
else:
    print("Using the CPU")

#  May need to run python -m spacy download es_core_news_lg first!
es_nlp = spacy.load('es_core_news_lg')

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


def train(config=None):
    """
    Find the optimal SBERT model by doing a hyperparameter search over random seeds, dev percentage, and different types of SBERT models
    """

    # this will write to the same project every time
    wandb.init(config=config, magic=True)

    config = wandb.config

    print(
        f"Grid Search Fine tuning parameters:\n{config}")

    label2int = dict(zip(label_names, range(len(label_names))))

    model_deets = f"{config.eval_classifier}_model={config.model_name}_test-perc={config.dev_perc}_seed={config.seeds}"

    wandb.run.notes = model_deets

    X_train, X_dev, y_train, y_dev = train_test_split(train_sents, train_labels, test_size=config.dev_perc,
                                                      stratify=train_labels, random_state=100)

    # Load data samples into batches
    train_batch_size = 16
    train_samples = build_data_samples(X_train, label2int, y_train)
    dev_samples = build_data_samples(X_dev, label2int, y_dev)

    # Train set config
    model = EarlyStoppingSentenceTransformer(config.model_name)
    train_dataset = SentencesDataset(train_samples, model=model)
    train_dataloader = DataLoader(
        train_dataset, shuffle=True, batch_size=train_batch_size)

    # Dev set config
    dev_dataset = SentencesDataset(dev_samples, model=model)
    dev_dataloader = DataLoader(
        dev_dataset, shuffle=True, batch_size=train_batch_size)

    # Define the way the loss is computed
    classifier = SoftmaxClassifier(model=model,
                                   sentence_embedding_dimension=model.get_sentence_embedding_dimension(),
                                   num_labels=len(label2int))
    warmup_steps = math.ceil(
        len(train_dataset) * config.max_num_epochs / train_batch_size * 0.1)  # 10% of train data for warm-up

    set_seeds(config.seeds)

    # Train the model
    start = time.time()
    dev_evaluator = CustomLabelAccuracyEvaluator(dataloader=dev_dataloader, softmax_model=classifier,
                                                 name='lae-dev', label_names=label_names,
                                                 model_hyper_params={'model_name': config.model_name, 'dev_perc': config.dev_perc, 'seed': config.seeds})

    model.fit(train_objectives=[(train_dataloader, classifier)],
              evaluator=dev_evaluator,
              epochs=config.max_num_epochs,
              evaluation_steps=1000,
              warmup_steps=warmup_steps,
              output_path=config.output_path,
              model_deets=model_deets,
              baseline=config.baseline,
              patience=config.patience,
              )

    end = time.time()
    hours, rem = divmod(end - start, 3600)
    minutes, seconds = divmod(rem, 60)
    print("Time taken for fine-tuning:",
          "{:0>2}:{:0>2}:{:05.2f}".format(int(hours), int(minutes), seconds))


def grid_search_fine_tune_sbert(train_params, train_sents, train_labels, label_names,
                                eval_classifier=None):
    """
    Find the optimal SBERT model by doing a hyperparameter search over random seeds, dev percentage, and different types of SBERT models
    """
    output_path = train_params["output_path"]
    dev_perc = train_params["all_dev_perc"]
    model_name = train_params["model_names"]
    max_num_epochs = train_params["max_num_epochs"]
    baseline = train_params['baseline']
    patience = train_params['patience']
    seed = train_params['seeds']

    print(
        f"Grid Search Fine tuning parameters:\n{json.dumps(train_params, indent=4)}")

    label2int = dict(zip(label_names, range(len(label_names))))

    X_train, X_dev, y_train, y_dev = train_test_split(train_sents, train_labels, test_size=dev_perc,
                                                      stratify=train_labels, random_state=100)

    # Load data samples into batches
    train_batch_size = 16
    train_samples = build_data_samples(X_train, label2int, y_train)
    dev_samples = build_data_samples(X_dev, label2int, y_dev)

    # Train set config
    model = EarlyStoppingSentenceTransformer(model_name)
    train_dataset = SentencesDataset(train_samples, model=model)
    train_dataloader = DataLoader(
        train_dataset, shuffle=True, batch_size=train_batch_size)

    # Dev set config
    dev_dataset = SentencesDataset(dev_samples, model=model)
    dev_dataloader = DataLoader(
        dev_dataset, shuffle=True, batch_size=train_batch_size)

    # Define the way the loss is computed
    classifier = SoftmaxClassifier(model=model,
                                   sentence_embedding_dimension=model.get_sentence_embedding_dimension(),
                                   num_labels=len(label2int))
    warmup_steps = math.ceil(
        len(train_dataset) * max_num_epochs / train_batch_size * 0.1)  # 10% of train data for warm-up

    set_seeds(seed)
    model_deets = f"{train_params['eval_classifier']}_model={model_name}_test-perc={dev_perc}_seed={seed}"

    # Train the model
    start = time.time()
    dev_evaluator = CustomLabelAccuracyEvaluator(dataloader=dev_dataloader, softmax_model=classifier,
                                                 name='lae-dev', label_names=label_names,
                                                 model_hyper_params={'model_name': model_name, 'dev_perc': dev_perc, 'seed': seed})

    # this will write to the same project every time
    run = wandb.init(notes=model_deets, project='WRI', tags=['baseline', 'training'],
                     entity='ramanshsharma')

    model.fit(train_objectives=[(train_dataloader, classifier)],
              evaluator=dev_evaluator,
              epochs=max_num_epochs,
              evaluation_steps=1000,
              warmup_steps=warmup_steps,
              output_path=output_path,
              model_deets=model_deets,
              baseline=baseline,
              patience=patience,
              show_progress_bar=False
              )

    run.save()
    run_name = run.name

    torch.save(model, output_path+'/saved_model.pt')
    wandb.save(output_path+'/saved_model.pt')

    wandb.finish()

    end = time.time()
    hours, rem = divmod(end - start, 3600)
    minutes, seconds = divmod(rem, 60)
    print("Time taken for fine-tuning:",
          "{:0>2}:{:0>2}:{:05.2f}".format(int(hours), int(minutes), seconds))

    return run_name


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


def set_seeds(seed):
    os.environ['PYTHONHASHSEED'] = str(seed)
    # Torch RNG
    torch.manual_seed(seed)
    # torch.cuda.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    # Python RNG
    np.random.seed(seed)
    random.seed(seed)
    # CuDA Determinism
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.enabled = False


def evaluate_using_sbert(model, test_sents, test_labels, label_names,
                         model_deets, numeric_labels, output_path=None, testing=False):
    """
    Evaluate an S-BERT model on a previously unseen test set, visualizing the embeddings, confusion matrix,
    and returning. Evaluation method:
     - Calculate cosine similarity between label and sentence embeddings
     #A-latent-embedding-approach
     - Includes the projection matrix approach used in https://joeddav.github.io/blog/2020/05/29/ZSL.html

    """
    # Projection matrix Z low-dim projection
    print("Classifying sentences...")
    proj_matrix = cp.asnumpy(calc_proj_matrix(
        test_sents, 50, es_nlp, model, 0.01))
    test_embs = encode_all_sents(test_sents, model, proj_matrix)
    label_embs = encode_labels(label_names, model, proj_matrix)

    model_preds, model_scores = calc_all_cos_similarity(
        test_embs, label_embs, label_names)

    print("Evaluating predictions...")
    print(classification_report(test_labels, model_preds))
    numeric_preds = labels2numeric(model_preds, label_names)
    evaluator = ModelEvaluator(
        label_names, y_true=numeric_labels, y_pred=numeric_preds)

    if not testing:
        print("Visualizing...")
        out_path = f"{output_path}/{model_deets}" if output_path and model_deets else None
        visualize_embeddings_2D(np.vstack(test_embs), test_labels, tsne_perplexity=50,
                                output_path=out_path)
        evaluator.plot_confusion_matrix(
            color_map='Blues', output_path=out_path)
    print("Macro/Weighted Avg F1-score:", evaluator.avg_f1.tolist())

    return evaluator.avg_f1.tolist()


def evaluate_using_sklearn(clf, model, train_sents, train_labels, test_sents, test_labels,
                           label_names, model_deets=None, output_path=None, testing=False):
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

    if not testing:
        print("Visualizing...")
        out_path = f"{output_path}/{model_deets}" if output_path and model_deets else None
        visualize_embeddings_2D(np.vstack(test_embs), test_labels, tsne_perplexity=50,
                                output_path=out_path)
        evaluator.plot_confusion_matrix(color_map='Blues', output_path=out_path)
    print("Macro/Weighted Avg F1-score:", evaluator.avg_f1.tolist())

    return evaluator.avg_f1.tolist()
