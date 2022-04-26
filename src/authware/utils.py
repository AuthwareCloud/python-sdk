from json import JSONDecodeError
from requests.models import Response
from authware.hwid import HardwareId
from authware.exceptions import RatelimitedException, UpdateRequiredException, ValidationException, AuthException


class Authware:
    wrapper_ver = "1.0.0"

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
        except JSONDecodeError:
            if resp.status_code == 429:
                raise RatelimitedException("You're being ratelimited, try again in a minute")
            elif resp.status_code == 426:
                raise UpdateRequiredException("An update is required for the application")
            elif resp.status_code == 400:
                raise ValidationException("A bad request was returned, check the data you've submitted")
            elif resp.status_code == 403:
                raise AuthException("You're being blocked by the API firewall, please contact Authware support")
            elif resp.status_code != 200:
                raise AuthException("An unhandled response was returned by the Authware API that could not be decoded, try updating the SDK and trying again")

    
        return response_json

