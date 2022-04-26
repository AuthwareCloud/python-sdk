import re
import requests

from uuid import UUID
from authware.hwid import HardwareId
from authware.user import User
from authware.utils import Authware


def __from_str(x):
    assert isinstance(x, str)
    return x


def __to_class(c, x):
    assert isinstance(x, c)
    return x.to_dict()


class Application:
    hwid = HardwareId()
    is_init = False

    def __init__(self, id: str, version: str):
        self.id = id
        self.version = version

        Authware.app_id = id
        Authware.version = version
        Authware.headers = {
            "X-Authware-Hardware-ID": self.hwid.get_id(),
            "X-Authware-App-Version": version,
            "User-Agent": f"AuthwarePython/{Authware.wrapper_ver}",
            "Authorization": f"Bearer {Authware.auth_token}"
        }

        app = self.__fetch_app()

        self.name = app["name"]
        self.date_created = app["date_created"]

    def __fetch_app(self) -> dict:
        fetch_payload = {
            "app_id": self.id
        }

        # There has got to be a better way of doing this
        req = requests.post(Authware.base_url + "/app",
                            json=fetch_payload, headers=Authware.headers)
        return Authware.check_response_sync(req)

    def authenticate(self, username: str, password: str) -> dict:
        auth_payload = {
            "app_id": self.id,
            "username": username,
            "password": password
        }

        auth_response = None

        
        req = requests.post(Authware.base_url + "/user/auth", json=auth_payload, headers=Authware.headers)

        auth_response = Authware.check_response_sync(req)

        Authware.auth_token = auth_response["auth_token"]
        Authware.regenerate_headers()

        return auth_response

    def redeem_token(self, username: str, token: str) -> dict:
        redeem_payload = {
            "app_id": self.id,
            "username": username,
            "token": token
        }

        redeem_response = None

        req = requests.post(Authware.base_url + "/user/renew", json=redeem_payload, headers=Authware.headers)
        redeem_response = Authware.check_response_sync(req)

        return redeem_response

    def create_user(self, username: str, email: str, password: str, token: str) -> dict:
        create_payload = {
            "app_id": self.id,
            "username": username,
            "email_address": email,
            "password": password,
            "token": token
        }

        create_response = None

        req = requests.post(Authware.base_url + "/user/register", json=create_payload, headers=Authware.headers)
        create_response = Authware.check_response_sync(req)

        return create_response

    def get_variables(self) -> dict:
        variable_payload = {
            "app_id": self.id
        }

        variable_response = None
        req = None

        if Authware.auth_token is not None:
            req = requests.get(Authware.base_url + "/app/variables", headers=Authware.headers)
        else:
            req = requests.post(Authware.base_url + "/app/variables", json=variable_payload, headers=Authware.headers)

        variable_response = Authware.check_response_sync(req)

        return variable_response

    def get_user(self) -> User:
        profile_response = None

        req = requests.get(Authware.base_url + "/user/profile", headers=Authware.headers)
        profile_response = Authware.check_response_sync(req)

        return User.from_dict(profile_response)

    @staticmethod
    def __from_dict(obj):
        assert isinstance(obj, dict)
        name = __from_str(obj.get("name"))
        id = UUID(obj.get("id"))
        version = __from_str(obj.get("version"))
        date_created = __from_str(obj.get("date_created"))
        return Application(name, id, version, date_created)

    def __to_dict(self):
        result = {}
        result["name"] = __from_str(self.name)
        result["id"] = str(self.id)
        result["version"] = __from_str(self.version)
        result["date_created"] = __from_str(self.date_created)
        return result


def __application_from_dict(s):
    return Application.from_dict(s)


def __application_to_dict(x):
    return __to_class(Application, x)
