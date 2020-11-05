# -*- coding: utf-8 -*-
import logging
from pathlib import Path
from dotenv import find_dotenv, load_dotenv
import os
from collections import defaultdict
from zipfile import ZipFile
from pikepdf import Pdf
from PyPDF2 import PdfFileReader
from io import BytesIO
import json


def text_cleaning(text):
    # Remove escaped characters
    escapes = ''.join([chr(char) for char in range(1, 32)])
    text = text.translate(str.maketrans('', '', escapes))
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


def main():
    """ Runs data processing scripts to turn raw data from (../raw) into
        cleaned data ready to be analyzed (saved in ../processed).
    """
    logger = logging.getLogger(__name__)
    logger.info('Making pdf_files.json from base pdf files')

    with ZipFile(DOCS_PATH) as myzip:
        # List files inside zip
        filenames = list(map(lambda x: x.filename, filter(lambda x: not x.is_dir(), myzip.infolist())))
        pdf_dict = defaultdict(dict)
        for file in filenames:
            logger.info(f"Processing {file}...")
            try:
                pdfReader = PdfFileReader(BytesIO(myzip.read(file)))  # read file
            except Exception as e:  # In case the file is corrupted
                logger.warning(e)
                logger.info(f"Attempting to recover {file}...")
                pdfReader = file_recovery(file, myzip)  # attempting to recover file
            # doc_dict holds the attributes of each pdf file
            doc_dict = {i[1:]: str(j) for i, j in pdfReader.getDocumentInfo().items()}
            doc_dict["Country"] = file.split("/")[0]
            doc_dict["Text"] = ""
            for page in range(pdfReader.numPages):
                try:
                    page_text = pdfReader.getPage(page).extractText()  # extracting pdf text
                except TypeError as e:
                    logger.warning(e)
                    logger.info(f"Skipping {file}...")
                    continue
                    # doc_dict["Text"] = 
                    # break
                page_text = text_cleaning(page_text)  # clean pdf text
                doc_dict["Text"] += page_text
            pdf_dict[os.path.splitext(os.path.basename(file))[0]] = doc_dict

    with open(os.path.join(INTER_PATH, 'pdf_files.json'), 'w') as outfile:
        json.dump(pdf_dict, outfile, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    project_dir = Path(__file__).resolve().parents[2]
    INTER_PATH = os.path.join(project_dir, "data", "interim")
    DOCS_PATH = os.path.join(project_dir, "data", "raw", "onedrive_docs.zip")

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    load_dotenv(find_dotenv())

    main()
