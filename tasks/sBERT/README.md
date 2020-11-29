# Models

On the 29th of November 2020 the folder was created and the files dealing with sBERT from the Omdena repo were transferred here. These files were:
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
