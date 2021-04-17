from collections import defaultdict
from sentence_transformers import SentenceTransformer
from tasks.data_loading.src.utils import *
import boto3
from scipy.spatial import distance

'''
TODO:
- Create AWS client/loader for easy retrieval of single and multiple files. Must be able to retrieve:
    - JSON files (sentence splitting process)
    - Text files
    - CSV files
    - Excel files
'''


def save_results_as_separate_csv(results_dictionary, queries_dictionary, init_doc, results_limit, aws_id, aws_secret):
    path = "s3://wri-nlp-policy/english_documents/assisted_labeling"
    col_headers = ["sentence_id", "similarity_score", "text"]
    for i, query in enumerate(results_dictionary.keys()):
        filename = f"{path}/query_{queries_dictionary[query]}_{i}_results_{init_doc}.csv"
        pd.DataFrame(results_dictionary[query], columns=col_headers).head(results_limit).to_csv(filename, storage_options={"key": aws_id, "secret": aws_secret})


def setup_s3(credentials_fname):
    aws_id, aws_secret = aws_credentials_from_file(credentials_fname)
    region = 'us-east-1'

    s3 = boto3.resource(
        service_name='s3',
        region_name=region,
        aws_access_key_id=aws_id,
        aws_secret_access_key=aws_secret
    )

    return s3


def main(aws_credentials_fname):
    s3 = setup_s3(aws_credentials_fname)

    # Define params
    init_at_doc = 14778
    end_at_doc = 16420

    similarity_threshold = 0
    search_results_limit = 500

    language = "english"
    bucket_name = 'wri-nlp-policy'

    transformer_name = 'xlm-r-bert-base-nli-stsb-mean-tokens'
    model = SentenceTransformer(transformer_name)

    # Get all sentence documents
    sentences = load_sentences_for_language(language, s3, bucket_name, init_at_doc, end_at_doc)

    # Define queries
    path = "../../input/"
    filename = "English_queries.xlsx"
    file = path + filename
    df = pd.read_excel(file, engine='openpyxl', sheet_name="Hoja1", usecols="A:C")

    queries = {}
    for index, row in df.iterrows():
        queries[row['Query sentence']] = row['Policy instrument']

    # Calculate and store query embeddings
    query_embeddings = dict(zip(queries, [model.encode(query.lower(), show_progress_bar=False) for query in queries]))

    # For each sentence, calculate its embedding, and store the similarity
    query_similarities = defaultdict(list)

    i = 0
    for sentence_id, sentence in sentences.items():
        sentence_embedding = model.encode(sentence['text'].lower(), show_progress_bar=False)
        i += 1
        if i % 100 == 0:
            print(i)

        for query_text, query_embedding in query_embeddings.items():
            score = round(1 - distance.cosine(sentence_embedding, query_embedding), 4)
            if score > similarity_threshold:
                query_similarities[query_text].append([sentence_id, score, sentences[sentence_id]['text']])

    # Sort results by similarity score
    for query in query_similarities:
        query_similarities[query] = sorted(query_similarities[query], key=lambda x: x[1], reverse=True)

    # Store results
    save_results_as_separate_csv(query_similarities, queries, init_at_doc, search_results_limit, aws_id, aws_secret)


if __name__ == '__main__':
    main()