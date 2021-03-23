import boto3
import json


def aws_credentials_from_file(path, filename):
    """
    Get the AWS S3 Id and Secret credentials, from a json file in the format:
        {"AWS_ID": "AWS_SECRET"}
    """
    with open(f"{path}/{filename}", 'r') as f:
        key_dict = json.load(f)
    for key in key_dict:
        aws_id = key
        aws_secret = key_dict[key]
        return aws_id, aws_secret


def get_s3(aws_id, aws_secret, region='us-east-1'):
    """
    Create an S3 boto3 resource given AWS credentials and a region
    """
    return boto3.resource(
        service_name='s3',
        region_name=region,
        aws_access_key_id=aws_id,
        aws_secret_access_key=aws_secret
    )


def labeled_sentences_from_json(sents_json):
    """
    Get a map of labeled sentences in the format:
        {sentence_id: {"text": "sentence text", "labels": []}}
    From the json that included other information such as metadata
    """
    return {sent_id: sent_labels_map for sent_id, sent_labels_map in [*sents_json.values()][0]["sentences"].items()}


## TODO: Move this function somewhere else?
def format_sents_for_output(sents, doc_id):
    return {f"{doc_id}_sent_{i}": {"text": sent, "label": []} for i, sent in enumerate(sents)}