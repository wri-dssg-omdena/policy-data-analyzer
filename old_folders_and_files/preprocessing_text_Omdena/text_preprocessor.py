import os
import re
import shutil
import string
import sys
import itertools

import es_core_news_sm
import nltk
import unidecode

import numpy as np

from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize
from num2words import num2words
from oauth2client.client import GoogleCredentials
from pathlib import Path
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

class TextPreprocessor:
    def __init__(self):
        self.nlp_model = es_core_news_sm.load()  # load spacy with spanish model
        self.nlp_model.max_length = 4000000
        stop = stopwords.words('spanish')  # stopwords in spanish
        sw_es = self.nlp_model.Defaults.stop_words  # stopwords in spanish
        self.sw = sw_es.union(stop)

    def authorize_drive(self):
        '''
        Authorize this script to upload and download files to your computer.
        '''
        gauth = GoogleAuth()
        gauth.LocalWebserverAuth()
        driven = GoogleDrive(gauth)
        return driven

    def download_files_from_folder(self, drive_client, source, temp_files_path):
        '''
        drive_client: The client on which to call the list and download operations required.
        source:       The ID of the folder to download the files from.
        '''
        file_list = drive_client.ListFile(
            {'q':  "'%s' in parents" % source}).GetList()
        # Create local temporary directory for files to download.
        local_download_path = Path(temp_files_path)
        local_download_path.mkdir(parents=True, exist_ok=True)
        output_file_list = []
        for f in file_list:
            fname = local_download_path/f['title']
            f_ = drive_client.CreateFile({'id': f['id']})
            f_.GetContentFile(fname)
            output_file_list.append(fname)
        return output_file_list

    def upload_file(self, drive_client, filename, destination):
        drive_file = drive_client.CreateFile({'title': filename.name,
                                            'parents': [{'id': destination}]})
        drive_file.SetContentFile(str(filename)) 
        drive_file.Upload()

    def split_into_paragraphs(self, text):
        '''
        Segment a text into paragraphs.
        '''
        paragraphs = text.split('\n')
        tokenized_paragraphs = []
        for p in paragraphs:
            punctuations = '''!()-[]{};:'"\,<>./?@#$%^&*_~'''
            sentences = p
            for punctuation in punctuations:
                sentences = sentences.replace(punctuation, '\n')
            sentences = sentences.split('\n\n')
            tokenized_paragraphs.append(sentences)
        return tokenized_paragraphs

    def clean_sentence(self, text, remove_punct=True, replace_accent=True,
        tolower=True, alphabetic_only=False):
        '''
        Cleans text including removal of whitespace, punctuation, accented characters,
        special characters and transforming to lowercase. Assumes input text is string.
        Returns clean string.
        '''
        if replace_accent:
            text = unidecode.unidecode(text)
        if remove_punct:
            table = str.maketrans('', '', string.punctuation)
            text = text.translate(table)
        if tolower:
            text = text.lower()
        if alphabetic_only:
            text = re.sub("[^a-zA-Z]+", " ", text)
        return text.strip()

    def tokenize_text(self, text, remove_stopwords=True, lemmatisation=True,
        num_words=False, as_string=False):
        '''
        Tokenizes text, normalized text including spanish lemmatisation, removal
        of spanish stop words and transforming numbers to words.
        Assumes input text is string. Returns a list of tokens.
        '''
        text = self.nlp_model(text)
        tokenized = list()
        for word in text:
            if lemmatisation:
                lemma = word.lemma_.strip()
            else:
                lemma = str(word).strip()
            if num_words:
                lemma = nums_to_words(lemma) # transform numbers to words
            if lemma:
                if not remove_stopwords or (remove_stopwords and lemma not in self.sw):
                    tokenized.append(lemma)
        if as_string:
            tokenized = " ".join(tokenized)
        return tokenized

    def nums_to_words(self, word):
        '''
        Transforms numbers to spanish names for each number in words.
        Assumes input is string. Returns a string.
        '''
        if word.isdigit(): # check if the word is a number
            return num2words(word, lang='es')
        else:
            return re.sub(r'[0-9]+', '', word) # remove the number attached to a word

    def preprocess_text_files_paragraphs(self, paths, program_args):
        '''
        paths: list of the temporary files downloaded from Google Drive for preprocessing
        '''
        print(program_args)

        file_paragraphs = []
        for p in paths:
            with open(p, 'r', encoding='utf-8') as f:
                p_data = f.read()
                paragraphs = self.split_into_paragraphs(p_data)
                for i, paragraph in enumerate(paragraphs):
                    for j, sentence in enumerate(paragraph):
                        clean_sentence = self.clean_sentence(
                            sentence,
                            remove_punct=(not program_args.punctuation),
                            replace_accent=(not program_args.accents),
                            tolower=(not program_args.capitalization)
                        )
                        tokenized_sentence = self.tokenize_text(
                            clean_sentence,
                            (not program_args.stopwords),
                            program_args.lemmatisation,
                            program_args.number_words
                        )
                        paragraphs[i][j] = tokenized_sentence
                file_paragraphs.append(paragraphs)
        if program_args.join:
            file_paragraphs = list(np.array(file_paragraphs)).flatten()
        return file_paragraphs

    def upload_token_files(self, drive_client, paths, program_args, tokens):
        '''
        drive_client: The client on which to call the list and download operations required.
        paths: list of the temporary files downloaded from Google Drive preprocessed
        tokens: list of tokens (per file if --join argument is False, all files in one otherwise)
        '''
        if program_args.join:
            filename = program_args.output_filename
            local_download_path = program_args.temp_files_path
            tmp_filename = os.path.join(local_download_path, filename)
            with open(tmp_filename, 'w', encoding='utf-8') as f:
                for token in tokens:
                    f.write(str(token) + ' ')
            self.upload_file(drive_client, tmp_filename, program_args.destination)
        else:
            for path, path_tokens in zip(paths, tokens):
                filename = path.name.split('.')[0]
                tmp_filename = path.parent/(filename + '_preprocessed.txt')
                
                with open(tmp_filename, 'w', encoding='utf-8') as f:
                    for sentence in path_tokens:
                        for token in sentence:
                            f.write(' '.join(token))
                        f.write('\n')
                
                self.upload_file(drive_client, tmp_filename, program_args.destination)

    def clean_temp_folder(self, path):
        if os.path.isdir(path):
            shutil.rmtree(path)

    def text_preprocessor_main(self, program_args):
        '''
        program_args: See argument parser definition for a description on each field contained.
        '''
        print('1. Authorize Google Drive.')
        drive_client = self.authorize_drive()
        print('2. Download files.')
        local_file_paths = self.download_files_from_folder(drive_client, program_args.source, program_args.temp_files_path)
        print('3. Preprocess text files into tokens.')
        tokens = self.preprocess_text_files_paragraphs(local_file_paths, program_args)
        print('4. Upload token files to Google Drive')
        self.upload_token_files(drive_client, local_file_paths, program_args, tokens)
        print('5. Remove tmp folder')
        self.clean_temp_folder(program_args.temp_files_path)