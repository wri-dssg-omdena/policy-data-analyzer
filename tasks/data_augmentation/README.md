# Zero-Shot Learning

In tasks/data_augmentation/notebooks/zero_shot_learning/ you will find the notebooks containing our experiments for both zero shot learning methods in here, as well as a notebook written by @DavidSilva98 to fine-tune SBERT.

Currently using the LatentEmbeddings_ZeroShotLearningExperiments.ipynb notebook to run experiments, including fine-tuning the model. Feel free to play around with it!
In tasks/data_augmentation/src/zero_shot_learning/ you will find all the supporting functions for the notebooks to work! They add quite a bit of abstraction so we can dive into experiments as soon as possible

New task/methods collection! In tasks/data_visualization/src/plotting.py you will find the methods necessary to plot the embeddings from SBERT. Included PCA, t-SNE and PHATE.

Bonus:

Refactored the model evaluator a bit, examples in the notebooks from zero shot learninfg
Added more functions for data loading in tasks/data_loader/src/utils.py, loading data has never been as easy :)
TO DO:

Change the import paths in the zero shot learning notebooks
Update the requirements file, as well as the Docker file if necessary to be able to run all of the code

# Semi-Automatic Labeling
In tasks/data_augmentation/notebooks/Semi-Automatic Labeling/ you will find the notebook containing the code to perform experiments for the semi-automatic labelling method. You need to adjust the paths for data input and output.

# sBERT Models

On the 29th of November 2020 the folder was created and the files dealing with sBERT from the Omdena repo were transferred here. These files were:
* context_word_embeddings.py
* evaluate_sbert.py
* this README.md file
* segment_highlighter.py

In this folder one will find:
- The scripts related to models as wells as those related to their evaluation.
- Instructions on where to find the data to run the models and the app. The app has its own README in src/visualizations/.

## Search Engines

### BM25
To execute queries using this engine you must
1. Download the tokenizer and term-document matrices extracted for the Wikipedia dataset [here](https://drive.google.com/drive/u/1/folders/1ymPs2E3WTZMpxpa3L8VExKUUWGgzIQFm). Place the contents of that folder inside `data/processed/wikipedia/`.

2. To perform that preprocessing in your own machine, follow steps _2_ and _3_. Obtain the Wikipedia articles dataset by running

```
python -m src.data.make_wikipedia_dataset
```

3. Extract tokens from that corpus and store it in bag-of-words representation by running
```
python -m src.features.build_corpus_tdm -docs_dir data/interim/wikipedia -dataset_name wikipedia
```

4. Perform queries by running (here the `query` is _"reforestacion"_ and we're retrieving the _10_ most relevant documents)
```
python -m src.models.search_engine -class bm25 -id wikipedia -query reforestacion -k 10
```

## Segment Highlighters

### BetoHighlighter
To execute queries using this engine you must
1. Obtain the Wikipedia articles dataset by running
```
python -m src.data.make_wikipedia_dataset
```

2. Perform queries by running
```
python -m src.models.segment_highlighter -class beto -id 2020190916 -doc_path data/interim/subsample/SembrandovidaReportefeb2019Febrero-1.txt -query compensación\ económica -precision 0.5
```

### BoW Highlighter

1. Perform queries (This will split the document in paragraphs and will check the similarity of the query with every paragraph) by running:
```
python -m src.models.segment_highlighter -class bow -doc_path "src\data\LibroLey_Bosque_NativoReglamentos.txt" -query "ley incentivo" -precision 0.4
```

### SBERTHighlighter
1. Download the preprocessed file `Lineamientos_de_Operaci_n_del_Programa_Sembrando_Vida.txt` from the project's [preprocessing](https://drive.google.com/drive/folders/1smqIPhvdWFGaB17Rf4SPLnGzmJtEH-0H) folder in Google Drive. Place it inside the `data/interim/subsample` folder.

2. Query relevant segments using
```
python -m src.models.segment_highlighter -class sbert -id 2020190916 -doc_path data/interim/subsample/Lineamientos_de_Operaci_n_del_Programa_Sembrando_Vida.txt -query incentivo\ económico -precision 0.3
```

## Data
