import json

from pathlib import Path

class AuthStorage:
    def save_auth_token(self, token):
        format = {
            'token': token
        }
        
        file_contents = json.dumps(format)
        
        with open(Path.joinpath(Path.home(), "authware"), "w") as file:
            file.write(file_contents)
        
    def read_auth_token(self):
        if not Path.is_file(Path.joinpath(Path.home(), "authware")):
            return None
        
        with open(Path.joinpath(Path.home(), "authware")) as file:
            dict = json.load(file)
            return dict["token"]
        
        