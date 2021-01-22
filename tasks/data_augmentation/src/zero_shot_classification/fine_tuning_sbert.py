import math
import time
from typing import Iterable, Dict

import cupy as cp
from sklearn.metrics import classification_report
import spacy
from sentence_transformers import SentencesDataset, SentenceTransformer, InputExample
from sentence_transformers.evaluation import LabelAccuracyEvaluator
from sklearn.model_selection import train_test_split
from torch import nn, Tensor
from torch.utils.data import DataLoader

from tasks.data_augmentation.src.zero_shot_classification.latent_embeddings_classifier import *
from tasks.data_loader.src.utils import *
from tasks.data_visualization.src.plotting import *
from tasks.evaluate_model.src.model_evaluator import *

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
    output_path = train_params["output_path"]
    experiment = train_params["experiment"]
    all_test_perc = train_params["all_test_perc"]
    model_names = train_params["model_names"]
    start_epochs = train_params["start_epochs"]
    max_num_epochs = train_params["max_num_epochs"]
    epochs_increment = train_params["epochs_increment"]
    numeric_labels = labels2numeric(test_labels, label_names)
    train_params["eval_classifier"] = eval_classifier.__class__.__name__
    print("Grid Search Fine tuning parameters:\n", json.dumps(train_params, indent=4))

    # Output setup - we will update the json as the fine tuning process goes so every result is stored immediately
    with open(f"{output_path}/{experiment}_FineTuningResults.json", "w") as fw:
        json.dump({}, fw)

    for test_perc in all_test_perc:
        with open(f"{output_path}/{experiment}_FineTuningResults.json", "r") as fr:
            output = json.load(fr)

        output[f"test_perc={test_perc}"] = {}
        X_train, X_test, y_train, y_test = train_test_split(train_sents, train_labels, test_size=test_perc,
                                                            stratify=train_labels, random_state=69420)

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
            # Setup
            output[f"test_perc={test_perc}"][model_name] = []

            # Train set config
            model = SentenceTransformer(model_name)
            train_dataset = SentencesDataset(train_samples, model=model)
            train_dataloader = DataLoader(train_dataset, shuffle=True, batch_size=train_batch_size)

            # Define the way the loss is computed
            classifier = SoftmaxClassifier(model=model,
                                           sentence_embedding_dimension=model.get_sentence_embedding_dimension(),
                                           num_labels=len(label2int))

            # Dev set config
            dev_dataset = SentencesDataset(dev_samples, model=model)
            dev_dataloader = DataLoader(dev_dataset, shuffle=True, batch_size=train_batch_size)
            dev_evaluator = LabelAccuracyEvaluator(dataloader=dev_dataloader, softmax_model=classifier, name='lae-dev')

            for num_epochs in range(start_epochs, max_num_epochs + 2, epochs_increment):
                warmup_steps = math.ceil(
                    len(train_dataset) * num_epochs / train_batch_size * 0.1)  # 10% of train data for warm-up
                model_deets = f"model={model_name}_test-perc={test_perc}_n-epoch={num_epochs}"

                # Train the model
                start = time.time()
                if num_epochs == start_epochs:
                    model.fit(train_objectives=[(train_dataloader, classifier)],
                              evaluator=dev_evaluator,
                              epochs=start_epochs,
                              evaluation_steps=1000,
                              warmup_steps=warmup_steps,
                              )
                else:
                    model.fit(train_objectives=[(train_dataloader, classifier)],
                              evaluator=dev_evaluator,
                              epochs=epochs_increment,  # We always tune on an extra epoch to see the performance gain
                              evaluation_steps=1000,
                              warmup_steps=warmup_steps,
                              )

                end = time.time()
                hours, rem = divmod(end - start, 3600)
                minutes, seconds = divmod(rem, 60)
                print("Time taken for fine-tuning:", "{:0>2}:{:0>2}:{:05.2f}".format(int(hours), int(minutes), seconds))

                if eval_classifier:
                    output = evaluate_using_sklearn(eval_classifier, model, train_sents, train_labels, test_sents,
                                                    test_labels,
                                                    label_names, experiment, model_deets, model_name, num_epochs,
                                                    output,
                                                    test_perc, output_path)
                else:
                    output = evaluate_using_sbert(model, test_sents, test_labels, label_names, experiment,
                                                  model_deets, model_name, num_epochs, numeric_labels, output,
                                                  output_path, test_perc)


def fine_tune_sbert(train_params, train_sents, train_labels, test_sents, test_labels, label_names,
                    eval_classifier=None):
    output_path = train_params["output_path"]
    experiment = train_params["experiment"]
    test_perc = train_params["test_perc"]
    model_name = train_params["model_names"]
    num_epochs = train_params["num_epochs"]
    numeric_labels = labels2numeric(test_labels, label_names)
    train_params["eval_classifier"] = eval_classifier.__class__.__name__
    print("Fine tuning parameters:\n", json.dumps(train_params, indent=4))

    output = {f"test_perc={test_perc}": {}}
    X_train, X_test, y_train, y_test = train_test_split(train_sents, train_labels, test_size=test_perc,
                                                        stratify=train_labels, random_state=69420)
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

    # Setup
    output[f"test_perc={test_perc}"][model_name] = []

    # Train set config
    model = SentenceTransformer(model_name)
    train_dataset = SentencesDataset(train_samples, model=model)
    train_dataloader = DataLoader(train_dataset, shuffle=True, batch_size=train_batch_size)

    # Define the way the loss is computed
    classifier = SoftmaxClassifier(model=model,
                                   sentence_embedding_dimension=model.get_sentence_embedding_dimension(),
                                   num_labels=len(label2int))

    # Dev set config
    dev_dataset = SentencesDataset(dev_samples, model=model)
    dev_dataloader = DataLoader(dev_dataset, shuffle=True, batch_size=train_batch_size)
    dev_evaluator = LabelAccuracyEvaluator(dataloader=dev_dataloader, softmax_model=classifier, name='lae-dev')
    warmup_steps = math.ceil(
        len(train_dataset) * num_epochs / train_batch_size * 0.1)  # 10% of train data for warm-up
    model_deets = f"model={model_name}_test-perc={test_perc}_n-epoch={num_epochs}"

    # Train the model
    start = time.time()
    model.fit(train_objectives=[(train_dataloader, classifier)],
              evaluator=dev_evaluator,
              epochs=num_epochs,
              evaluation_steps=1000,
              warmup_steps=warmup_steps,
              output_path=output_path
              )

    end = time.time()
    hours, rem = divmod(end - start, 3600)
    minutes, seconds = divmod(rem, 60)
    print("Time taken for fine-tuning:", "{:0>2}:{:0>2}:{:05.2f}".format(int(hours), int(minutes), seconds))

    if eval_classifier:
        output = evaluate_using_sklearn(eval_classifier, model, train_sents, train_labels, test_sents, test_labels,
                                        label_names, experiment, model_deets, model_name, num_epochs, output,
                                        test_perc, output_path)
    else:
        output = evaluate_using_sbert(model, test_sents, test_labels, label_names, experiment,
                                      model_deets, model_name, num_epochs, numeric_labels, output,
                                      output_path, test_perc)


def evaluate_using_sbert(model, test_sents, test_labels, label_names, experiment,
                         model_deets, model_name, num_epochs, numeric_labels, output,
                         output_path, test_perc):
    # Projection matrix Z low-dim projection
    print("Classifying sentences...")
    proj_matrix = cp.asnumpy(calc_proj_matrix(test_sents, 50, es_nlp, model, 0.01))
    test_embs = encode_all_sents(test_sents, model, proj_matrix)
    label_embs = encode_labels(label_names, model, proj_matrix)
    visualize_embeddings_2D(np.vstack(test_embs), test_labels, tsne_perplexity=50,
                            store_name=f"{output_path}/{model_deets}")
    model_preds, model_scores = calc_all_cos_similarity(test_embs, label_embs, label_names)

    print("Evaluating predictions...")
    numeric_preds = labels2numeric(model_preds, label_names)
    evaluator = ModelEvaluator(label_names, y_true=numeric_labels, y_pred=numeric_preds)
    output[f"test_perc={test_perc}"][model_name].append(
        {"num_epochs": num_epochs,
         "avg_f1": evaluator.avg_f1.tolist()})

    with open(f"{output_path}/{experiment}_FineTuningResults.json", "w") as fw:
        json.dump(output, fw)
    evaluator.plot_confusion_matrix(color_map='Blues', exp_name=f"{output_path}/{model_deets}")
    print("Macro/Weighted Avg F1-score:", evaluator.avg_f1.tolist())

    return output


def evaluate_using_sklearn(clf, model, train_sents, train_labels, test_sents, test_labels,
                           label_names, experiment, model_deets, model_name, num_epochs, output,
                           test_perc, output_path):
    # Sentence encoding
    print("Classifying sentences...")
    train_embs = encode_all_sents(train_sents, model)
    test_embs = encode_all_sents(test_sents, model)

    visualize_embeddings_2D(np.vstack(train_embs), train_labels, tsne_perplexity=50,
                            store_name=f"{output_path}/{model_deets}")

    # Classifier training
    clf.fit(np.vstack(train_embs), train_labels)

    # Classifier predictions
    clf_preds = [clf.predict([sent_emb])[0] for sent_emb in test_embs]

    print("Evaluating predictions...")
    print(classification_report(test_labels, clf_preds))
    numeric_preds = labels2numeric(clf_preds, label_names)
    numeric_test_labels = labels2numeric(test_labels, label_names)
    evaluator = ModelEvaluator(label_names, y_true=numeric_test_labels, y_pred=numeric_preds)

    output[f"test_perc={test_perc}"][model_name].append({"num_epochs": num_epochs, "avg_f1": evaluator.avg_f1.tolist()})
    with open(f"{output_path}/{experiment}_FineTuningResults.json", "w") as fw:
        json.dump(output, fw)

    evaluator.plot_confusion_matrix(color_map='Blues', exp_name=f"{output_path}/{clf.__class__.__name__}_{model_deets}")
    print("Macro/Weighted Avg F1-score:", evaluator.avg_f1.tolist())

    return output


def load_dataset(data_path, rater, set_of_labels_string):
    """
    Return the train data, train labels, test data, and test labels
    """
    dataset = []

    for dataset_type in ["train", "test"]:
        for file_type in ["sentences", "labels"]:
            filename = dataset_type + "_" + rater + "_" + set_of_labels_string + "_" + file_type + ".csv"
            file = data_path + "/" + filename
            try:
                data = pd.read_csv(file, index_col=False, header=None)
            except Exception as e:
                if "can't decode byte" in str(e):
                    data = pd.read_csv(file, index_col=False, header=None, encoding="ISO-8859-1")
                else:
                    raise Exception("Couldn't read file:", file)
            dataset.append(data[0].tolist())  # The data is always the entire first column

    return dataset[0], dataset[1], dataset[2], dataset[3]