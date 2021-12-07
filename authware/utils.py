from aiohttp.client_reqrep import ClientResponse
from authware.hwid import HardwareId
from authware.storage import AuthStorage
from authware.exceptions import UpdateRequiredException, ValidationException, AuthException

class Authware:
    wrapper_ver = "1.0.0.0"
    
    app_id = None    
    version = None
    
    hwid = HardwareId()
    storage = AuthStorage()
    
    headers = {}
    base_url = "https://982c-2a02-c7f-76e2-7a00-58da-1abc-de5a-f3ae.ngrok.io"
    
    
    def __init__(self, headers, version, app_id):
        self.app_id = app_id
        self.headers = headers
        self.version = version
        self.headers = {
            "X-Authware-Hardware-ID": self.hwid.get_id(),
            "X-Authware-App-Version": version,
            "User-Agent": f"AuthwarePython/{self.wrapper.wrapper_ver}",
            "Authorization": f"Bearer {self.storage.read_auth_token()}"
        }
        
    @staticmethod
    async def check_response(resp: ClientResponse):
        response_json = await resp.json()
        
        if (resp.status == 426):
            raise UpdateRequiredException(response_json["message"])
        elif (resp.status == 400):
            raise ValidationException(response_json["message"])
        elif (resp.status != 200):
            raise AuthException(response_json['message'])
        
        return response_json