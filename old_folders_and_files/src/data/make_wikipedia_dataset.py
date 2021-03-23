import os
import re
import sys
import json

import wget
import codecs
import tarfile
from tqdm import tqdm

dataset_url = "https://www.cs.upc.edu/~nlp/wikicorpus/raw.es.tgz"
raw_dataset_dir = "data/raw/wikipedia/"
interim_dataset_dir = "data/interim/wikipedia/"
article_path = os.path.join(interim_dataset_dir, "{article_id}.txt")
titles_path = os.path.join(interim_dataset_dir, "titles.json")

def make_dataset():
    """
    Downloads the Wikipedia dataset and splits the Wikipedia articles in it into
    separate text files.
    """
    # Download dataset if needed
    if os.path.isdir(raw_dataset_dir):
        print("Dataset downloaded.")
    else:
        print("Downloading dataset.")
        os.makedirs(raw_dataset_dir, exist_ok=True)
        filename = wget.download(dataset_url, raw_dataset_dir)
        tarfile.open(filename).extractall(raw_dataset_dir)
        os.remove(filename)
    # Split the articles in each `.XML` into individual `.txt` files
    if os.path.isdir(interim_dataset_dir):
        print("Articles split into individual files.")
        return
    else:
        print("Splitting articles into individual files.")
    titles = {}
    os.makedirs(interim_dataset_dir, exist_ok=True)
    for raw_filename in tqdm(os.listdir(raw_dataset_dir)):
        raw_filename = os.path.join(raw_dataset_dir, raw_filename)
        with codecs.open(raw_filename, encoding="ISO-8859-1", mode="r") as f:
            file_content = f.read()
        # Parsed with regex because the XML files are not properly formatted
        articles = re.findall("<doc.*?</doc>", file_content, re.S)
        for article in articles:
            # Extract article title and id, and record title
            article_id = re.search("id=\".*?\"", article).group(0)
            article_id = article_id.replace("id=", "").replace("\"", "")
            article_title = re.search("title=\".*?\"", article).group(0)
            article_title = article_title.replace("title=", "").replace("\"", "")
            titles.update({article_id: article_title})
            # Write the article in it's own file
            with open(article_path.format(article_id=article_id), "w") as f:
                f.write(article)
    # Finally write the article titles file
    with open(titles_path, "w") as f:
        json.dump(titles, f, indent=2)

if __name__ == "__main__":
    make_dataset()