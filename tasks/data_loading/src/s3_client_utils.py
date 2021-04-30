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

def versioning_s3_objects(s3, bucket_name, sents_folder, dest_bucket_name):
    """
    When a file is changed in the s3 bucket, changes might not be available before 24h because the old versions are cached in the 
    AWS cloud front. There are two alternatives to access new files. 
    1. Invalidating files in the CloudFront. But you need permission and it comes at a cost
    2. Make a version of the file by changing its name.
    This function is to version files. It is designed to make a version and revert it to the original when you apply it a second time
    """

    for i, obj in enumerate(s3.Bucket(bucket_name).objects.all().filter(Prefix = sents_folder)):
        if i % 1000 == 0:
            print(i)
        
        if not obj.key.endswith("/"):
            fileName = obj.key.split("/")[-1].replace("_version", "")
            new_name = dest_bucket_name + fileName
            copySource = bucket_name + '/' + obj.key
            try: 
                s3.Object(bucket_name, new_name).copy_from(CopySource=copySource)
                # s3.Object(bucket_name, fileName).delete()
            except Exception as e:
                print(f"Error while renaming {fileName} to {new_name}.")
                print(e)

## TODO: Move this function somewhere else?
def format_sents_for_output(sents, doc_id):
    return {f"{doc_id}_sent_{i}": {"text": sent, "label": []} for i, sent in enumerate(sents)}