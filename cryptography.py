from hashlib import sha256

class Cryptography:
    def hash_sha256(self, data:str):
        return sha256(data.encode('utf-8')).hexdigest()