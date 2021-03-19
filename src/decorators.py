import boto3
import json

# Whenever you have your key and your secret credentials in a json file of the form {<"key"> : <"secret">} you can use it as decorator for the connection function
def load_key_secret(path, filename, credentials):
    def decorator(func):
        def inner(*args):
            file = path + filename
            with open(file, 'r') as dict:
                key_dict = json.load(dict)
            key = list(key_dict.keys())[0]
            secret = list(key_dict.values())[0]
            if credentials == "key":
                return func(key, *args)
            elif credentials == "secret":
                return func(secret, *args)
            elif credentials == "both":
                return func(key,secret, *args)
        return inner
    return decorator

# This has the @load_key_secret embedded so you can directly use it for connecting to a S3 resource
def connect_to_S3_resource(path, filename, region):
    def decorator(func):
        def inner(*args):
            @load_key_secret(path, filename, "both")
            def get_S3_resource(key, secret, region):
                s3 = boto3.resource(
                    service_name = 's3',
                    region_name = region,
                    aws_access_key_id = key,
                    aws_secret_access_key = secret
                )
                return func(s3, *args)
            return get_S3_resource(region)
        return inner
    return decorator