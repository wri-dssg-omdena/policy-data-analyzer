import glob
import pandas as pd
import unidecode
import os

countries = ['mexico','peru']
docs_path = r'.\src\data\docs'

documents = list()
corpus = list()

for country in countries:

    txt_path = os.path.join(docs_path, country.title())
    files = os.listdir(txt_path)#glob.glob(txt_path)
    files = [file for file in files if '.txt' in file]

    for elem in files:
        if type(elem) == str:
            file_name = elem.split('/')[-1].split('.')[0]#.lower()
        else: continue 
        open_path = os.path.join(txt_path, file_name + ".txt")
        #os.path.join(txt_path, file_name + "_preprocessed.txt")
        print(open_path)
        
        try:
            with open(open_path, 'rb') as text:
                decoded = text.read()
                decoded = decoded.decode('UTF-8').replace('\n', ' ')        
            documents.append(decoded)
            text.close
        except: 
            print("This file must be included locally ", file_name)
            continue