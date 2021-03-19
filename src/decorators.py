def load_key_secret(func):
    def inner(*args, **kwargs):
        file = path + filename
        with open(file, 'r') as dict:
            key_dict = json.load(dict)
        return func(key_dict.keys())[0], list(key_dict.values())[0])
    return inner