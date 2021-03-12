""" Sample usage:
    -  India docs, 5 minimum word sentence, with abbreviations
        - python sentence_splitting.py -i ../input -o ../output -l eng -c India -af India_abbrevs.txt -fdb fname_id_db.json -mnw 5
    -  USA docs, 3 minimum word sentence, with abbreviations
        - python sentence_splitting.py -i ../input -o ../output -l eng -c USA -af USA_abbrevs.txt -fdb fname_id_db.json -mnw 3
"""
import nltk
import json
import os
import uuid
import argparse
import sys
from tqdm import tqdm
sys.path.append("../../../")
from tasks.text_preprocessing.src.utils import *

en_tokenizer = nltk.data.load("tokenizers/punkt/english.pickle")
es_tokenizer = nltk.data.load("tokenizers/punkt/spanish.pickle")


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


def generate_uuid(f_name, fname_ids_db_path):
    """
    Generate uuid for file name and store in existing json if it doesn't exist already
    """

    with open(fname_ids_db_path, "r") as fin:
        fjson = json.load(fin)

        if f_name not in fjson:
            f_uuid = str(uuid.uuid4())
            fjson[f_name] = f_uuid
        else:
            f_uuid = fjson[f_name]

    with open(fname_ids_db_path, "w") as fout:
        json.dump(fjson, fout, indent=4)

    return f_uuid


def output_sents(sents, f_name, f_uuid, country, output_dir="../output"):

    sents_json = {}
    fformat = f_name.split(".")[-1]
    sents_json[f_uuid] = {"metadata":
                              {"n_sentences": len(sents),
                               "filename": f_name,
                               "fileformat": fformat,
                               "country": country},
                          "sentences": format_sents_for_output(sents, f_uuid)}

    with open(f"{output_dir}/{f_uuid}_sents.json", "w") as fout:
        json.dump(sents_json, fout, indent=4)


def get_abbrevs(input_path, abbrevs_file):
    if abbrevs_file:
        with open(f"{input_path}/{abbrevs_file}", "r") as f:
            abbrevs = set([abbrev.replace("\n", "") for abbrev in f.readlines()])
            return abbrevs
    return None


def get_files(input_path, country):
    blacklist = {".DS_Store", f"{country}_abbrevs.txt"}
    return [file for file in os.listdir(input_path) if file not in blacklist]


def main(base_input_dir, base_output_dir, language, country, abbrevs_file, fname_ids_db_name, min_num_words):
    input_path = f"{base_input_dir}/{country}"
    output_path = f"{base_output_dir}/{country}"

    # NOTE: Can uncomment for manual experiments without depending on command line
    # usa_files = ["Federal Register, Volume 85 Issue 190 (Wednesday, September 30, 2020).htm",
    #              "Federal Register, Volume 86 Issue 28 (Friday, February 12, 2021).htm",
    #              "Federal Register, Volume 86 Issue 29 (Tuesday, February 16, 2021).htm"]
    # india_files = ["India1.txt", "India2.txt", "India_image1.txt", "India_image2.txt"]

    # usa_abbrevs = {"no", "sec", "cong", "dist", "doc"}
    # india_abbrevs = {"sub", "subs", "ins", "govt", "dy", "dept", "deptt", "ptg"}

    # This is where we store the original file names mapped to their unique ids
    # fname_ids_db_name = "fname_id_db.json"

    # Choose a file for testing purposes and the minimum number of words to include in the sentences
    # f_name = india_files[3]
    # min_num_words = 5

    abbrevs = get_abbrevs(input_path, abbrevs_file)
    files = get_files(input_path, country)
    tokenizer = es_tokenizer if language == "spa" else en_tokenizer

    for f_name in tqdm(files):
        with open(f"{input_path}/{f_name}", "r") as txt_file:
            txt = txt_file.read()
            preprocessed = english_sents_preprocess(txt)
            sents = nltk_sents(preprocessed, tokenizer, abbrevs)
            post_processed_sents = english_sents_postprocess(sents, min_num_words)
            f_uuid = generate_uuid(f_name, fname_ids_db_path=f"{base_output_dir}/{fname_ids_db_name}")
            output_sents(post_processed_sents, f_name, f_uuid, country, output_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('-i', '--input_path', default="../input",
                        help="Base path for input folders")
    parser.add_argument('-o', '--output_path', default="../output",
                        help="Base path for output folders")
    parser.add_argument('-l', '--language', default="eng",
                        help="Language for sentence preprocessing/splitting")
    parser.add_argument('-c', '--country', default="USA",
                        help="Country for sentence preprocessing/splitting and name of output sub-folder")
    parser.add_argument('-af', '--abbrevs_file', default="USA_abbrevs.txt",
                        help="Name of the file that contains abbreviations. Should be located in input sub-folder for country")
    parser.add_argument('-fdb', '--fname_ids_db_name', default="fname_id_db.json",
                        help="Name of the JSON file that contains the mappings between file names and their unique ids. Should be located in output base folder")
    parser.add_argument('-mnw', '--min_num_words', default=5,
                        help="Minimum number of words that a sentence needs to have to be stored")

    args = parser.parse_args()

    main(args.input_path, args.output_path, args.language, args.country, args.abbrevs_file, args.fname_ids_db_name, int(args.min_num_words))



