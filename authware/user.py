import dateutil.parser
import aiohttp

from uuid import UUID
from authware.utils import Authware


def from_str(x):
    assert isinstance(x, str)
    return x


def from_datetime(x):
    return dateutil.parser.parse(x)


def from_bool(x):
    assert isinstance(x, bool)
    return x


def from_list(f, x):
    assert isinstance(x, list)
    return [f(y) for y in x]


def to_class(c, x):
    assert isinstance(x, c)
    return x.to_dict()


def from_int(x):
    assert isinstance(x, int) and not isinstance(x, bool)
    return x


class Variable:
    def __init__(self, id, key, value, date_created, require_authentication):
        self.id = id
        self.key = key
        self.value = value
        self.date_created = date_created
        self.require_authentication = require_authentication

    @staticmethod
    def from_dict(obj):
        assert isinstance(obj, dict)
        id = UUID(obj.get("id"))
        key = from_str(obj.get("key"))
        value = int(from_str(obj.get("value")))
        date_created = from_datetime(obj.get("date_created"))
        require_authentication = from_bool(obj.get("require_authentication"))
        return Variable(id, key, value, date_created, require_authentication)

    def to_dict(self):
        result = {}
        result["id"] = str(self.id)
        result["key"] = from_str(self.key)
        result["value"] = from_str(str(self.value))
        result["date_created"] = self.date_created.isoformat()
        result["require_authentication"] = from_bool(self.require_authentication)
        return result


class Role:
    def __init__(self, id, name, variables):
        self.id = id
        self.name = name
        self.variables = variables

    @staticmethod
    def from_dict(obj):
        assert isinstance(obj, dict)
        id = UUID(obj.get("id"))
        name = from_str(obj.get("name"))
        variables = from_list(Variable.from_dict, obj.get("variables"))
        return Role(id, name, variables)

    def to_dict(self):
        result = {}
        result["id"] = str(self.id)
        result["name"] = from_str(self.name)
        result["variables"] = from_list(lambda x: to_class(Variable, x), self.variables)
        return result


class Session:
    def __init__(self, id, date_created):
        self.id = id
        self.date_created = date_created

    @staticmethod
    def from_dict(obj):
        assert isinstance(obj, dict)
        id = UUID(obj.get("id"))
        date_created = from_datetime(obj.get("date_created"))
        return Session(id, date_created)

    def to_dict(self):
        result = {}
        result["id"] = str(self.id)
        result["date_created"] = self.date_created.isoformat()
        return result


class User:
    def __init__(self, roles, username, id, email, date_created, plan_expire, is_two_factor_enabled, sessions, code):
        self.roles = roles
        self.username = username
        self.id = id
        self.email = email
        self.date_created = date_created
        self.plan_expire = plan_expire
        self.is_two_factor_enabled = is_two_factor_enabled
        self.sessions = sessions
        self.code = code

    @staticmethod
    def from_dict(obj):
        assert isinstance(obj, dict)
        roles = from_list(Role.from_dict, obj.get("roles"))
        username = from_str(obj.get("username"))
        id = UUID(obj.get("id"))
        email = from_str(obj.get("email"))
        date_created = from_datetime(obj.get("date_created"))
        plan_expire = from_datetime(obj.get("plan_expire"))
        is_two_factor_enabled = from_bool(obj.get("is_two_factor_enabled"))
        sessions = from_list(Session.from_dict, obj.get("sessions"))
        code = from_int(obj.get("code"))
        return User(roles, username, id, email, date_created, plan_expire, is_two_factor_enabled, sessions, code)

    def to_dict(self):
        result = {}
        result["roles"] = from_list(lambda x: to_class(Role, x), self.roles)
        result["username"] = from_str(self.username)
        result["id"] = str(self.id)
        result["email"] = from_str(self.email)
        result["date_created"] = self.date_created.isoformat()
        result["plan_expire"] = self.plan_expire.isoformat()
        result["is_two_factor_enabled"] = from_bool(self.is_two_factor_enabled)
        result["sessions"] = from_list(lambda x: to_class(Session, x), self.sessions)
        result["code"] = from_int(self.code)
        return result
    
    async def change_email(self, new_email: str, password: str) -> dict:
        change_payload = {
            "new_email_address": new_email,
            "password": password
        }
        
        change_response = None
        
        async with aiohttp.ClientSession(base_url=Authware.base_url, headers=Authware.headers) as session:
            async with session.put("/user/change-email", json=change_payload) as resp:
                change_response = await Authware.check_response(resp)
                
        return change_response
    
    async def change_password(self, old_password: str, new_password: str, repeat_password: str) -> dict:
        change_payload = {
            "old_password": old_password,
            "password": new_password,
            "repeat_password": repeat_password
        }
        
        change_response = None
        
        async with aiohttp.ClientSession(base_url=Authware.base_url, headers=Authware.headers) as session:
            async with session.put("/user/change-password", json=change_payload) as resp:
                change_response = await Authware.check_response(resp)
                
        return change_response
    
    async def execute_api(self, api_id: str, params: dict) -> dict:
        execute_payload = {
            "api_id": api_id,
            "parameters": params
        }
        
        async with aiohttp.ClientSession(base_url=Authware.base_url, headers=Authware.headers) as session:
            async with session.post("/api/execute", json=execute_payload) as resp:
                change_response = await Authware.check_response(resp)
                
        return change_response
        

def user_from_dict(s):
    return User.from_dict(s)


def user_to_dict(x):
    return to_class(User, x)