""" Sample usage:
    -  Format
        $ python sentence_splitting.py -c [path_to_aws_credentials_json] -l [english | spanish] -n [any integer]
    -  English documents, 5 words minimum for a sentence to be stored
        $ python sentence_splitting.py -c /Users/some_user/credentials.json -l english -n 5

    Expected format for JSON credentials file:
    {
        "aws": {
            "id": "AWS ID",
            "secret": "AWS SECRET"
        }
    }
"""
import sys

sys.path.append("../../../")
from tasks.text_preprocessing.src.utils import *

import nltk
import json
import boto3
import csv
import codecs
import argparse

EN_TOKENIZER = nltk.data.load("tokenizers/punkt/english.pickle")
ES_TOKENIZER = nltk.data.load("tokenizers/punkt/spanish.pickle")
BUCKET_NAME = "wri-nlp-policy"


def english_sents_preprocess(txt, remove_new_lines=False):
    """
    Steps in the preprocessing of text:
        1. Remove HTML tags
        2. Replace URLS by a tag [URL]
        3. Replace new lines and tabs by normal spaces - sometimes sentences have new lines in the middle
        4. Remove excessive spaces (more than 1 occurrence)
        5. Parse emails and abreviations
    """

    if remove_new_lines:
        txt = replace_links(remove_html_tags(txt)).replace("\n", " ").replace("\t", " ").strip()
    else:
        txt = replace_links(remove_html_tags(txt)).strip()

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


def english_sents_postprocess(sents, min_num_words=4):
    """
    Remove sentences that are made of less than a given number of words. Default is 4
    """

    return [sent for sent in sents if len(sent.split()) >= min_num_words]


def nltk_sents(txt, tokenizer, extra_abbreviations=None):
    if extra_abbreviations:
        tokenizer._params.abbrev_types.update(extra_abbreviations)

    sents = tokenizer.tokenize(txt)
    return sents


def format_sents_for_output(sents, doc_id):
    formatted_sents = {}

    for i, sent in enumerate(sents):
        formatted_sents.update({f"{doc_id}_sent_{i}": {"text": sent, "label": []}})

    return formatted_sents


def doc_ids_per_country(country, s3):
    """
    Get a list of text document file IDs for a given country from the CSV database in the S3 bucket.
    In the CSV, the file id is the file name without the file extension ("23sd45fg.txt" without the ".txt")
    """
    metadata_fname = f"metadata/{country}_metadata.csv"
    obj = s3.Object(bucket_name=BUCKET_NAME, key=metadata_fname)

    doc_ids = []
    for row in csv.reader(codecs.getreader("utf-8")(obj.get()['Body'])):
        # Add original file ID without the file format
        doc_ids.append(row[3][:-4])

    return doc_ids


def get_abbreviations(language, s3):
    """
    Gets the set of abbreviations for a given language, from the text file in the S3 bucket
    """
    abbreviations_fname = f"abbreviations/{language}_abbreviations.txt"
    obj = s3.Object(bucket_name=BUCKET_NAME, key=abbreviations_fname)
    abbreviations_str = obj.get()['Body'].read().decode('utf-8')
    return set(abbreviations_str.split("\n"))


def aws_credentials_from_file(f_name):
    """
    Returns the id and secret for an AWS account. Expected format of input file:
        "aws": {
            "id": "AWS ID",
            "secret": "AWS SECRET"
        }
    }
    """
    with open(f_name, "r") as f:
        creds = json.load(f)

    return creds["aws"]["id"], creds["aws"]["secret"]


def move_s3_object(obj_name, obj_old_folder, obj_new_folder, s3):
    """
    Moves an object from a given S3 folder to another by copying it to the new folder it and then deleting it from the old one
    """
    try:
        s3.Object(BUCKET_NAME, f"{obj_old_folder}/{obj_name}").copy_from(
            CopySource=f"{BUCKET_NAME}/{obj_new_folder}/{obj_name}")
        _ = s3.Object(BUCKET_NAME, f"{obj_old_folder}/{obj_name}").delete()
    except Exception as e:
        print(f"Error while moving {obj_name} from {obj_old_folder} to {obj_new_folder}.")
        print(e)


def output_sents(sents, f_name, f_uuid, language, s3):
    """
    Store a JSON file containing the metadata and sentences for a given text file in the S3 bucket
    """
    sents_json = {}
    fformat = f_name.split(".")[-1]
    sents_json[f_uuid] = {"metadata":
                              {"n_sentences": len(sents),
                               "file_name": f_name,
                               "file_format": fformat},
                          "sentences": format_sents_for_output(sents, f_uuid)}

    s3.Object(BUCKET_NAME, f"{language}_documents/sentences/{f_uuid}_sents.json").put(
        Body=(json.dumps(sents_json, indent=4)))


def main(credentials_fname, language, min_num_words):
    """
    1. Set up S3 bucket object using credentials from given file
    2. Iterate through new text files in given language folder (i.e english_documents/text_files/new/)
    3. For each file, split the text into sentences and store the JSON sentences file to the sentences folder in the bucket (i.e english_documents/sentences
    4. Move the text file from the new to the processed folder (i.e english_documents/text_files/processed/)
    """
    # Set up AWS S3 bucket info
    aws_id, aws_secret = aws_credentials_from_file(credentials_fname)
    region = 'us-east-1'

    s3 = boto3.resource(
        service_name='s3',
        region_name=region,
        aws_access_key_id=aws_id,
        aws_secret_access_key=aws_secret
    )

    # Set up abbreviations and sentence tokenizer
    abbrevs = get_abbreviations(language, s3)
    tokenizer = ES_TOKENIZER if language == "spanish" else EN_TOKENIZER

    # Get original text files, split them into sentences, and store them to the S3 bucket
    i = 0
    error_files = []
    new_text_files_folder = f"{language}_documents/text_files/new"
    processed_text_files_folder = f"{language}_documents/text_files/processed"
    for obj in s3.Bucket(BUCKET_NAME).objects.all().filter(Prefix=new_text_files_folder):
        # Don't get the directory itself
        if not obj.key.endswith("/"):
            print("Processing", obj.key)
            file_id = obj.key.replace(new_text_files_folder, "").replace(".txt", "")
            text = obj.get()['Body'].read().decode('utf-8')
            try:
                preprocessed = english_sents_preprocess(text)
                sents = nltk_sents(preprocessed, tokenizer, abbrevs)
                post_processed_sents = english_sents_postprocess(sents, min_num_words)
                output_sents(post_processed_sents, obj.key, file_id, language, s3)
                move_s3_object(file_id + ".txt", new_text_files_folder, processed_text_files_folder, s3)
            except Exception as e:
                error_files.append({file_id: e})

        i += 1
        if i == 2:
            break
        if i % 100 == 0:
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

    args = parser.parse_args()

    main(args.creds_file, args.language, int(args.min_num_words))
