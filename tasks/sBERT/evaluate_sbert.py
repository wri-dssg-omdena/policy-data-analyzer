import os
import argparse

import pandas as pd
from tqdm import tqdm
from textdistance import lcsstr

from src.models.segment_highlighter import classes
from src.data.text_preprocessor import TextPreprocessor
from src.models.sentence_embeddings import SentenceEmbeddings

query = "beneficio económico o asistencia técnica"
result_path = "models/highlighter/sbert.csv"
min_paragraph_length = 60
substring_similarity_threshold = 60
blacklist = [
    "Presupuesto de Egresos de la Federación",
    "Sembrando Vida",
    "poseedores de terrenos forestales "
]

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-dataset_dir", type=str)
    parser.add_argument("-tags_path", type=str)
    args = vars(parser.parse_args())
    # Instantiate model
    sbert = SentenceEmbeddings("xlm-r-100langs-bert-base-nli-stsb-mean-tokens")
    preprocessor = TextPreprocessor()
    # Iterate over tags file
    tags = pd.read_excel(args["tags_path"], sheet_name=None)
    scores = []
    labels = []
    incentive_paragraphs = []
    for country, country_tags in tags.items():
        print("Processing data available for '{}'".format(country))
        # Get the available documents' paths
        def get_txt_path(pdf_path):
            if isinstance(pdf_path, str):
                txt_path = os.path.basename(pdf_path).replace(".pdf", ".txt") 
                return os.path.join(args["dataset_dir"], country, "txt", txt_path)
            else:
                return None
        country_tags["txt_path"] = country_tags["Path"].apply(get_txt_path)
        for doc_path in tqdm(country_tags["txt_path"].unique()):
            # Collect sentence scores and classification
            if doc_path is None or not os.path.exists(doc_path):
                continue
            doc_tags = country_tags[country_tags["txt_path"] == doc_path]
            with open(doc_path, "r") as f: document = f.read()
            paragraphs = document.split("\n\n")
            for paragraph in paragraphs:
                # Skip overly-short paragraphs
                if len(paragraph) < min_paragraph_length:
                    continue
                # Score the paragraph's similarity to the query
                paragraph_score = sbert.get_similarity(paragraph, query)
                paragraph_label = 0
                incentive_paragraph = None
                # Determine if the paragraph has been tagged with an incentive
                for tagged_segment in doc_tags["Text"]:
                    if not isinstance(tagged_segment, str):
                        continue
                    substring = lcsstr._custom(paragraph, tagged_segment)
                    for term in blacklist:
                        substring = substring.replace(term, "")
                    if len(substring) > substring_similarity_threshold:
                        paragraph_label = 1
                        paragraph_score = sbert.get_similarity(tagged_segment, query)
                        incentive_paragraph = tagged_segment
                        break
                labels.append(paragraph_label)
                scores.append(paragraph_score)
                incentive_paragraphs.append(incentive_paragraph)
        pd.DataFrame({
            "score": scores, "label": labels, "incentive": incentive_paragraphs
        }).to_csv(result_path, index=False)