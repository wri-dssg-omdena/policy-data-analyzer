"""
Custom LabelAccuracyEvaluator for custom traning loop based on:
    - https://github.com/UKPLab/sentence-transformers/blob/master/sentence_transformers/evaluation/LabelAccuracyEvaluator.py
Added:
    - F1 score calculation
    - Visualization of confusion matrix
    - `call()` function now returns a dict instead of a float, to access more metrics
"""
import itertools
from typing import Dict

import matplotlib.pyplot as plt
import numpy as np
import torch
from torch.utils.data import DataLoader
from torch import device
import logging
from tqdm import tqdm
import os
import csv
from sklearn.metrics import f1_score, confusion_matrix
from sentence_transformers.evaluation import SentenceEvaluator


def batch_to_device(batch, target_device: device):
    """
    send a pytorch batch to a device (CPU/GPU)
    """
    features = batch[0]
    for paired_sentence_idx in range(len(features)):
        for feature_name in features[paired_sentence_idx]:
            features[paired_sentence_idx][feature_name] = features[paired_sentence_idx][feature_name].to(target_device)

    labels = batch[1].to(target_device)
    return features, labels


def plot_confusion_matrix(cm, label_names, title='Confusion matrix',
                          color_map=None,
                          normalize=True,
                          output_path=None):
    """
    Adapted from: https://stackoverflow.com/questions/19233771/sklearn-plot-confusion-matrix-with-labels
    """
    if color_map is None:
        color_map = plt.get_cmap('Blues')

    plt.figure(figsize=(8, 6))
    plt.imshow(cm, interpolation='nearest', cmap=color_map)

    plt.title(title)
    plt.colorbar()
    plt.style.use('seaborn-white')

    if label_names:
        tick_marks = np.arange(len(label_names))
        plt.xticks(tick_marks, label_names, rotation=45)
        plt.yticks(tick_marks, label_names)

    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]

    thresh = cm.max() / 1.5 if normalize else cm.max() / 2
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        if normalize:
            plt.text(j, i, "{:0.2f}".format(cm[i, j]),
                     horizontalalignment="center",
                     color="white" if cm[i, j] > thresh else "black")
        else:
            plt.text(j, i, "{:,}".format(cm[i, j]),
                     horizontalalignment="center",
                     color="white" if cm[i, j] > thresh else "black")

    plt.tight_layout()
    plt.xlabel('Predicted label')
    plt.ylabel('True label')

    if output_path:
        fname = f"{output_path}_cm.png"
        plt.savefig(fname)
        print(f"Stored confusion matrix: {fname}")

    plt.show()


class CustomLabelAccuracyEvaluator(SentenceEvaluator):
    """
    Evaluate a model based on its accuracy on a labeled dataset

    This requires a model with LossFunction.SOFTMAX

    The results are written in a CSV. If a CSV already exists, then values are appended.
    """

    def __init__(self, dataloader: DataLoader, name: str = "", label_names: list = None, softmax_model=None,
                 model_hyper_params: Dict[str, str] = None):
        """
        Constructs an evaluator for the given dataset

        :param dataloader:
            the data for the evaluation
        """
        self.dataloader = dataloader
        self.name = name
        self.softmax_model = softmax_model
        self.label_names = label_names
        self.model_hyper_params = model_hyper_params

        if name:
            name = "_" + name

        self.csv_file = "accuracy_f1_evaluation" + name + "_results.csv"
        self.csv_headers = [param_name for param_name in self.model_hyper_params]
        self.csv_headers.extend(["epoch", "steps", "accuracy", "macro_f1", "weighted_f1"])

    def __call__(self, model, output_path: str = None, model_deets: str = None,
                 epoch: int = -1, steps: int = -1) -> dict:
        model.eval()
        total = 0
        correct = 0

        if epoch != -1:
            if steps == -1:
                out_txt = " after epoch {}:".format(epoch)
            else:
                out_txt = " in epoch {} after {} steps:".format(epoch, steps)
        else:
            out_txt = ":"

        logging.info("Evaluation on the " + self.name + " dataset" + out_txt)
        self.dataloader.collate_fn = model.smart_batching_collate

        all_predictions = []
        all_labels = []
        for step, batch in enumerate(tqdm(self.dataloader, desc="Evaluating")):
            features, label_ids = batch_to_device(batch, model.device)
            with torch.no_grad():
                _, prediction = self.softmax_model(features, labels=None)

            predictions_as_numbers = torch.argmax(prediction, dim=1)
            all_predictions.extend(predictions_as_numbers.tolist())
            all_labels.extend(label_ids.tolist())

            total += prediction.size(0)
            correct += predictions_as_numbers.eq(label_ids).sum().item()

        # Calculate evaluation metrics
        cm = confusion_matrix(all_labels, all_predictions)
        accuracy = correct / total
        macro_f1 = f1_score(all_labels, all_predictions, average='macro')
        weighted_f1 = f1_score(all_labels, all_predictions, average='weighted')
        score_dict = {"accuracy": accuracy,
                      "macro_f1": macro_f1,
                      "weighted_f1": weighted_f1}

        logging.info("Accuracy: {:.4f} ({}/{})\n".format(accuracy, correct, total))
        logging.info(f"Macro F1: {macro_f1}")
        logging.info(f"Weighted F1: {weighted_f1}")
        out_path = f"{output_path}/{model_deets}_n-epochs={epoch}" if model_deets and output_path else None
        plot_confusion_matrix(cm, self.label_names, output_path=out_path)

        if output_path is not None:
            self.store_results(score_dict, epoch, output_path, steps)

        return score_dict

    def store_results(self, results_dict, epoch, output_path, steps):
        accuracy = results_dict["accuracy"]
        macro_f1 = results_dict["macro_f1"]
        weighted_f1 = results_dict["weighted_f1"]

        csv_path = os.path.join(output_path, self.csv_file)
        if not os.path.isfile(csv_path):
            with open(csv_path, mode="w", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(self.csv_headers)
                row = [param_value for param_value in self.model_hyper_params]
                row.extend([epoch, steps, accuracy, macro_f1, weighted_f1])
                writer.writerow(row)
        else:
            with open(csv_path, mode="a", encoding="utf-8") as f:
                writer = csv.writer(f)
                row = [param_value for param_value in self.model_hyper_params]
                row.extend([epoch, steps, accuracy, macro_f1, weighted_f1])
                writer.writerow(row)
