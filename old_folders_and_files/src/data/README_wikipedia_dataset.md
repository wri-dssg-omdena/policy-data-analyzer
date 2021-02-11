# Datasets

## Wikipedia Dataset
Made up of 259600 articles from the Spanish Wikipedia in 2006. The dataset was obtained from the [Wikicorpus v1.0](https://www.cs.upc.edu/~nlp/wikicorpus/) corpus, which was extracted by Universitat Politècnica de Catalunya. Download this dataset by executing:
```
python src/data/make_wikipedia_dataset.py
```
This will download the raw data into the [raw directory](../../data/raw/wikipedia) and create an individual `.txt` file per Wikipedia article inide the [interim directory](../../data/interim/wikipedia).