import pandas as pd
import unidecode
import os

import src.models.labeled_lda_SergioSJS.model.labeled_lda as llda
from src.data.text_preprocessor import TextPreprocessor

countries = ['mexico','peru']#,'guatemala','chile','el salvador']
docs_path = r'.\src\data\docs'

'''
Outputs
----------
labeled_documents : list of tuples, where the first element is the entire document
    and the second one contains all the labels specified in 'WRI Policy Tags.xlsx'
    file.
labeled_paragraphs : list of tuples, where the first element is a particular paragraph
    and the second one contains all the labels specified in 'WRI Policy Tags.xlsx'
    file.
'''

def preclean_xlsxParagraph(text_list):
    preprocessor = TextPreprocessor()
    word_list = list()
    for text in text_list:
        clean_text = preprocessor.clean_sentence(text)
        word_list.append(' '.join(preprocessor.tokenize_text(clean_text)))
    return(word_list)

def preclean_entireDoc(text):
    preprocessor = TextPreprocessor()
    clean_text = preprocessor.clean_sentence(text)
    word_list = preprocessor.tokenize_text(clean_text)
    words = ' '.join(word_list)
    return(words)

labeled_documents = list()
labeled_paragraphs = list()
all_labels = list()
corpus = list()
all_paragraphs = list()

for country in countries:

    labels_file = os.path.join(docs_path,'WRI Policy Tags.xlsx')
    country = country.title()
    policy_tags = pd.read_excel(io = labels_file, sheet_name = country)

    txt_path = os.path.join(docs_path, country)
    files = policy_tags.Path.unique()

    label = policy_tags['Key words'].apply(
        lambda x: x.lower().split(', ') if type(x) == str else ["nan"])#.values
    all_labels.append(label)

    paragraph = policy_tags['Text'].apply(
        lambda x: x.lower().replace('\n',' ') if type(x) == str else ["nan"])#.values
    paragraph = preclean_xlsxParagraph(paragraph.tolist())
    all_paragraphs.append(paragraph)
    print(txt_path)

    for i in range(len(paragraph)):
        labeled_paragraphs.append((paragraph[i], label[i]))
    
    for elem in files:
        if type(elem) == str:
            file_name = elem.split('/')[-1].split('.')[0].lower()
        else: continue 
        open_path = os.path.join(txt_path, file_name + "_preprocessed.txt")
        print(open_path)
        
        try:
            with open(open_path, 'rb') as text:
                decoded = text.read()
                decoded = decoded.decode('UTF-8').replace('\n', ' ')
                corpus.append(decoded)
                decoded = preclean_entireDoc(decoded)            
            temp_df = policy_tags[policy_tags['Path']==elem].copy()
            fulldoc_labs = temp_df['Key words'].apply(
                lambda x: x.lower().replace('\n',
                    ' ').split(', ') if type(x) == str else ["nan"]).tolist()
            fulldoc_labs = [j for i in fulldoc_labs for j in i]
            labeled_documents.append((decoded, fulldoc_labs))
            text.close
        except: 
            print("This file must be included locally ",file_name)
            continue

# print(all_paragraphs[1])

# print(labeled_paragraphs[0])
# train_data = [elem for elem in labeled_paragraphs if elem[1] != ["nan"]]
# print(train_data)

print(labeled_documents)
train_data = [(t, [x for x in l if x != "nan"]) for t, l in labeled_documents]
print(train_data)


llda_model = llda.LldaModel(labeled_documents=train_data, alpha_vector=0.01)
print(llda_model)

# training
while True:
    print("iteration %s sampling..." % (llda_model.iteration + 1))
    llda_model.fit(1)
    print("after iteration: %s, perplexity: %s" % (llda_model.iteration, llda_model.perplexity()))
    print("delta beta: %s" % llda_model.delta_beta)
    if llda_model.is_convergent(method="beta", delta=0.01):
        break
      
print(llda_model)      