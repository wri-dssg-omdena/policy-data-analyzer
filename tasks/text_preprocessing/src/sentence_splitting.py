""" Sample usage:
    -  Format
        $ python sentence_splitting.py -c [path_to_aws_credentials_json] -l [english | spanish] -n [any integer]
    -  English documents, 5 words minimum for a sentence to be stored
        $ python sentence_splitting.py -c /Users/some_user/credentials.json -l english -n 5

    Expected format for JSON credentials file:
    {
        "AWS ID": "AWS SECRET"
    }
"""
from typing import Dict, List, Any, Set

from tasks.text_preprocessing.src.utils import *
from tasks.data_loading import S3Client

import nltk
import json
import argparse
import unidecode

EN_TOKENIZER = nltk.data.load("tokenizers/punkt/english.pickle")
ES_TOKENIZER = nltk.data.load("tokenizers/punkt/spanish.pickle")


def format_sents_for_output(sents: List[str], doc_id: str) -> Dict[str, Dict[str, Any]]:
    """
    Transform a list of sentences into a dict of format:
        {
            "sent_id": {"text": "sentence text", "label": []}
        }
    """
    formatted_sents = {}

    for i, sent in enumerate(sents):
        formatted_sents.update({f"{doc_id}_sent_{i}": {"text": sent, "label": []}})

    return formatted_sents


def preprocess_text(txt: str, remove_new_lines: bool = False) -> str:
    """
    Steps in the preprocessing of text:
        1. Remove HTML tags
        2. Replace URLS by a tag [URL]
        3. Replace new lines and tabs by normal spaces - sometimes sentences have new lines in the middle
        4. Remove excessive spaces (more than 1 occurrence)
        5. Parse emails and abreviations
    """
    txt = replace_links(remove_html_tags(txt)).strip()
    if remove_new_lines:
        txt = txt.replace("\n", " ").replace("\t", " ").strip()

    txt = remove_multiple_spaces(txt)
    txt = parse_emails(txt)
    txt = parse_acronyms(txt)

    new_txt = ""
    all_period_idx = set([indices.start() for indices in re.finditer("\.", txt)])

    for i, char in enumerate(txt):
        if i in all_period_idx:
            # Any char following a period that is NOT a space means that we should not add that period
            if i + 1 < len(txt) and txt[i + 1] != " ":
                continue

            # NOTE: Any char that is a number following a period will not count.
            # For enumerations, we're counting on docs being enumerated as "(a)" or "(ii)", and if not,
            # they will be separated by the "." after the number:
            # "Before bullet point. 3. Bullet point text" will just be "Before bullet point 3." and "Bullet point text" as the sentences
            if i + 2 < len(txt) and txt[i + 2].isnumeric():
                continue

            # If we wanted to have all numbered lists together, uncomment this, and comment out the previous condition
            # if i + 2 < len(txt) and not txt[i + 2].isalpha():
            #     continue

        new_txt += char

    return new_txt


def preprocess_english_text(txt: str, remove_new_lines: bool = False) -> str:
    return preprocess_text(txt, remove_new_lines)


def preprocess_spanish_text(txt: str, remove_new_lines: bool = False) -> str:
    return unidecode.unidecode(preprocess_text(txt, remove_new_lines))


def remove_short_sents(sents: List[str], min_num_words: int = 4) -> List[str]:
    """
    Remove sentences that are made of less than a given number of words. Default is 4
    """
    return [sent for sent in sents if len(sent.split()) >= min_num_words]


def get_nltk_sents(txt: str, tokenizer: nltk.PunktSentenceTokenizer, extra_abbreviations: Set[str] = None) -> List[str]:
    if extra_abbreviations is not None:
        tokenizer._params.abbrev_types.update(extra_abbreviations)

    return tokenizer.tokenize(txt)


def main(credentials_fpath, language, min_num_words, print_every):
    """
    1. Set up S3 bucket object using credentials from given file
    2. Iterate through new text files in given language folder (i.e english_documents/text_files/new/)
    3. For each file, split the text into sentences and store the JSON sentences file to the sentences folder in the bucket (i.e english_documents/sentences/)
    4. Move the text file from the new to the processed folder (i.e english_documents/text_files/processed/)
    """

    s3_client = S3Client(creds_filepath=credentials_fpath,
                         bucket_name="wri-nlp-policy", language="spanish")

    abbrevs = s3_client.get_abbreviations("spanish")
    tokenizer = ES_TOKENIZER if language == "spanish" else EN_TOKENIZER

    new_text_files_folder = f"{language}_documents/text_files/new"
    processed_text_files_folder = f"{language}_documents/text_files/processed"

    i = 0
    error_files = []
    for file_id, text in s3_client.load_text_files(language):
        try:
            file_id = file_id.replace("/", "")
            preprocessed_text = preprocess_spanish_text(text)
            sents = get_nltk_sents(preprocessed_text, tokenizer, abbrevs)
            postprocessed_sents = format_sents_for_output(remove_short_sents(sents, min_num_words), file_id)
            s3_client.store_sentences(postprocessed_sents, file_id, language)
            s3_client.move_object(file_id + ".txt", new_text_files_folder, processed_text_files_folder)

        except Exception as e:
            error_files.append({file_id: e})

        i += 1

        if i % print_every == 0:
            print("----------------------------------------------")
            print(f"Processing {i} documents...")
            print(f"Number of errors so far: {len(error_files)}")
            print("----------------------------------------------")

    with open("../output/sentence_splitting_errors.json", "w") as f:
        json.dump(error_files, f)

    print("=============================================================")
    print(f"Total documents processed: {i}")
    print(f"Total number of documents with errors: {len(error_files)}. Stored file in ../output/sentence_splitting_errors.json")
    print("=============================================================")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('-c', '--creds_file', required=True,
                        help="AWS credentials JSON file")
    parser.add_argument('-l', '--language', required=True,
                        help="Language for sentence preprocessing/splitting. Current options are: english, spanish")
    parser.add_argument('-n', '--min_num_words', default=5,
                        help="Minimum number of words that a sentence needs to have to be stored")
    parser.add_argument('-p', '--print_every', default=100,
                        help="Print status of preprocessing every X iterations")

    args = parser.parse_args()

    main(args.creds_file, args.language, int(args.min_num_words), int(args.print_every))
