"""
Custom LabelAccuracyEvaluator for custom traning loop based on: 
    - https://github.com/UKPLab/sentence-transformers/blob/master/sentence_transformers/evaluation/LabelAccuracyEvaluator.py
Added:
    - F1 score calculation
    - `call()` function now returns a dict instead of a float, to access more metrics
"""
from sentence_transformers.evaluation import SentenceEvaluator
import torch
from torch.utils.data import DataLoader
from torch import device
import logging
from tqdm import tqdm
import os
import csv
from sklearn.metrics import f1_score


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


class CustomLabelAccuracyEvaluator(SentenceEvaluator):
    """
    Evaluate a model based on its accuracy on a labeled dataset

    This requires a model with LossFunction.SOFTMAX

    The results are written in a CSV. If a CSV already exists, then values are appended.
    """

    def __init__(self, dataloader: DataLoader, name: str = "", softmax_model=None):
        """
        Constructs an evaluator for the given dataset

        :param dataloader:
            the data for the evaluation
        """
        self.dataloader = dataloader
        self.name = name
        self.softmax_model = softmax_model

        if name:
            name = "_" + name

        self.csv_file = "accuracy_evaluation" + name + "_results.csv"
        self.csv_headers = ["epoch", "steps", "accuracy"]

    def __call__(self, model, output_path: str = None, epoch: int = -1, steps: int = -1) -> dict:
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
        accuracy = correct / total

        logging.info("Accuracy: {:.4f} ({}/{})\n".format(accuracy, correct, total))

        if output_path is not None:
            csv_path = os.path.join(output_path, self.csv_file)
            if not os.path.isfile(csv_path):
                with open(csv_path, mode="w", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(self.csv_headers)
                    writer.writerow([epoch, steps, accuracy])
            else:
                with open(csv_path, mode="a", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow([epoch, steps, accuracy])

        score_dict = {"accuracy": accuracy,
                      "macro_f1": f1_score(all_labels, all_predictions, average='macro'),
                      "weighted_f1": f1_score(all_labels, all_predictions, average='weighted')}

        return score_dict
