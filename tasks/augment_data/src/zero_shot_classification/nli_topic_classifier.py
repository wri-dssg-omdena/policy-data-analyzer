from transformers import pipeline
from tqdm import tqdm


def create_classfier(model_name):
    return pipeline('zero-shot-classification',
                    model=model_name)


def classify_sentence(sentence, labels,
                      hypothesis, classifier,
                      allow_multi_class=False, multi_class_thresh=0.5, all_probs=False):

    result = classifier(sentence, labels,
                        hypothesis_template=hypothesis,
                        multi_class=allow_multi_class)

    if all_probs:
        return list(zip(result["labels"], result["scores"]))

    if allow_multi_class:
        multi_labels = []
        multi_scores = []
        for i, score in enumerate(result["scores"]):
            if score > multi_class_thresh:
                multi_labels.append(result["labels"][i])
                multi_scores.append(score)

        return list(zip(multi_labels, multi_scores))

    return result["labels"][0], result["scores"][0]


def classify_sentences_topic(dataset_map, topics,
                             hypothesis_template, classifier):
    model_preds = []
    scores = []
    for sentence in tqdm(dataset_map.values()):
        model_pred, score = classify_sentence(sentence['text'], topics,
                                              hypothesis_template, classifier)
        model_preds.append(model_pred)
        scores.append(score)

    return model_preds, scores
