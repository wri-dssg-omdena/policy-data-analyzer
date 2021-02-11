import argparse

import nltk

from argparse import RawTextHelpFormatter

from src.data.text_preprocessor import TextPreprocessor

'''
Script arguments parser set up
'''

parser = argparse.ArgumentParser(description='''
Text Preprocessing Script\n
Input: .txt files in folder with ID
Output: .txt or .csv files in folder with ID

Example:
python -m src.app.text_preprocessing <SOURCE_FOLDER_ID> <DESTINATION_FOLDER_ID>

The resulting files will be uploaded to the root of your Drive folder.
''', formatter_class=RawTextHelpFormatter)
parser.add_argument('source', type=str, help='''
If you have https://drive.google.com/drive/u/0/folders/1wjKu3NDWjqboTHR_wuR0yKBlyr_tceyG,
the last part of the URL, 1wjKu3NDWjqboTHR_wuR0yKBlyr_tceyG is the ID''')
parser.add_argument('destination', type=str, help='''
If you have https://drive.google.com/drive/u/0/folders/1c-TYVCLr0hwULGpJK5DT68zj6mPfdkXV,
the last part of the URL, 1c-TYVCLr0hwULGpJK5DT68zj6mPfdkXV is the ID''')
parser.add_argument('--stopwords', nargs='?', default=False, type=bool, help='''
If True, keeps stopwords. Set to False by default.
''')
parser.add_argument('--lemmatisation', nargs='?', default=False, type=bool, help='''
If True, lemmatises tokens. Set to False by default.
''')
parser.add_argument('--number_words', nargs='?', default=False, type=bool, help='''
If True, converts numbers to words. Set to False by default.
''')
parser.add_argument('--punctuation', nargs='?', default=False, type=bool, help='''
If True, keeps punctuation. Set to False by default.
''')
parser.add_argument('--accents', nargs='?', default=True, type=bool, help='''
If True, keeps accents. Set to True by default.
''')
parser.add_argument('--capitalization', nargs='?', default=True, type=bool, help='''
If True, keeps capitalization. Set to True by default.
''')
parser.add_argument('--join', nargs='?', default=False, type=bool, help='''
If true, joins all files to a single file. Set to False by default.
''')
parser.add_argument('--temp_files_path', nargs='?', default='data/tmp', type=str, help='''
Directory to store temp files during preprocessing. Set to data/tmp by default
''')
parser.add_argument('--output_filename', nargs='?', default='preprocessed.txt', type=str, help='''
If exporting a single file, the filename of this exported file. Set to preprocessed.txt by default.
''')
args = parser.parse_args()

if __name__ == "__main__":
    nltk.download('stopwords')
    nltk.download('punkt')
    TextPreprocessor().text_preprocessor_main(args)
