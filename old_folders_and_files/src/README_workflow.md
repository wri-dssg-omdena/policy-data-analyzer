#Instructions of usage

##Step 1: Conversion of PDFs to TXT/JSON

- In the folder src\app\ one can find the script text_extraction.py. This script must be run from the console 
and is documented with an example of use:

Input: .pdf files in folder with ID
Output: .txt or .csv files in folder with ID
Example:
python -m src.app.text_extraction <SOURCE_FOLDER_ID> <DESTINATION_FOLDER_ID>
The resulting files will be uploaded to the root of your Drive folder.

The ID is the last part of the Drive URL, as shown here:
https://drive.google.com/drive/-URL specifications-/1LFMNu7amHe0tSNpzT65P61I269X7ok7u

Where the ID is: 1LFMNu7amHe0tSNpzT65P61I269X7ok7u

Notice that the script right now is linked works with folders in Drive to take the input and write the output.
Since it works with Drive, the Google Drive API must be active.

If we were to do this change locally, we must change the script a little to account for this possibility.

- The methods used for the PDF transformation are found in src\data\pdf_processing.py. There, one can find:
	+ load_files(self, drive_client, source_id, temp_dir): Which allows us to choose what kind of files to load from Drive.
	+ pdf_to_txt(self, source_id, destination_id, temp_path): Which uses two different libraries to convert the pdf
	  to txt. Note that there is a temporary folder. So it needs to create a local copy of the txt before uploading.
	+ pdf_to_json_page_label(self, source_id, destination_id, temp_path): it's very similar to the previous method,
	  but divides the document by page and labels each.

##Step 2: Using the highlighting model.

- In the folder \src\models, you can find the following scripts:
	+ sentence_embeddings.py which is the SBERT model. Currently it is not being fine-tuned. Which gives room for 
	  improvement. The link to the original paper can be found there.
	+ segment_highlighter.py which is the class that implements the different highlighters: BoW (bag of words), BETO y
	  SBERT. The metric used so far to compare a query with a paragraph is the cosine similarity. Also, they are implemented to 
	  work with any lenght of text, so it is not required to use paragraphs. The input could be a sentence or a whole document.
	+ evaluate_sbert.py takes as input the ground truth labels and a preprocessed file where the SBERT tagged each paragraph as
	  relevant/non-relevant. Then, compares if the relevant paragraphs for SBERT were relevant for WRI. The output is a dataframe 
	  that contains: the paragraph, the cosine similarity score and the label.

- In the folder \src\visualizations, you can find all the app files:
	+ The README file in there contains the relevant information to run the application.
	+ The requirements.txt file is up-to-date and is located in the base folder. The app must be run from that location.
	+ The data that is loaded to the app must be located in the \scr\data\processed folder. This is currently not found there. Once 
	  corrected, this file will be updated.

