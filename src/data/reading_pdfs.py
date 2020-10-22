import os
import sys
from collections import defaultdict
from zipfile import ZipFile
from pikepdf import Pdf
from PyPDF2 import PdfFileReader
from io import BytesIO
import json

# TODO: apply preprocessing to text, 
# solve reading problem with "Sembrando Vida Operations_Mexico.pdf", 
# solve data problems with several files (e.g. "Sembrando Vida_Mexico", "Sembrando Vida Report", ...)


INTER_PATH = os.path.join("data", "interim")
DOCS_PATH = os.path.join("data", "raw", "onedrive_docs.zip")


def text_cleaning(text):
    # Remove \n
    text = text.translate(str.maketrans('', '', '\n'))
    return text


def file_recovery(filename, zipfile):
    with Pdf.open(BytesIO(zipfile.read(filename))) as pdf_file:  # attempting to recovery file
        path_to_file = os.path.join(INTER_PATH, os.path.basename(filename))
        pdf_file.save(path_to_file)
        pdfReader = PdfFileReader(path_to_file)
        os.remove(path_to_file)
    return pdfReader

def text_reader():
    # Useful link: https://stackoverflow.com/questions/55993860/getting-typeerror-ord-expected-string-of-length-1-but-int-found-error
    pass
            

if __name__ == "__main__":
    with ZipFile(DOCS_PATH) as myzip:
        # List files inside zip
        filenames = list(map(lambda x: x.filename, filter(lambda x: not x.is_dir(), myzip.infolist())))
        pdf_dict = defaultdict(dict)
        for file in filenames:
            print("Processing file:", file)
            try:
                pdfReader = PdfFileReader(BytesIO(myzip.read(file)))  # read file
            except Exception as e:  # In case the file is corrupted
                print(f"The following Exception was caught: \"{e}\"")
                pdfReader = file_recovery(file, myzip)  # attempting to recover file
            # doc_dict holds the attributes of each pdf file
            doc_dict = {i[1:]: str(j) for i, j in pdfReader.getDocumentInfo().items()}
            doc_dict["Country"] = file.split("/")[0]
            doc_dict["Text"] = ""
            for page in range(pdfReader.numPages):
                try:
                    page_text = pdfReader.getPage(page).extractText()  # extracting pdf text
                except TypeError as e:
                    print(f"The following Exception was caught: \"{e}\"")
                    continue
                    # doc_dict["Text"] = 
                    # break
                page_text = text_cleaning(page_text)  # clean pdf text
                doc_dict["Text"] += page_text
            pdf_dict[os.path.splitext(os.path.basename(file))[0]] = doc_dict


    with open(os.path.join(INTER_PATH, 'pdf_files.json'), 'w') as outfile:
        json.dump(pdf_dict, outfile, ensure_ascii=False, indent=4)
