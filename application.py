import aiohttp
import json

from authware.hwid import HardwareId
from authware.user import User
from authware.utils import Authware
from authware.storage import AuthStorage

class Application:
    version = None
    
    hwid = HardwareId()
    storage = AuthStorage()
    
    def __init__(self, app_id: str, version: str):
        Authware.app_id = app_id
        Authware.headers = {
            "X-Authware-Hardware-ID": self.hwid.get_id(),
            "X-Authware-App-Version": version,
            "User-Agent": f"AuthwarePython/{Authware.wrapper_ver}",
            "Authorization": f"Bearer {self.storage.read_auth_token()}"
        }
        Authware.version = version
        
    async def authenticate(self, username: str, password: str) -> dict:
        auth_storage = self.storage.read_auth_token()
        if auth_storage is not None:
            return { 'token': auth_storage }
        
        auth_payload = {
            "app_id": self.app_id,
            "username": username,
            "password": password
        }
        
        auth_response = None
        
        # There has got to be a better way of doing this
        async with aiohttp.ClientSession(base_url=Authware.base_url, headers=Authware.headers) as session:
            async with session.post("/user/auth", json=auth_payload) as resp:
                auth_response = await Authware.check_response(resp)
                
        self.auth_token = auth_response["auth_token"]   
        self.storage.save_auth_token(self.auth_token)
        
        return auth_response
    
    async def create_user(self, username: str, email: str, password: str, token: str) -> dict:
        create_payload = {
            "app_id": Authware.app_id,
            "username": username,
            "email_address": email,
            "password": password,
            "token": token
        }
        
        create_response = None
        
        async with aiohttp.ClientSession(base_url=Authware.base_url, headers=Authware.headers) as session:
            async with session.post("/user/register", json=create_payload) as resp:
                create_response = await Authware.check_response(resp)
                
        return create_response
        
    
    async def get_variables(self) -> dict:
        variable_payload = {
            "app_id": Authware.app_id
        }
        
        variable_response = None
        
        async with aiohttp.ClientSession(base_url=Authware.base_url, headers=Authware.headers) as session:
            if Authware.storage.read_auth_token() is not None:
                async with session.get("/user/variables") as resp:
                    variable_response = await Authware.check_response(resp)
            else:
                async with session.post("/user/variables", json=variable_payload) as resp:
                    variable_response = await Authware.check_response(resp)
                
        return variable_response
        
            
    async def get_user(self) -> User:
        profile_response = None
        
        async with aiohttp.ClientSession(base_url=Authware.base_url, headers=Authware.headers) as session:
            async with session.get("/user/profile") as resp:
                profile_response = await Authware.check_response(resp)
                
        return User.from_dict(profile_response)
        
        
