from json import JSONDecodeError

from aiohttp import ClientResponse
from requests.models import Response

from .exceptions import RatelimitedException, UpdateRequiredException, ValidationException, AuthException
from .hwid import HardwareId


def raise_exception(status_code: int):
    if status_code == 429:
        raise RatelimitedException("You're being ratelimited, try again in a minute")
    elif status_code == 426:
        raise UpdateRequiredException("An update is required for the application")
    elif status_code == 400:
        raise ValidationException("A bad request was returned, check the data you've submitted")
    elif status_code == 403:
        raise AuthException("You're being blocked by the API firewall, please contact Authware support")
    elif status_code != 200:
        raise AuthException("An unhandled response was returned by the Authware API that could not be "
                            "decoded, try updating the SDK and trying again")


class Authware:
    wrapper_ver = "2.0.0"

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

        if resp.status == 426:
            raise UpdateRequiredException(response_json["message"])
        elif resp.status == 400:
            raise ValidationException(response_json["message"])
        elif resp.status != 200:
            raise AuthException(response_json['message'])

        return response_json

    @staticmethod
    def check_response_sync(resp: Response) -> dict:
        try:
            response_json = resp.json()

            if resp.status_code == 429:
                raise RatelimitedException(response_json["message"])
            elif resp.status_code == 426:
                raise UpdateRequiredException(response_json["message"])
            elif resp.status_code == 400:
                raise ValidationException(response_json["message"])
            elif resp.status_code != 200:
                raise AuthException(response_json['message'])

            return response_json
        except JSONDecodeError:
            raise_exception(resp.status_code)
