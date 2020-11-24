import os
import argparse

import pandas as pd
from tqdm import tqdm

query = "beneficio económico o asistencia técnica"
result_path = "models/highlighter/sbert.csv"
min_paragraph_length = 60
substring_similarity_threshold = 60
blacklist = [
    "Presupuesto de Egresos de la Federación",
    "Sembrando Vida",
    "poseedores de terrenos forestales "
]


def read_model_output():
    pass


def labels_from_dataset():
    pass


def evaluate(y_true, y_pred, metric):
    pass


def evaluate_model(dataset_path, model_output_path, metric):
    ground_truth = labels_from_dataset(dataset_path)
    model_preds = read_model_output(model_output_path)
    results_df = evaluate(ground_truth, model_preds, metric)
    results_plots = plot_results(results_df)

    
def plot_results(eval_results):
    pass


def main():

    # Read command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-metric", type=str)
    parser.add_argument("-model_name", type=str)
    parser.add_argument("-model_output_path", type=str)
    parser.add_argument("-dataset_path", type=str)
    args = vars(parser.parse_args())

    evaluate_model(args["dataset_path"], args["model_output_path"])
    