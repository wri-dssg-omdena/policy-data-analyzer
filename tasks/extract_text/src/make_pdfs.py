# -*- coding: utf-8 -*-
"""
Extracts text and metadata from pdf files. Reads pdf files from ../input/onedrive_docs.zip 
and outputs extracted information to ../output/pdf_files.json.
"""
import json
import logging
import os
from collections import defaultdict
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

from pikepdf import Pdf
from PyPDF2 import PdfFileReader


def text_cleaning(text):
    """Cleans a piece of text by removing escaped characters.

    Args:
        text (str): string with text

    Returns:
        str: cleaned piece of text
    """
    # Remove escaped characters
    escapes = ''.join([chr(char) for char in range(1, 32)])
    text = text.translate(str.maketrans('', '', escapes))
    return text


def file_recovery(filename, zipfile):
    """Attempts to recover a pdf file inside a zip that wasn't read correctly.

    Args:
        filename (str): file path string
        zipfile (ZipFile): ZipFile instance where file is located

    Returns:
        PdfFileReader: new PdfFileReader instance from where text will be read
    """
    with Pdf.open(BytesIO(zipfile.read(filename))) as pdf_file:  # attempting to recovery file
        path_to_file = os.path.join(OUTPUT_PATH, os.path.basename(filename))
        pdf_file.save(path_to_file)  # writes the file to disk
        pdfReader = PdfFileReader(path_to_file)  # attempts to read the file again
        os.remove(path_to_file)
    return pdfReader

def text_reader():
    """Function to solve TypeError: ord() expected string of length 1, but 
     int found error. TO IMPLEMENT.
    """
    # Useful link: https://stackoverflow.com/questions/55993860/getting-typeerror-ord-expected-string-of-length-1-but-int-found-error
    pass


def main():
    logger = logging.getLogger(__name__)
    logger.info('Making pdf_files.json from base pdf files')

    with ZipFile(INPUT_PATH) as myzip:
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
            doc_dict["Country"], doc_dict["Text"] = file.split("/")[0], []
            for page in range(pdfReader.numPages):
                try:
                    page_text = pdfReader.getPage(page).extractText()  # extracting pdf text
                except TypeError as e:
                    logger.warning(e)
                    logger.info(f"Skipping {file}...")
                    continue
                page_text = text_cleaning(page_text)  # clean pdf text
                doc_dict["Text"].append(page_text)
            doc_dict["Text"] = " ".join(doc_dict["Text"])  # joining pages' text
            pdf_dict[os.path.splitext(os.path.basename(file))[0]] = doc_dict

    with open(os.path.join(OUTPUT_PATH, 'pdf_files.json'), 'w') as outfile:
        json.dump(pdf_dict, outfile, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # Necessary paths
    TASK_DIR = Path(__file__).resolve().parents[1]
    OUTPUT_PATH = os.path.join(TASK_DIR, "output")
    INPUT_PATH = os.path.join(TASK_DIR, "input", "onedrive_docs.zip")

    main()
