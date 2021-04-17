import json
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from os import listdir
from os.path import isfile, join


def country_labeled_sentences(excel_map):
    result = {}
    sent_num = 0

    for country, dataframe in excel_map.items():

        new_sents_col = dataframe["Sentence"].dropna()
        new_labels_col = dataframe["Primary Instrument"].dropna()

        sentences = list(new_sents_col.apply(lambda x: x.replace("\n", "").strip()))
        label_col = new_labels_col.apply(lambda x: x.replace("(PES)", "").replace("(Bond)", "").strip())
        labels = [[string.strip() for string in label.split(", ")][0] for label in label_col]
        result[country] = {}

        for sent, label in zip(sentences, labels):
            if sent_num not in result[country]:
                result[country][sent_num] = {"text": sent, "labels": [label]}
            else:
                result[country][sent_num]["text"] = sent
                result[country][sent_num]["labels"] = [label]

            sent_num += 1

    return result

def filter_out_labeled_sents(sents, labels_to_filter):
    return [sent for sent in sents.values() if sent['labels'][0] not in labels_to_filter]

def get_counts_per_label(y_true, n_classes):
    """
    Return a map of {label: number of data points with that label} for the given list of labels
    Parameters:
        - y_true: (integer) a list of labels
        - n_classes: (integer) the number of classes
    """
    label_counts = [0] * n_classes
    for label in y_true:
        label_counts[label] += 1
    return label_counts

def labeled_sentences_from_dataset(dataset):
    sentence_tags_dict = {}

    for document in dataset.values():
        for section in document.values():
            sentence_tags_dict.update(section['sentences'])

    return sentence_tags_dict

def labeled_sentences_from_excel(excel_map):
    country2labeledsents = country_labeled_sentences(excel_map)
    labeled_sents = dict()
    for sents in country2labeledsents.values():
        labeled_sents.update(sents)

    return labeled_sents

def labels_from_dataset(dataset, label):
    labels = []

    for sentence in dataset.values():
        labels.append(sentence[label])

    return labels

def labels_from_model_output(model_preds):
    return [preds["labels"][0] for preds in model_preds.values()]

def labels2numeric(labels, label_names):
    label_map = dict(zip(label_names, range(len(label_names))))
    num_dataset_labels = [label_map[label] for label in labels]
    return num_dataset_labels

def list_files_from_dir(path):
    files = [f for f in listdir(path) if isfile(join(path, f))]
    return files

def load_dataset(data_path, experiment):
    """
    Return the train data, train labels, test data, and test labels
    """
    dataset = []
    for dataset_type in ["train", "test"]:
        for file_type in ["sentences", "labels"]:
            filename = experiment + "_" + dataset_type + "_" + file_type + ".csv"
            f = data_path + "/" + filename
            try:
                data = pd.read_csv(f, index_col=False, header=None)
            except Exception as e:
                if "can't decode byte" in str(e):
                    data = pd.read_csv(f, index_col=False, header=None, encoding="ISO-8859-1")
                else:
                    raise Exception("Couldn't read file:", f)
            dataset.append(data[0].tolist())  # The data is always the entire first column

    return dataset[0], dataset[1], dataset[2], dataset[3]

def load_json(file_name):
    with open(file_name, "r") as f:
        return json.load(f)

def merge_labels(all_labels, labels_to_merge):
    return [f"{labels_to_merge[0]} & {labels_to_merge[1]}" if label in labels_to_merge else label for label in all_labels]

def numeric_labels_from_dataset(dataset):
    """
    TEMPORARY: We're getting the set of unique labels from the data, but in reality we should standardize this and define it in a separate env file.
    """
    dataset_labels = labels_from_dataset(dataset)
    label_names = [label for label in set(dataset_labels)]
    label_names.sort()
    label_map = dict(zip(label_names, range(len(label_names))))
    num_dataset_labels = [label_map[label] for label in dataset_labels]
    return num_dataset_labels

def plot_data_distribution(data, label_names, normalize=True):
    weights = np.array(get_counts_per_label(data, len(label_names)))
    if normalize:
        weights = weights / sum(weights)

    plt.bar(label_names, weights)
    plt.xticks(label_names, rotation=90)
    plt.title("Data Distribution")
    plt.xlabel("Label")
    plt.ylabel("Percentage of label in data")
    plt.show()

    print("Label counts:")
    print(dict(zip(label_names, weights)))

def select_labels(dataset, labels_to_be_retrieved):
  new_dict = {}
  for key, value in dataset.items():
    if value['labels'] in labels_to_be_retrieved:
      new_dict[key] = value
  return new_dict
  
def sentences_from_dataset(dataset):
    sentences = []

    for sentence in dataset.values():
        sentences.append(sentence['text'])

    return sentences

def sentences_from_model_output(model_preds):
    return [preds["text"] for preds in model_preds.values()]

def sort_model_preds(dataset, model_preds):
    """
    Sorts the model predictions in the order that the input dataset is in.
    """
    # Dictionaries are insertion ordered since Python 3.6+,
    ordered_preds = {}

    for sentence_id in dataset:
        ordered_preds[sentence_id] = model_preds[sentence_id]

    return ordered_preds

def unique_labels(all_labels):
    return list(set(all_labels))