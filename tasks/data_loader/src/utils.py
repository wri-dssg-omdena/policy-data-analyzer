import json

def load_file(file_name):
    try:
        with open(file_name, "r") as f:
            return json.load(f)
    except Exception as e:
        print("Couldn't load file. Error: " + e)
        return None

def labeled_sentences_from_dataset(dataset):
    sentence_tags_pairs = []
                    
    for document in dataset.values():
        for section in document.values():
            for subsection in section.values():
                for sentence in subsection['sentences'].values():
                    sentence_tags_pairs.append((sentence['text'], sentence['labels'][0]))
                    
    return sentence_tags_pairs

def labeled_sentences_from_model_output(model_preds):
    sentence_tags_pairs = []
    for preds in model_preds:
        sentence_tags_pairs.append((preds["text"], preds["labels"][0]))
    return sentence_tags_pairs

def labels_from_dataset(dataset):
    labels = []
                    
    for document in dataset.values():
        for section in document.values():
            for subsection in section.values():
                for sentence in subsection['sentences'].values():
                    labels.append(sentence['labels'][0])
                    
    return labels

def labels_from_model_output(model_preds):
    return [preds["labels"][0] for preds in model_preds]