import asyncio

from aiohttp.client_reqrep import ClientResponse
from requests.models import Response
from authware.hwid import HardwareId
from authware.exceptions import UpdateRequiredException, ValidationException, AuthException


class Authware:
    wrapper_ver = "1.0.3"

    app_id = None
    version = None

    auth_token = None

    hwid = HardwareId()

    headers = {}
    base_url = "https://api.authware.org"

    def __init__(self, headers, version, app_id):
        self.app_id = app_id
        self.headers = headers
        self.version = version
        self.regenerate_headers()

    @staticmethod
    def regenerate_headers():
        Authware.headers = {
            "X-Authware-Hardware-ID": Authware.hwid.get_id(),
            "X-Authware-App-Version": Authware.version,
            "User-Agent": f"AuthwarePython/{Authware.wrapper_ver}",
            "Authorization": f"Bearer {Authware.auth_token}"
        }

    @staticmethod
    async def check_response(resp: ClientResponse) -> dict:
        response_json = await resp.json()

        if (resp.status == 426):
            raise UpdateRequiredException(response_json["message"])
        elif (resp.status == 400):
            raise ValidationException(response_json["message"])
        elif (resp.status != 200):
            raise AuthException(response_json['message'])

        return response_json

    @staticmethod
    def check_response_sync(resp: Response) -> dict:
        response_json = resp.json()

        if (resp.status_code == 426):
            raise UpdateRequiredException(response_json["message"])
        elif (resp.status_code == 400):
            raise ValidationException(response_json["message"])
        elif (resp.status_code != 200):
            raise AuthException(response_json['message'])

        return response_json

    def once(func):
        future = None

        async def once_wrapper(*args, **kwargs):
            nonlocal future
            if not future:
                future = asyncio.create_task(func(*args, **kwargs))
            return await future
        return once_wrapper
