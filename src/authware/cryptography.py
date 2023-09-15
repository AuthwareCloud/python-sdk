from hashlib import sha256


def hash_sha256(data: str):
    return sha256(data.encode('utf-8')).hexdigest()
