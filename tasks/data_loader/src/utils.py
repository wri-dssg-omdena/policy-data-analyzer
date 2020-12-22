import json


def load_file(file_name):
    with open(file_name, "r") as f:
        return json.load(f)


def labeled_sentences_from_dataset(dataset):
    sentence_tags_dict = {}

    for document in dataset.values():
        for section in document.values():
            sentence_tags_dict.update(section['sentences'])

    return sentence_tags_dict


def sort_model_preds(dataset, model_preds):
    """
    Sorts the model predictions in the order that the input dataset is in.
    """
    # Dictionaries are insertion ordered since Python 3.6+,
    ordered_preds = {}

    for sentence_id in dataset:
        ordered_preds[sentence_id] = model_preds[sentence_id]

    return ordered_preds


def labels_from_dataset(dataset):
    labels = []

    for document in dataset.values():
        for section in document.values():
            for sentence in section['sentences'].values():
                labels.append(sentence['labels'][0])

    return labels


def labels_from_model_output(model_preds):
    return [preds["labels"][0] for preds in model_preds.values()]
