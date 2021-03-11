import nltk
import json
import uuid
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


def format_sents_for_output(sents):
    formatted_sents = []

    for i, sent in enumerate(sents):
        formatted_sents.append({f"sentence_{i}": sent, "label": []})

    return formatted_sents


def output_sents(sents, fname, country, fname_to_id_json, output_dir="../output"):
    # 1. Generate uuid for file name and store in existing json if it doesn't exist already
    with open(f"{output_dir}/{fname_to_id_json}", "r") as fin:
        fjson = json.load(fin)

        if fname not in fjson:
            f_uuid = str(uuid.uuid4())
            fjson[fname] = f_uuid
        else:
            f_uuid = fjson[fname]

    with open(f"{output_dir}/{fname_to_id_json}", "w") as fout:
        json.dump(fjson, fout, indent=4)

    # 2. Build and store the sentences in the output json
    sents_json = {}
    fformat = fname.split(".")[-1]
    sents_json[f_uuid] = {"metadata":
                              {"n_sentences": len(sents),
                               "filename": fname,
                               "format": fformat,
                               "country": country},
                          "sentences": format_sents_for_output(sents)}

    with open(f"{output_dir}/{country}_{f_uuid}_sents.json", "w") as fout:
        json.dump(sents_json, fout, indent=4)


def main():
    country = "India"
    base_path = f"../input/{country}"
    output_path = f"../output/{country}"

    # usa_files = ["Federal Register, Volume 85 Issue 190 (Wednesday, September 30, 2020).htm",
    #              "Federal Register, Volume 86 Issue 28 (Friday, February 12, 2021).htm",
    #              "Federal Register, Volume 86 Issue 29 (Tuesday, February 16, 2021).htm"]
    india_files = ["India1.txt", "India2.txt", "India_image1.txt", "India_image2.txt"]

    # TODO: Import this from txt file
    # usa_abrevs = {"no", "sec", "cong", "dist", "doc"}
    india_abrevs = {"sub", "subs", "ins", "govt", "dy", "dept", "deptt", "ptg"}

    # This is where we store the original file names mapped to their unique ids
    fname_db_name = "fname_id_db.json"

    # Choose a file for testing purposes and the minimum number of words to include in the sentences
    fname = india_files[3]
    min_num_words = 5

    with open(f"{base_path}/{fname}", "r") as txt_file:
        txt = txt_file.read()
        preprocessed = english_sents_preprocess(txt)
        sents = nltk_sents(preprocessed, en_tokenizer, india_abrevs)
        post_processed_sents = english_sents_postprocess(sents, min_num_words)
        output_sents(post_processed_sents, fname, country, fname_db_name, output_path)


if __name__ == '__main__':
    main()

