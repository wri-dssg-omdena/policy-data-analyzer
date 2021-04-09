import os
import math
import random
import time
from typing import Iterable, Dict

import cupy as cp
import spacy
from sentence_transformers import SentencesDataset, SentenceTransformer, InputExample
from sentence_transformers.evaluation import LabelAccuracyEvaluator
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from torch import nn, Tensor
from torch.utils.data import DataLoader

from tasks.data_augmentation.src.zero_shot_classification.latent_embeddings_classifier import *
from tasks.data_loading.src.utils import *
from tasks.data_visualization.src.plotting import *
from tasks.fine_tuning_sbert.src.sentence_transformer import EarlyStoppingSentenceTransformer
from tasks.model_evaluation.src.model_evaluator import *

if spacy.prefer_gpu():
    print("Using the GPU")
else:
    print("Using the CPU")

#  May need to run python -m spacy download es_core_news_lg first!
es_nlp = spacy.load('es_core_news_lg')


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


def grid_search_fine_tune_sbert(train_params, train_sents, train_labels, test_sents, test_labels, label_names,
                                eval_classifier=None):
    """
    Find the optimal SBERT model by doing a hyperparameter search over random seeds, test percentage, and different types of SBERT models
    """
    output_path = train_params["output_path"]
    experiment = train_params["experiment"]
    all_test_perc = train_params["all_test_perc"]
    model_names = train_params["model_names"]
    max_num_epochs = train_params["max_num_epochs"]
    baseline = train_params['baseline']
    patience = train_params['patience']
    seeds = train_params['seeds']

    numeric_labels = labels2numeric(test_labels, label_names)

    if eval_classifier is None:
        train_params["eval_classifier"] = "SBERT"
    else:
        train_params["eval_classifier"] = eval_classifier.__class__.__name__

    print(f"Grid Search Fine tuning parameters:\n{json.dumps(train_params, indent=4)}")

    json_output_fname = output_path + f"/{experiment}_FineTuningResults.json"

#     # Output setup - we will update the json as the fine tuning process goes so every result is stored immediately
#     with open(json_output_fname, "w") as f:
#         json.dump({}, f)
    for seed in seeds:

        # =============== SETTING GLOBAL SEEDS ===============================
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
        # ====================================================================        
        
        for DO_seed in range[1, 2]:#TODO: Set the full range
            for test_perc in all_test_perc:
#                 with open(json_output_fname, "r") as fr:
#                     output = json.load(fr)

#                 output[f"test_perc={test_perc}"] = {}
                X_train, X_test, y_train, y_test = train_test_split(train_sents, train_labels, test_size=test_perc,
                                                                    stratify=train_labels, random_state=DO_seed)

                # Load data samples into batches
                train_batch_size = 16
                label2int = dict(zip(label_names, range(len(label_names))))
                train_samples = []
                for sent, label in zip(X_train, y_train):
                    label_id = label2int[label]
                    train_samples.append(InputExample(texts=[sent], label=label_id))

                # Configure the dev set evaluator - still need to test whether this works
                dev_samples = []
                for sent, label in zip(X_test, y_test):
                    label_id = label2int[label]
                    dev_samples.append(InputExample(texts=[sent], label=label_id))

                for model_name in model_names:
#                     # Setup
#                     output[f"test_perc={test_perc}"][f'model_name={model_name}'][f'seed={seed}'] = []
#                     output[f"test_perc={test_perc}"][f'model_name={model_name}'] = {}

                    # Train set config
                    model = EarlyStoppingSentenceTransformer(model_name)
                    train_dataset = SentencesDataset(train_samples, model=model)
                    train_dataloader = DataLoader(train_dataset, shuffle=True, batch_size=train_batch_size)



                    # Define the way the loss is computed
                    classifier = SoftmaxClassifier(model=model,
                                                   sentence_embedding_dimension=model.get_sentence_embedding_dimension(),
                                                   num_labels=len(label2int))

                    # Dev set config
                    dev_dataset = SentencesDataset(dev_samples, model=model)
                    dev_dataloader = DataLoader(dev_dataset, shuffle=True, batch_size=train_batch_size)
                    dev_evaluator = LabelAccuracyEvaluator(dataloader=dev_dataloader, softmax_model=classifier,
                                                           name='lae-dev')

                    warmup_steps = math.ceil(
                        len(train_dataset) * max_num_epochs / train_batch_size * 0.1)  # 10% of train data for warm-up

                    model_deets = f"{train_params['eval_classifier']}_model={model_name}_test-perc={test_perc}_n-epoch={max_num_epochs}_seed={seed}"

                    # Train the model
                    start = time.time()

                    model.fit(train_objectives=[(train_dataloader, classifier)],
                              evaluator=dev_evaluator,
                              epochs=max_num_epochs,  # We always tune on an extra epoch to see the performance gain
                              evaluation_steps=1000,
                              warmup_steps=warmup_steps,
                              output_path=output_path,
                              BASELINE=baseline,
                              PATIENCE=patience,
                              params={'model_name': model_name, 'test_perc': test_perc, 'seed': seed}
                              )

                    end = time.time()
                    hours, rem = divmod(end - start, 3600)
                    minutes, seconds = divmod(rem, 60)
                    print(f"WI : {seed} - DO : {DO_seed} - test_per: {test_perc} - model : {model_name}\n")
                    print("Time taken for fine-tuning:", "{:0>2}:{:0>2}:{:05.2f}".format(int(hours), int(minutes), seconds))

                    if eval_classifier is None:
                        evaluate_using_sbert(model, test_sents, test_labels, label_names,
                                             model_deets, model_name, max_num_epochs, numeric_labels, output,
                                             output_path, test_perc, json_output_fname, seed)
                    else:
                        evaluate_using_sklearn(eval_classifier, model, train_sents, train_labels, test_sents,
                                               test_labels, label_names, model_deets, model_name, max_num_epochs,
                                               output, test_perc, output_path, json_output_fname, seed)


def evaluate_using_sbert(model, test_sents, test_labels, label_names,
                         model_deets, model_name, num_epochs, numeric_labels, output,
                         output_path, test_perc, json_output_fname, seed):
    # Projection matrix Z low-dim projection
    print("Classifying sentences...")
    proj_matrix = cp.asnumpy(calc_proj_matrix(test_sents, 50, es_nlp, model, 0.01))
    test_embs = encode_all_sents(test_sents, model, proj_matrix)
    label_embs = encode_labels(label_names, model, proj_matrix)

    # i = 0
    # # ===========
    # viz_string = f"{output_path}/{model_deets}_exp_{i}"
    # cm_string = f"{output_path}/{model_deets}_exp_{i}"
    # # ===========

    # while os.path.exists(viz_string):
    #     i += 1
    #     viz_string = f"{output_path}/{model_deets}_exp_{i}"
    #     cm_string = f"{output_path}/{model_deets}_exp_{i}"

    visualize_embeddings_2D(np.vstack(test_embs), test_labels, tsne_perplexity=50,
                            store_name=f"{output_path}/{model_deets}")

    model_preds, model_scores = calc_all_cos_similarity(test_embs, label_embs, label_names)

    print("Evaluating predictions...")
    numeric_preds = labels2numeric(model_preds, label_names)
    evaluator = ModelEvaluator(label_names, y_true=numeric_labels, y_pred=numeric_preds)

    # with open(f"{results_save_path}/exp_num.txt") as f:
    #     exp = int(f.read())

    output[f"test_perc={test_perc}"][f'model_name={model_name}'][f'seed={seed}'].append(
        {"num_epochs": num_epochs,
         "avg_f1": evaluator.avg_f1.tolist()})

    # with open(f"{results_save_path}/exp_num.txt", "w") as f:
    #     f.write(str(exp+1))

    with open(json_output_fname, "w") as f:
        json.dump(output, f)
    evaluator.plot_confusion_matrix(color_map='Blues', exp_name=f"{output_path}/{model_deets}")
    print("Macro/Weighted Avg F1-score:", evaluator.avg_f1.tolist())


def evaluate_using_sklearn(clf, model, train_sents, train_labels, test_sents, test_labels,
                           label_names, model_deets, model_name, num_epochs, output,
                           test_perc, output_path, json_output_fname, seed):
    # Sentence encoding
    print("Classifying sentences...")
    train_embs = encode_all_sents(train_sents, model)
    test_embs = encode_all_sents(test_sents, model)

    # i = 0
    # # ===========
    # viz_string = f"{output_path}/{model_deets}_exp_{i}"
    # cm_string = f"{output_path}/{model_deets}_exp_{i}"
    # # ===========

    # while os.path.exists(viz_string):
    #     i += 1
    #     viz_string = f"{output_path}/{model_deets}_exp_{i}"
    #     cm_string = f"{output_path}/{model_deets}_exp_{i}"

    visualize_embeddings_2D(np.vstack(test_embs), test_labels, tsne_perplexity=50,
                            store_name=f"{output_path}/{model_deets}")

    # Classifier training
    clf.fit(np.vstack(train_embs), train_labels)

    # Classifier predictions
    clf_preds = list(clf.predict(np.vstack(test_embs)))

    print("Evaluating predictions...")
    print(classification_report(test_labels, clf_preds))
    numeric_preds = labels2numeric(clf_preds, label_names)
    numeric_test_labels = labels2numeric(test_labels, label_names)
    evaluator = ModelEvaluator(label_names, y_true=numeric_test_labels, y_pred=numeric_preds)

    # with open(f"{results_save_path}/exp_num.txt") as f:
    #     exp = int(f.read())

    output[f"test_perc={test_perc}"][f'model_name={model_name}'][f'seed={seed}'].append(
        {"num_epochs": num_epochs,
         "avg_f1": evaluator.avg_f1.tolist()})

    # with open(f"{results_save_path}/exp_num.txt", "w") as f:
    #     f.write(str(exp+1))

    with open(json_output_fname, "w") as f:
        json.dump(output, f)

    evaluator.plot_confusion_matrix(color_map='Blues', exp_name=f"{output_path}/{model_deets}")
    print("Macro/Weighted Avg F1-score:", evaluator.avg_f1.tolist())