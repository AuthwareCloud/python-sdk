import aiohttp
import requests

from uuid import UUID
from .hwid import HardwareId
from .user import User
from .utils import Authware


def from_str(x):
    assert isinstance(x, str)
    return x


def to_class(c, x):
    assert isinstance(x, c)
    return x.to_dict()


class Application:
    """The application class and it's functions, including variables, user authentication and registration.

     Fields
    -----------
    id -> uuid -> the current ID of your application
    name -> string -> the name of your application
    date_created -> datetime -> the date and time your application was created
    version -> string -> the current application version, set at the app creation"""
    is_init = False

    def __init__(self, app_id: str, version: str, hwid: HardwareId = HardwareId()):
        """Initializes the application with the provided arguments

        Arguments
        -----------
        id -> uuid -> the current ID of your application version -> string -> the current
        application version, set at the app creation hwid -< HardwareId (optional) -> the hardware ID fetching class,
        this is used to grab the hardware ID of the current device and set it to a user

        Hardware IDs
        -----------
        This package defaults to use a Windows-only hardware ID implementation which uses
        WMI, this means it will NOT work on Linux, macOS, etc. If you wish to support other platforms, you can just
        pass in a HardwareId to just disable the feature entirely, or you can build your own class to fetch a
        hardware ID, just simply inherit the HardwareId class and code away!
        """

        self.id = app_id
        self.version = version
        self.hwid = hwid

        Authware.app_id = app_id
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

    async def authenticate_async(self, username: str, password: str) -> dict:
        auth_payload = {
            "app_id": self.id,
            "username": username,
            "password": password
        }

        # There has got to be a better way of doing this
        async with aiohttp.ClientSession(base_url=Authware.base_url, headers=Authware.headers) as session:
            async with session.post("/user/auth", json=auth_payload) as resp:
                auth_response = await Authware.check_response(resp)

        Authware.auth_token = auth_response["auth_token"]
        Authware.regenerate_headers()

        return auth_response

    def authenticate(self, username: str, password: str) -> dict:
        auth_payload = {
            "app_id": self.id,
            "username": username,
            "password": password
        }

        req = requests.post(Authware.base_url + "/user/auth", json=auth_payload, headers=Authware.headers)

        auth_response = Authware.check_response_sync(req)

        Authware.auth_token = auth_response["auth_token"]
        Authware.regenerate_headers()

        return auth_response

    async def redeem_token_async(self, username: str, token: str) -> dict:
        redeem_payload = {
            "app_id": self.id,
            "username": username,
            "token": token
        }

        async with aiohttp.ClientSession(base_url=Authware.base_url, headers=Authware.headers) as session:
            async with session.post("/user/renew", json=redeem_payload) as resp:
                redeem_response = await Authware.check_response(resp)

        return redeem_response

    def redeem_token(self, username: str, token: str) -> dict:
        redeem_payload = {
            "app_id": self.id,
            "username": username,
            "token": token
        }

        req = requests.post(Authware.base_url + "/user/renew", json=redeem_payload, headers=Authware.headers)
        redeem_response = Authware.check_response_sync(req)

        return redeem_response

    async def create_user_async(self, username: str, email: str, password: str, token: str) -> dict:
        create_payload = {
            "app_id": self.id,
            "username": username,
            "email_address": email,
            "password": password,
            "token": token
        }

        async with aiohttp.ClientSession(base_url=Authware.base_url, headers=Authware.headers) as session:
            async with session.post("/user/register", json=create_payload) as resp:
                create_response = await Authware.check_response(resp)

        return create_response

    def create_user(self, username: str, email: str, password: str, token: str) -> dict:
        create_payload = {
            "app_id": self.id,
            "username": username,
            "email_address": email,
            "password": password,
            "token": token
        }

        req = requests.post(Authware.base_url + "/user/register", json=create_payload, headers=Authware.headers)
        create_response = Authware.check_response_sync(req)

        return create_response

    async def get_variables_async(self) -> dict:
        variable_payload = {
            "app_id": self.id
        }

        async with aiohttp.ClientSession(base_url=Authware.base_url, headers=Authware.headers) as session:
            if Authware.auth_token is not None:
                async with session.get("/user/variables") as resp:
                    variable_response = await Authware.check_response(resp)
            else:
                async with session.post("/user/variables", json=variable_payload) as resp:
                    variable_response = await Authware.check_response(resp)

        return variable_response

    def get_variables(self) -> dict:
        variable_payload = {
            "app_id": self.id
        }

        if Authware.auth_token is not None:
            req = requests.get(Authware.base_url + "/app/variables", headers=Authware.headers)
        else:
            req = requests.post(Authware.base_url + "/app/variables", json=variable_payload, headers=Authware.headers)

        variable_response = Authware.check_response_sync(req)

        return variable_response

    async def get_user_async(self) -> User:
        async with aiohttp.ClientSession(base_url=Authware.base_url, headers=Authware.headers) as session:
            async with session.get("/user/profile") as resp:
                profile_response = await Authware.check_response(resp)

        return User.from_dict(profile_response)

    def get_user(self) -> User:
        req = requests.get(Authware.base_url + "/user/profile", headers=Authware.headers)
        profile_response = Authware.check_response_sync(req)

        return User.from_dict(profile_response)

    @staticmethod
    def __from_dict(obj):
        assert isinstance(obj, dict)
        name = from_str(obj.get("name"))
        id = UUID(obj.get("id"))
        version = from_str(obj.get("version"))
        date_created = from_str(obj.get("date_created"))
        return Application(name, id, version, date_created)

    def __to_dict(self):
        result = {"name": from_str(self.name), "id": str(self.id), "version": from_str(self.version),
                  "date_created": from_str(self.date_created)}
        return result


def __application_from_dict(s):
    return Application.from_dict(s)


def __application_to_dict(x):
    return __to_class(Application, x)
