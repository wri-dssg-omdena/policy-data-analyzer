from tasks.data_loading.src.s3_client_utils import *
from pandas import DataFrame
from csv import reader
from codecs import getreader


class S3Client:
    def __init__(self, creds_filepath, creds_filename, bucket_name, language=None):
        self.aws_id, self.aws_secret = aws_credentials_from_file(creds_filepath, creds_filename)
        self.s3 = get_s3(self.aws_id, self.aws_secret)
        self.bucket_name = bucket_name
        self.language = language
        self.metadata_folder = f"metadata/"

        # Language dependent DB names
        self.base_folder = None
        self.raw_files_folder = None
        self.new_text_files_folder = None
        self.processed_text_files_folder = None
        self.new_sentences_folder = None
        self.processed_sentences_folder = None
        self.assisted_labeling_folder = None

        # Extra file names
        self.abbrevs_file = None

        if language:
            self._update_folder_names(language)

    def _update_folder_names(self, language):
        if self.language != language:
            # Folders
            self.base_folder = f"{language}_documents"
            self.raw_files_folder = f"{self.base_folder}/raw_pdf"
            self.new_text_files_folder = f"{self.base_folder}/text_files/new"
            self.processed_text_files_folder = f"{self.base_folder}/text_files/processed"
            self.new_sentences_folder = f"{self.base_folder}/sentences/new"
            self.processed_sentences_folder = f"{self.base_folder}/sentences/processed"
            self.assisted_labeling_folder = f"{self.base_folder}/assisted_labeling"

            # Files
            self.abbrevs_file = f"abbreviations/{language}_abbreviations.txt"

    def move_object(self, obj_name, obj_old_folder, obj_new_folder):
        """
        Move an object from a given S3 folder to another by copying it to the new folder,
        then deleting it from the old one
        """
        try:
            self.s3.Object(self.bucket_name, f"{obj_old_folder}/{obj_name}") \
                .copy_from(CopySource=f"{self.bucket_name}/{obj_new_folder}/{obj_name}")
            _ = self.s3.Object(self.bucket_name, f"{obj_old_folder}/{obj_name}").delete()
        except Exception as e:
            print(f"Error while moving {obj_name} from {obj_old_folder} to {obj_new_folder}.")
            print(e)

    def load_text_files(self, language):
        """
        Yield a text file id, and the text content of the file itself from the new text files folder
        These should be used for sentence splitting, and then calling the store_sentences() method
        """
        self._update_folder_names(language)
        for obj in self.s3.Bucket(self.bucket_name).objects.all().filter(Prefix=self.new_text_files_folder):
            if not obj.key.endswith("/"):
                file_id = obj.key.replace(self.new_text_files_folder, "").replace(".txt", "")
                text = obj.get()['Body'].read().decode('utf-8')
                yield file_id, text

    def store_sentences(self, sents, file_name, file_uuid, language):
        """
        Store a JSON file containing the metadata and sentences for a given text file in the S3 bucket
        """
        self._update_folder_names(language)
        sents_json = {file_uuid: {"metadata":
                                      {"n_sentences": len(sents),
                                       "file_name": file_name,
                                       "language": language},
                                  "sentences": sents}}

        self.s3.Object(self.bucket_name, f"{self.new_sentences_folder}/{file_uuid}_sents.json") \
            .put(Body=(json.dumps(sents_json, indent=4)))

    def load_sentences(self, language, init_doc, end_doc):
        """
        TODO: Write docs
        """
        self._update_folder_names(language)
        for i, obj in enumerate(self.s3.Bucket(self.bucket_name).objects.all().filter(Prefix=self.new_sentences_folder)):
            if not obj.key.endswith("/") and init_doc <= i < end_doc:
                sents = labeled_sentences_from_json(json.loads(obj.get()['Body'].read()))
                for sent_id, sent_labels_map in sents.items():
                    yield sent_id, sent_labels_map

    def store_assisted_labeling_csv(self, results_dictionary, queries_dictionary, init_doc, results_limit):
        """
        TODO: Write docs
        """
        path = f"s3://{self.bucket_name}/{self.assisted_labeling_folder}"
        col_headers = ["sentence_id", "similarity_score", "text"]
        for i, query in enumerate(results_dictionary.keys()):
            filename = f"{path}/query_{queries_dictionary[query]}_{i}_results_{init_doc}.csv"
            DataFrame(results_dictionary[query], columns=col_headers) \
                .head(results_limit) \
                .to_csv(filename, storage_options={"key": self.aws_id, "secret": self.aws_secret})

    def doc_ids_per_country(self, country):
        """
        Get a list of text document file IDs for a given country from the CSV database in the S3 bucket.
        In the CSV, the file id is the file name without the file extension ("23sd45fg.txt" without the ".txt")
        """
        metadata_fname = f"{self.metadata_folder}/{country}_metadata.csv"
        obj = self.s3.Object(bucket_name=self.bucket_name, key=metadata_fname)

        doc_ids = []
        for row in reader(getreader("utf-8")(obj.get()['Body'])):
            # Add original file ID without the file format
            doc_ids.append(row[3][:-4])

        return doc_ids

    def get_abbreviations(self, language):
        """
        Gets the set of abbreviations for a given language, from the text file in the S3 bucket
        """
        self._update_folder_names(language)
        obj = self.s3.Object(bucket_name=self.bucket_name, key=self.abbrevs_file)
        abbreviations_str = obj.get()['Body'].read().decode('utf-8')
        return set(abbreviations_str.split("\n"))
