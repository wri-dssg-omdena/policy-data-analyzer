import argparse

from argparse import RawTextHelpFormatter

from src.data.pdf_processing import PDFProcessing

'''
Script arguments parser set up
'''

parser = argparse.ArgumentParser(description='''
Pdf Preprocessing Script\n
Input: .pdf files in folder with ID
Output: .txt or .csv files in folder with ID
Example:
python -m src.app.text_extraction <SOURCE_FOLDER_ID> <DESTINATION_FOLDER_ID>
The resulting files will be uploaded to the root of your Drive folder.
''', formatter_class=RawTextHelpFormatter)
parser.add_argument('source', type=str, help='''
If you have https://drive.google.com/drive/u/0/folders/1wjKu3NDWjqboTHR_wuR0yKBlyr_tceyG,
the last part of the URL, 1wjKu3NDWjqboTHR_wuR0yKBlyr_tceyG is the ID''')
parser.add_argument('destination', type=str, help='''
If you have https://drive.google.com/drive/u/0/folders/1c-TYVCLr0hwULGpJK5DT68zj6mPfdkXV,
the last part of the URL, 1c-TYVCLr0hwULGpJK5DT68zj6mPfdkXV is the ID''')
parser.add_argument('--temp_files_path', nargs='?', default='data/tmp', type=str, help='''
Directory to store temp files during preprocessing. Set to data/tmp by default
''')
parser.add_argument('--source_json', type=str, help='''
Country where the processed jsons are to be looked for
''')
parser.add_argument('--json', nargs='?', default=True, type=bool, help='''
If True, the PDF file is converted to a .json file. Otherwise, exported as a .txt. Set to False by default.
''')
args = parser.parse_args()

if __name__ == '__main__':
    pf = PDFProcessing()

    # pf.pdf_to_json_update(args.destination, args.temp_files_path, args.source_json)

    if args.json:
        pf.pdf_to_json_page_label(args.source, args.destination, args.temp_files_path)
    else:
        pf.pdf_to_txt(args.source, args.destination, args.temp_files_path)
