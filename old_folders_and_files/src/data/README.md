# PDF to txt/json conversion
In order to extract the text from a pdf file we use the script:

text_extraction.py located in: https://github.com/OmdenaAI/wrilatinamerica/blob/master/src/app/text_extraction.py

Run as:
python -m src.app.text_extraction <SOURCE_FOLDER_ID> <DESTINATION_FOLDER_ID>

This script takes the files from a Google Drive folder and uploads them to a Google Drive folder.

# Methods used in conversion
The methods used inside the text_extraction script are found in:
https://github.com/OmdenaAI/wrilatinamerica/blob/master/src/data/pdf_processing.py

# Text to paragraph conversion
This might be open for discussion:
## 1
The text can be converted to paragraphs via the split_into_paragraph function found in:
https://github.com/OmdenaAI/wrilatinamerica/blob/master/src/data/text_preprocessor.py

## 2
Many PDFs have a structure in which each sentence in the same paragraph is separated by "\n". Therefore,
initially splitting using "\n" might lead to wrong results. Another way, which is implemented in:
https://github.com/OmdenaAI/wrilatinamerica/blob/task-10-classification-llda/src/models/LDA/LDA_model_paragraphs_(with%20minimum%20amount%20of%20words).ipynb
where the splitting is done by defining paragraphs as a sequence of consecutive words of at least 60 words.

